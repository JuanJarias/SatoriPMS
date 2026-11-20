"""Router de persistencia de sesiones conversacionales de WhatsApp/n8n en PostgreSQL 16 (Lote M3)."""

from datetime import datetime, timedelta, timezone
import json
import sys
from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from dependencies.auth import require_role, require_service_key, require_service_or_role, resolve_actor_name
    from models.conversation import Conversation
    from models.user import User, UserRole
    from services.audit_service import record_audit
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.dependencies.auth import require_role, require_service_key, require_service_or_role, resolve_actor_name
    from apps.api.models.conversation import Conversation
    from apps.api.models.user import User, UserRole
    from apps.api.services.audit_service import record_audit

router = APIRouter(tags=["Conversations & Sessions"])


class SessionUpsertRequest(BaseModel):
    """Payload para guardar sesión de chat o link de pago Wompi en PostgreSQL."""

    value: str | dict[str, Any] | None = None
    session: dict[str, Any] | None = None
    ttl: int | None = 660


class AgentEscalationRequest(BaseModel):
    """Payload enviado por n8n cuando el huésped solicita hablar con un agente humano."""

    wa_id: str
    name: str | None = "Huésped WhatsApp"
    context: str | None = "Solicitud de agente desde WhatsApp"


def _normalize_session_key(raw_key: str) -> tuple[str, str | None]:
    """Normaliza la llave de sesión y extrae el wa_id si corresponde a una sesión de usuario."""
    key = raw_key.strip()
    if key.startswith("session:"):
        return key, key.split("session:", 1)[1]
    if key.startswith("wompi:link:"):
        return key, None
    return f"session:{key}", key


@router.get(
    "/api/v1/conversations/session/{key:path}",
    status_code=status.HTTP_200_OK,
)
async def get_conversation_session(
    key: str,
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Recupera el estado conversacional o link de pago desde PostgreSQL (reemplazo 1:1 de Redis GET)."""
    session_key, wa_id = _normalize_session_key(key)
    res = await db.execute(
        select(Conversation).where(Conversation.session_key == session_key)
    )
    conv = res.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if conv is None or (conv.expires_at is not None and conv.expires_at <= now):
        return {"key": session_key, "wa_id": wa_id, "value": None, "session": {}}

    parsed: dict[str, Any] = {}
    if conv.session_data:
        try:
            loaded = json.loads(conv.session_data)
            if isinstance(loaded, dict):
                parsed = loaded
        except json.JSONDecodeError:
            parsed = {}

    return {
        "key": session_key,
        "wa_id": conv.wa_id or wa_id,
        "value": conv.session_data,
        "session": parsed,
    }


@router.put(
    "/api/v1/conversations/session/{key:path}",
    status_code=status.HTTP_200_OK,
)
@router.post(
    "/api/v1/conversations/session/{key:path}",
    status_code=status.HTTP_200_OK,
)
async def upsert_conversation_session(
    key: str,
    payload: SessionUpsertRequest,
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Guarda o actualiza el contexto conversacional en PostgreSQL 16 (reemplazo 1:1 de Redis SET)."""
    session_key, wa_id = _normalize_session_key(key)

    raw_val = payload.value if payload.value is not None else payload.session
    parsed_dict: dict[str, Any] = {}
    if isinstance(raw_val, dict):
        parsed_dict = raw_val
        serialized = json.dumps(raw_val, ensure_ascii=False)
    elif isinstance(raw_val, str):
        serialized = raw_val
        try:
            loaded = json.loads(raw_val)
            if isinstance(loaded, dict):
                parsed_dict = loaded
        except json.JSONDecodeError:
            parsed_dict = {}
    else:
        serialized = "{}"

    resolved_wa_id = str(parsed_dict.get("wa_id") or wa_id or "") or None
    sender_name = str(parsed_dict.get("sender_name") or "") or None
    state = str(parsed_dict.get("state") or "menu")
    step = str(parsed_dict.get("step") or "inicio")
    agent_active = bool(parsed_dict.get("agent_active", False))

    expires_at: datetime | None = None
    if payload.ttl and payload.ttl > 0:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=payload.ttl)

    stmt = (
        pg_insert(Conversation)
        .values(
            session_key=session_key,
            wa_id=resolved_wa_id,
            sender_name=sender_name,
            state=state,
            step=step,
            agent_active=agent_active,
            session_data=serialized,
            expires_at=expires_at,
        )
        .on_conflict_do_update(
            index_elements=[Conversation.session_key],
            set_={
                "wa_id": resolved_wa_id,
                "sender_name": sender_name,
                "state": state,
                "step": step,
                "agent_active": agent_active,
                "session_data": serialized,
                "expires_at": expires_at,
            },
        )
    )
    await db.execute(stmt)
    await db.commit()

    return {
        "key": session_key,
        "wa_id": resolved_wa_id,
        "value": serialized,
        "status": "saved",
    }


@router.delete(
    "/api/v1/conversations/session/{key:path}",
    status_code=status.HTTP_200_OK,
)
async def delete_conversation_session(
    key: str,
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Elimina una sesión conversacional inactiva en PostgreSQL 16 (reemplazo 1:1 de Redis DEL)."""
    session_key, _ = _normalize_session_key(key)
    await db.execute(
        delete(Conversation).where(Conversation.session_key == session_key)
    )
    await db.commit()
    return {"key": session_key, "deleted": True}


@router.post(
    "/api/notifications/agent-request",
    status_code=status.HTTP_200_OK,
)
@router.post(
    "/api/v1/notifications/agent-request",
    status_code=status.HTTP_200_OK,
)
async def request_human_agent(
    payload: AgentEscalationRequest,
    _service: str = Depends(require_service_key),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Escala una conversación de WhatsApp a un recepcionista humano y registra auditoría."""
    session_key = f"session:{payload.wa_id}"
    session_obj = {
        "state": "escalamiento",
        "step": "atencion_humana",
        "agent_active": True,
        "wa_id": payload.wa_id,
        "sender_name": payload.name,
    }
    stmt = (
        pg_insert(Conversation)
        .values(
            session_key=session_key,
            wa_id=payload.wa_id,
            sender_name=payload.name,
            state="escalamiento",
            step="atencion_humana",
            agent_active=True,
            session_data=json.dumps(session_obj, ensure_ascii=False),
        )
        .on_conflict_do_update(
            index_elements=[Conversation.session_key],
            set_={
                "sender_name": payload.name,
                "state": "escalamiento",
                "step": "atencion_humana",
                "agent_active": True,
            },
        )
    )
    await db.execute(stmt)
    await record_audit(
        db=db,
        actor=payload.wa_id,
        action="AGENT_ESCALATION_REQUESTED",
        entity="conversation",
        entity_id=payload.wa_id,
        details={"name": payload.name, "context": payload.context},
    )
    await db.commit()
    return {
        "status": "ok",
        "agent_available": True,
        "wa_id": payload.wa_id,
    }


@router.get("/api/conversations", status_code=status.HTTP_200_OK)
@router.get("/api/v1/conversations", status_code=status.HTTP_200_OK)
async def list_conversations(
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Lista las conversaciones de WhatsApp para la bandeja de entrada de recepción."""
    res = await db.execute(
        select(Conversation)
        .where(Conversation.wa_id.is_not(None))
        .order_by(Conversation.updated_at.desc())
    )
    rows = res.scalars().all()
    return [
        {
            "id": r.id,
            "waId": r.wa_id,
            "guestName": r.sender_name or "Huésped WhatsApp",
            "guestPhone": r.wa_id,
            "status": "escalated" if r.agent_active else "active",
            "step": r.step,
            "state": r.state,
            "agentActive": r.agent_active,
            "updatedAt": r.updated_at.isoformat() if r.updated_at else None,
        }
        for r in rows
    ]


@router.post(
    "/api/conversations/{conversation_id}/escalation",
    status_code=status.HTTP_200_OK,
)
@router.post(
    "/api/v1/conversations/{conversation_id}/escalation",
    status_code=status.HTTP_200_OK,
)
async def escalate_conversation_by_id(
    conversation_id: int,
    current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Activa o confirma escalamiento a humano por ID de conversación."""
    conv = await db.get(Conversation, conversation_id)
    if conv is not None:
        conv.agent_active = True
        conv.state = "escalamiento"
        await record_audit(
            db=db,
            actor=resolve_actor_name(current_user),
            action="CONVERSATION_ESCALATED",
            entity="conversation",
            entity_id=conversation_id,
            details={"wa_id": conv.wa_id},
        )
        await db.commit()
    return {"status": "escalated", "id": conversation_id}


sys.modules.setdefault("routers.conversations", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.conversations", sys.modules[__name__])
