"""Router de persistencia de sesiones conversacionales de WhatsApp/n8n en PostgreSQL 16 (Lote M3)."""

from datetime import datetime, timedelta, timezone
import json
import sys
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
import httpx
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.config import settings
    from core.database import get_db
    from dependencies.auth import require_role, require_service_key, require_service_or_role, resolve_actor_name
    from models.conversation import Conversation
    from models.user import User, UserRole
    from services.audit_service import record_audit
    from services.event_bus import publish_pms_event
except ImportError:
    from apps.api.core.config import settings
    from apps.api.core.database import get_db
    from apps.api.dependencies.auth import require_role, require_service_key, require_service_or_role, resolve_actor_name
    from apps.api.models.conversation import Conversation
    from apps.api.models.user import User, UserRole
    from apps.api.services.audit_service import record_audit
    from apps.api.services.event_bus import publish_pms_event

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


class ToggleBotRequest(BaseModel):
    """Permite activar o pausar explícitamente el bot automático n8n en una sesión."""

    bot_active: bool | None = None


class ManualMessageRequest(BaseModel):
    """Mensaje manual enviado por recepción o gerencia al huésped en WhatsApp."""

    text: str = Field(..., min_length=1, max_length=2000)


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


def _parse_session_json(raw: str | None) -> dict[str, Any]:
    """Deserializa session_data de forma segura."""
    if not raw:
        return {}
    try:
        loaded = json.loads(raw)
        return loaded if isinstance(loaded, dict) else {}
    except json.JSONDecodeError:
        return {}


@router.get(
    "/api/v1/conversations/session-keys",
    status_code=status.HTTP_200_OK,
)
async def list_session_keys(
    prefix: str = Query(default="session:"),
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Lista llaves almacenadas en PostgreSQL por prefijo (ej. wompi:link: o session:)."""
    now = datetime.now(timezone.utc)
    res = await db.execute(
        select(Conversation)
        .where(Conversation.session_key.like(f"{prefix}%"))
        .order_by(Conversation.updated_at.desc())
    )
    rows = res.scalars().all()
    items: list[dict[str, Any]] = []
    for r in rows:
        if r.expires_at is not None and r.expires_at <= now:
            continue
        items.append(
            {
                "key": r.session_key,
                "waId": r.wa_id,
                "value": r.session_data,
                "session": _parse_session_json(r.session_data),
                "updatedAt": r.updated_at.isoformat() if r.updated_at else None,
            }
        )
    return items


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
        .where(
            Conversation.wa_id.is_not(None),
            Conversation.session_key.like("session:%"),
        )
        .order_by(Conversation.updated_at.desc())
    )
    rows = res.scalars().all()
    out: list[dict[str, Any]] = []
    for r in rows:
        parsed = _parse_session_json(r.session_data)
        out.append(
            {
                "id": r.id,
                "waId": r.wa_id,
                "guestName": r.sender_name or "Huésped WhatsApp",
                "guestPhone": r.wa_id,
                "status": "escalated" if r.agent_active else "active",
                "step": r.step,
                "state": r.state,
                "agentActive": r.agent_active,
                "messages": parsed.get("manual_messages", []),
                "updatedAt": r.updated_at.isoformat() if r.updated_at else None,
            }
        )
    return out


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
    """Activa escalamiento a humano por ID de conversación."""
    conv = await db.get(Conversation, conversation_id)
    if conv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada",
        )
    conv.agent_active = True
    conv.state = "escalamiento"
    session_obj = _parse_session_json(conv.session_data)
    session_obj["agent_active"] = True
    session_obj["state"] = "escalamiento"
    conv.session_data = json.dumps(session_obj, ensure_ascii=False)
    await record_audit(
        db=db,
        actor=resolve_actor_name(current_user),
        action="CONVERSATION_ESCALATED",
        entity="conversation",
        entity_id=conversation_id,
        details={"wa_id": conv.wa_id},
    )
    await db.commit()
    publish_pms_event("conversation.updated", {"id": conversation_id, "agentActive": True})
    return {"status": "escalated", "id": conversation_id, "agentActive": True}


@router.post(
    "/api/v1/conversations/{conversation_id}/toggle-bot",
    status_code=status.HTTP_200_OK,
)
async def toggle_conversation_bot(
    conversation_id: int,
    payload: ToggleBotRequest | None = None,
    current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Alterna entre atención humana (bot en silencio) y bot automático n8n."""
    conv = await db.get(Conversation, conversation_id)
    if conv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada",
        )
    if payload is not None and payload.bot_active is not None:
        new_agent_active = not payload.bot_active
    else:
        new_agent_active = not bool(conv.agent_active)

    conv.agent_active = new_agent_active
    conv.state = "escalamiento" if new_agent_active else "menu"
    if not new_agent_active:
        conv.step = "esperando_opcion"

    session_obj = _parse_session_json(conv.session_data)
    session_obj["agent_active"] = new_agent_active
    session_obj["state"] = conv.state
    if not new_agent_active:
        session_obj["step"] = "esperando_opcion"
    conv.session_data = json.dumps(session_obj, ensure_ascii=False)

    await record_audit(
        db=db,
        actor=resolve_actor_name(current_user),
        action="CONVERSATION_BOT_TOGGLED",
        entity="conversation",
        entity_id=conversation_id,
        details={"wa_id": conv.wa_id, "bot_active": not new_agent_active},
    )
    await db.commit()
    publish_pms_event(
        "conversation.updated",
        {"id": conversation_id, "agentActive": new_agent_active},
    )
    return {
        "id": conversation_id,
        "agentActive": new_agent_active,
        "botActive": not new_agent_active,
        "status": "escalated" if new_agent_active else "active",
    }


@router.post(
    "/api/v1/conversations/{conversation_id}/messages",
    status_code=status.HTTP_200_OK,
)
async def send_manual_whatsapp_message(
    conversation_id: int,
    payload: ManualMessageRequest,
    current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Envía/registra un mensaje manual desde recepción en la sesión del huésped."""
    conv = await db.get(Conversation, conversation_id)
    if conv is None or not conv.wa_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada",
        )

    text_clean = payload.text.strip()
    if not text_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El mensaje no puede estar vacío",
        )

    dispatched_whatsapp = False
    if settings.WHATSAPP_TOKEN.strip() and settings.WHATSAPP_PHONE_ID.strip():
        graph_ver = settings.WHATSAPP_GRAPH_VERSION.strip() or "v20.0"
        url = f"https://graph.facebook.com/{graph_ver}/{settings.WHATSAPP_PHONE_ID.strip()}/messages"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    url,
                    headers={"Authorization": f"Bearer {settings.WHATSAPP_TOKEN.strip()}"},
                    json={
                        "messaging_product": "whatsapp",
                        "to": conv.wa_id,
                        "type": "text",
                        "text": {"body": text_clean},
                    },
                )
                dispatched_whatsapp = 200 <= resp.status_code < 300
        except Exception:
            dispatched_whatsapp = False

    session_obj = _parse_session_json(conv.session_data)
    history = list(session_obj.get("manual_messages") or [])
    entry = {
        "from": "staff",
        "author": resolve_actor_name(current_user),
        "text": text_clean,
        "sentAt": datetime.now(timezone.utc).isoformat(),
        "dispatched": dispatched_whatsapp,
    }
    history.append(entry)
    session_obj["manual_messages"] = history[-50:]
    conv.session_data = json.dumps(session_obj, ensure_ascii=False)

    await record_audit(
        db=db,
        actor=resolve_actor_name(current_user),
        action="CONVERSATION_MANUAL_MESSAGE",
        entity="conversation",
        entity_id=conversation_id,
        details={"wa_id": conv.wa_id, "dispatched_whatsapp": dispatched_whatsapp},
    )
    await db.commit()
    publish_pms_event("conversation.message", {"id": conversation_id, "message": entry})
    return {
        "id": conversation_id,
        "waId": conv.wa_id,
        "dispatched": dispatched_whatsapp,
        "message": entry,
    }


sys.modules.setdefault("routers.conversations", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.conversations", sys.modules[__name__])
