"""Modelo relacional Guest para huéspedes y cumplimiento de Ley 1581."""

from datetime import datetime
import sys

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

try:
    from core.database import Base
except ImportError:
    from apps.api.core.database import Base


class Guest(Base):
    """Huésped registrado por WhatsApp o recepción con consentimiento Ley 1581."""

    __tablename__ = "guest"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    whatsapp_phone: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True
    )
    document_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    habeas_data_accepted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


sys.modules.setdefault("models.guest", sys.modules[__name__])
sys.modules.setdefault("apps.api.models.guest", sys.modules[__name__])
