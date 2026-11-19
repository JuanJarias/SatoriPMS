"""Dependencias de autenticación JWT y control de acceso basado en roles (RBAC RN-10)."""

from collections.abc import Callable, Coroutine, Sequence
import sys
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from core.security import JWTError, decode_access_token
    from models.user import User
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.core.security import JWTError, decode_access_token
    from apps.api.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


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


sys.modules.setdefault("dependencies.auth", sys.modules[__name__])
sys.modules.setdefault("apps.api.dependencies.auth", sys.modules[__name__])
