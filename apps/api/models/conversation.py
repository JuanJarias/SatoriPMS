"""Modelo relacional Conversation para persistir sesiones de WhatsApp/n8n en PostgreSQL 16 sin Redis (Lote M3)."""

from datetime import datetime
import sys

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

try:
    from core.database import Base
except ImportError:
    from apps.api.core.database import Base


class Conversation(Base):
    """Contexto conversacional y enlaces de pago de WhatsApp/n8n persistidos en PostgreSQL."""

    __tablename__ = "conversation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_key: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
    )
    wa_id: Mapped[str | None] = mapped_column(
        String(40), nullable=True, index=True
    )
    sender_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(
        String(40), nullable=False, default="menu"
    )
    step: Mapped[str] = mapped_column(
        String(40), nullable=False, default="inicio"
    )
    agent_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    session_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
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


sys.modules.setdefault("models.conversation", sys.modules[__name__])
sys.modules.setdefault("apps.api.models.conversation", sys.modules[__name__])
