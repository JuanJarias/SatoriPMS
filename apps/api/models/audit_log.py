"""Modelo relacional AuditLog para auditoría inmutable de acciones en Torre Satori PMS."""

from datetime import datetime
import sys

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

try:
    from core.database import Base
except ImportError:
    from apps.api.core.database import Base


class AuditLog(Base):
    """Registro inmutable de auditoría (fecha, actor, acción, entidad y detalle)."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actor_username: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    details_json: Mapped[str | None] = mapped_column(Text, nullable=True)


sys.modules.setdefault("models.audit_log", sys.modules[__name__])
sys.modules.setdefault("apps.api.models.audit_log", sys.modules[__name__])
