"""Modelo relacional User (system_users) para autenticación JWT y RBAC (RN-10)."""

from datetime import datetime
from enum import StrEnum
import sys

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

try:
    from core.database import Base
except ImportError:
    from apps.api.core.database import Base


class UserRole(StrEnum):
    """Roles del personal en Torre Satori PMS (RN-10)."""

    ADMINISTRADOR = "Administrador"
    RECEPCIONISTA = "Recepcionista"


class User(Base):
    """Usuario interno del hotel (Administrador o Recepcionista)."""

    __tablename__ = "system_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(30), nullable=False, default=UserRole.RECEPCIONISTA.value
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('Administrador', 'Recepcionista')",
            name="chk_system_users_role",
        ),
    )


sys.modules.setdefault("models.user", sys.modules[__name__])
sys.modules.setdefault("apps.api.models.user", sys.modules[__name__])
