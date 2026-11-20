"""Router de autenticación JWT, perfil de sesión y consulta de auditoría RBAC (Lote M1)."""

import sys

from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from core.security import create_access_token, hash_password, verify_password
    from dependencies.auth import require_role
    from models.audit_log import AuditLog
    from models.user import User, UserRole
    from services.audit_service import record_audit
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.core.security import create_access_token, hash_password, verify_password
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
    timestamp: str | None = None
    actor_username: str
    action: str
    entity: str
    entity_id: str | None = None
    details_json: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=6, max_length=128)


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
            timestamp=entry.timestamp.isoformat() if entry.timestamp else None,
            actor_username=entry.actor_username,
            action=entry.action,
            entity=entry.entity,
            entity_id=entry.entity_id,
            details_json=entry.details_json,
        )
        for entry in logs
    ]


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_own_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Permite al usuario autenticado cambiar su contraseña en PostgreSQL."""
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta",
        )
    current_user.password_hash = hash_password(payload.new_password)
    await record_audit(
        db=db,
        actor=current_user.username,
        action="PASSWORD_CHANGED",
        entity="system_users",
        entity_id=current_user.id,
    )
    await db.commit()
    return {"updated": True, "message": "Contraseña actualizada exitosamente"}


@router.get("/users", status_code=status.HTTP_200_OK)
async def list_system_users(
    _current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Lista las cuentas de personal registradas (solo Administrador)."""
    res = await db.execute(select(User).order_by(User.id.asc()))
    return [
        {
            "id": u.id,
            "username": u.username,
            "name": u.name,
            "role": u.role,
            "active": u.active,
            "createdAt": u.created_at.isoformat() if u.created_at else None,
        }
        for u in res.scalars().all()
    ]


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_system_user(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Crea una nueva cuenta de Recepcionista o Administrador en PostgreSQL."""
    username = str(body.get("username") or "").strip().lower()
    name = str(body.get("name") or "").strip()
    password = str(body.get("password") or "").strip()
    role = str(body.get("role") or UserRole.RECEPCIONISTA.value).strip()
    if role not in (UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rol inválido")
    if not username or not name or len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username, name y password (>=6 caracteres) son obligatorios",
        )
    existing = await db.execute(select(User).where(User.username == username))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El usuario '{username}' ya existe",
        )
    new_user = User(
        username=username,
        password_hash=hash_password(password),
        role=role,
        name=name,
        active=True,
    )
    db.add(new_user)
    await db.flush()
    await record_audit(
        db=db,
        actor=current_user.username,
        action="USER_CREATED",
        entity="system_users",
        entity_id=new_user.id,
        details={"username": username, "role": role},
    )
    await db.commit()
    await db.refresh(new_user)
    return {
        "id": new_user.id,
        "username": new_user.username,
        "name": new_user.name,
        "role": new_user.role,
        "active": new_user.active,
    }


@router.patch("/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_system_user(
    user_id: int,
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Actualiza nombre, rol, estado activo o clave de un usuario (solo Administrador)."""
    target = await db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if "active" in body:
        next_active = bool(body["active"])
        if target.id == current_user.id and not next_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No puedes desactivar tu propia cuenta activa",
            )
        target.active = next_active
    if "name" in body and str(body["name"]).strip():
        target.name = str(body["name"]).strip()
    if "role" in body and str(body["role"]) in (
        UserRole.ADMINISTRADOR.value,
        UserRole.RECEPCIONISTA.value,
    ):
        target.role = str(body["role"])
    if "password" in body and str(body["password"]).strip():
        pwd = str(body["password"]).strip()
        if len(pwd) < 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña debe tener mínimo 6 caracteres")
        target.password_hash = hash_password(pwd)

    await record_audit(
        db=db,
        actor=current_user.username,
        action="USER_UPDATED",
        entity="system_users",
        entity_id=target.id,
        details={"username": target.username, "active": target.active, "role": target.role},
    )
    await db.commit()
    await db.refresh(target)
    return {
        "id": target.id,
        "username": target.username,
        "name": target.name,
        "role": target.role,
        "active": target.active,
    }


sys.modules.setdefault("routers.auth", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.auth", sys.modules[__name__])
