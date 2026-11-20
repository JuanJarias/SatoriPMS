"""Funciones criptográficas para hashing de contraseñas (bcrypt) y tokens JWT (HS256)."""

from datetime import datetime, timedelta, timezone
import sys
from types import SimpleNamespace
from typing import Any

import bcrypt
from jose import JWTError, jwt

# Compatibilidad de passlib con bcrypt >= 4.1 (que eliminó bcrypt.__about__)
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = SimpleNamespace(__version__=getattr(bcrypt, "__version__", "4.0.0"))  # type: ignore[attr-defined]

from passlib.context import CryptContext

try:
    from core.config import settings
except ImportError:
    from apps.api.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Genera un hash bcrypt seguro a partir de una contraseña en texto plano."""
    try:
        return pwd_context.hash(password)
    except ValueError:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica en tiempo constante si la contraseña coincide con su hash bcrypt."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except ValueError:
            return False


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Firma un JSON Web Token (JWT) con HS256 incluyendo claims de identidad y rol."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.JWT_EXPIRES_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Decodifica y valida la firma criptográfica y expiración de un token JWT."""
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )


__all__ = [
    "JWTError",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "pwd_context",
    "verify_password",
]

sys.modules.setdefault("core.security", sys.modules[__name__])
sys.modules.setdefault("apps.api.core.security", sys.modules[__name__])
