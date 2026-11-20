"""Dependencias de autenticación JWT y control de acceso basado en roles (RBAC RN-10)."""

from collections.abc import Callable, Coroutine, Sequence
import hmac
import sys
from typing import Any

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.config import settings
    from core.database import get_db
    from core.security import JWTError, decode_access_token
    from models.user import User
except ImportError:
    from apps.api.core.config import settings
    from apps.api.core.database import get_db
    from apps.api.core.security import JWTError, decode_access_token
    from apps.api.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)

service_key_scheme = APIKeyHeader(
    name="X-Service-Key",
    auto_error=False,
)


def resolve_actor_name(principal: User | str | None, fallback: str = "system") -> str:
    """Extrae el nombre de actor auditable desde un usuario JWT o un servicio interno."""
    if isinstance(principal, User):
        return principal.username
    if isinstance(principal, str) and principal.strip():
        return principal.strip()
    return fallback


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Valida el JWT Bearer en la cabecera Authorization y recupera el usuario activo."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    try:
        payload = decode_access_token(token)
        username: str | None = payload.get("sub")
        token_role: str | None = payload.get("role")
        if not username or not token_role:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None or not user.active or user.role != token_role:
        raise credentials_exception

    return user


def require_role(
    allowed_roles: Sequence[str] | str,
) -> Callable[..., Coroutine[Any, Any, User]]:
    """Genera una dependencia de FastAPI que exige que el usuario tenga uno de los roles permitidos."""
    roles_set = (
        {allowed_roles}
        if isinstance(allowed_roles, str)
        else set(allowed_roles)
    )

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in roles_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: se requiere rol {', '.join(sorted(roles_set))}",
            )
        return current_user

    return role_checker


def require_service_key(
    service_key: str | None = Security(service_key_scheme),
) -> str:
    """Valida en tiempo constante la cabecera interna X-Service-Key usada por n8n."""
    expected = settings.N8N_INTERNAL_API_KEY
    if not service_key or not expected or not hmac.compare_digest(service_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cabecera X-Service-Key inválida o ausente",
        )
    return "n8n_service"


def require_service_or_role(
    allowed_roles: Sequence[str] | str,
) -> Callable[..., Coroutine[Any, Any, User | str]]:
    """Permite acceso por X-Service-Key interna (n8n) o por JWT Bearer con rol autorizado."""
    roles_set = (
        {allowed_roles}
        if isinstance(allowed_roles, str)
        else set(allowed_roles)
    )

    async def service_or_role_checker(
        service_key: str | None = Security(service_key_scheme),
        token: str | None = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
    ) -> User | str:
        if service_key is not None:
            return require_service_key(service_key)

        current_user = await get_current_user(token=token, db=db)
        if current_user.role not in roles_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: se requiere rol {', '.join(sorted(roles_set))}",
            )
        return current_user

    return service_or_role_checker


sys.modules.setdefault("dependencies.auth", sys.modules[__name__])
sys.modules.setdefault("apps.api.dependencies.auth", sys.modules[__name__])
