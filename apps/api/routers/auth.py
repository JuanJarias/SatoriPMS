"""Router de autenticación JWT, perfil de sesión y consulta de auditoría RBAC (Lote M1)."""

import sys

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from core.security import create_access_token, verify_password
    from dependencies.auth import require_role
    from models.audit_log import AuditLog
    from models.user import User, UserRole
    from services.audit_service import record_audit
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.core.security import create_access_token, verify_password
    from apps.api.dependencies.auth import require_role
    from apps.api.models.audit_log import AuditLog
    from apps.api.models.user import User, UserRole
    from apps.api.services.audit_service import record_audit

router = APIRouter(prefix="/api/v1/auth", tags=["Auth & RBAC"])


class LoginRequest(BaseModel):
    """Credenciales de inicio de sesión para personal del hotel."""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """Respuesta con token JWT firmado y metadatos básicos del rol."""

    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    name: str


class UserProfileResponse(BaseModel):
    """Perfil del usuario autenticado."""

    id: int
    username: str
    role: str
    name: str
    active: bool


class AuditLogResponse(BaseModel):
    """Entrada inmutable de auditoría (solo visible para Administrador)."""

    id: int
    actor_username: str
    action: str
    entity: str
    entity_id: str | None = None
    details_json: str | None = None


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Autentica al usuario contra PostgreSQL, registra auditoría inmutable y emite un JWT."""
    result = await db.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()

    if (
        user is None
        or not user.active
        or not verify_password(credentials.password, user.password_hash)
    ):
        await record_audit(
            db=db,
            actor=credentials.username,
            action="LOGIN_FAILED",
            entity="system_users",
            entity_id=str(user.id) if user is not None else None,
            details={"reason": "invalid_credentials"},
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
            "user_id": user.id,
        }
    )

    await record_audit(
        db=db,
        actor=user.username,
        action="LOGIN_SUCCESS",
        entity="system_users",
        entity_id=user.id,
        details={"role": user.role},
    )
    await db.commit()

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        username=user.username,
        role=user.role,
        name=user.name,
    )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
)
async def read_current_user(
    current_user: User = Depends(
        require_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
) -> UserProfileResponse:
    """Retorna el perfil del usuario autenticado (Administrador o Recepcionista)."""
    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        name=current_user.name,
        active=current_user.active,
    )


@router.get(
    "/audit-logs",
    response_model=list[AuditLogResponse],
    status_code=status.HTTP_200_OK,
)
async def list_audit_logs(
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> list[AuditLogResponse]:
    """Consulta la bitácora de auditoría inmutable (restringido exclusivamente a Administrador)."""
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.id.desc()).limit(50)
    )
    logs = result.scalars().all()
    return [
        AuditLogResponse(
            id=entry.id,
            actor_username=entry.actor_username,
            action=entry.action,
            entity=entry.entity,
            entity_id=entry.entity_id,
            details_json=entry.details_json,
        )
        for entry in logs
    ]


sys.modules.setdefault("routers.auth", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.auth", sys.modules[__name__])
