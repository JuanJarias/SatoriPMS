"""Modelo relacional Room para las 9 habitaciones de Hotel Torre Satori."""

from decimal import Decimal
import sys

from sqlalchemy import Boolean, CheckConstraint, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

try:
    from core.database import Base
except ImportError:
    from apps.api.core.database import Base


class Room(Base):
    """Catálogo de habitaciones del Hotel Torre Satori (Sevilla, Valle del Cauca)."""

    __tablename__ = "room"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    base_adults_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    max_adults_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    children_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    extra_guest_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    allows_pets: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    price_per_night: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="available"
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        CheckConstraint(
            "max_adults_capacity >= base_adults_capacity",
            name="chk_room_capacity",
        ),
        CheckConstraint(
            "status IN ('available', 'occupied', 'cleaning', 'maintenance')",
            name="chk_room_status",
        ),
        Index("idx_room_type", "type"),
        Index("idx_room_status", "status"),
    )


sys.modules.setdefault("models.room", sys.modules[__name__])
sys.modules.setdefault("apps.api.models.room", sys.modules[__name__])
