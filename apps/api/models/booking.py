"""Modelo relacional Booking con restricción de exclusión GiST (RN-02)."""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
import sys
import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint, UUID
from sqlalchemy.orm import Mapped, mapped_column

try:
    from core.database import Base
except ImportError:
    from apps.api.core.database import Base


class BookingStatus(StrEnum):
    """Estados canónicos de reserva en español en la base de datos (Decisión 1)."""

    BLOQUEADA_TEMPORAL = "BLOQUEADA_TEMPORAL"
    PENDIENTE_PAGO = "PENDIENTE_PAGO"
    CONFIRMADA = "CONFIRMADA"
    EN_CURSO = "EN_CURSO"
    EXPIRADA = "EXPIRADA"
    CANCELADA = "CANCELADA"


ACTIVE_BOOKING_STATUSES = (
    BookingStatus.BLOQUEADA_TEMPORAL.value,
    BookingStatus.PENDIENTE_PAGO.value,
    BookingStatus.CONFIRMADA.value,
    BookingStatus.EN_CURSO.value,
)


class Booking(Base):
    """Reserva de habitación protegida por candado atómico EXCLUDE USING gist (RN-02)."""

    __tablename__ = "booking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guest_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("guest.id"), nullable=False
    )
    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("room.id"), nullable=False
    )
    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=BookingStatus.BLOQUEADA_TEMPORAL.value,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    payment_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    payment_id: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True
    )
    adults: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    children: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    with_pet: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="chatbot")
    group_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reservation_group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    companions: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint("check_in < check_out", name="chk_booking_dates"),
        CheckConstraint(
            "adults >= 0 AND children >= 0", name="chk_booking_people"
        ),
        CheckConstraint(
            "status IN ('BLOQUEADA_TEMPORAL', 'PENDIENTE_PAGO', 'CONFIRMADA', 'EN_CURSO', 'EXPIRADA', 'CANCELADA')",
            name="chk_booking_status",
        ),
        ExcludeConstraint(
            (Column("room_id"), "="),
            (Column("daterange(check_in, check_out, '[)')", quote=False), "&&"),
            name="no_overlapping_bookings",
            using="gist",
            where=text(
                "status IN ('BLOQUEADA_TEMPORAL', 'PENDIENTE_PAGO', 'CONFIRMADA', 'EN_CURSO')"
            ),
        ),
        Index("idx_booking_room", "room_id"),
        Index("idx_booking_guest", "guest_id"),
        Index("idx_booking_status", "status"),
        Index("idx_booking_group_code", "group_code"),
    )


sys.modules.setdefault("models.booking", sys.modules[__name__])
sys.modules.setdefault("apps.api.models.booking", sys.modules[__name__])
