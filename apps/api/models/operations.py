"""Modelos operacionales en PostgreSQL: Tienda, Cargos al Folio, Salgados Café, Eventos y Egresos (Lote P1)."""

from datetime import date, datetime
from decimal import Decimal
import sys

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

try:
    from core.database import Base
except ImportError:
    from apps.api.core.database import Base


class Product(Base):
    """Catálogo e inventario de productos de la Tienda del Hotel."""

    __tablename__ = "product"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("price >= 0", name="chk_product_price"),
        CheckConstraint("stock >= 0", name="chk_product_stock"),
    )


class FolioCharge(Base):
    """Cargos consumidos por huéspedes (Tienda o Salgados Café) vinculados a reserva o habitación."""

    __tablename__ = "folio_charge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int | None] = mapped_column(
        ForeignKey("booking.id", ondelete="SET NULL"), nullable=True
    )
    room_id: Mapped[int | None] = mapped_column(
        ForeignKey("room.id", ondelete="SET NULL"), nullable=True
    )
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="tienda")
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_folio_charge_qty"),
        CheckConstraint("total_amount >= 0", name="chk_folio_charge_total"),
        Index("idx_folio_charge_booking", "booking_id"),
        Index("idx_folio_charge_room", "room_id"),
    )


class CafeMenuItem(Base):
    """Carta oficial de desayunos, barismo y experiencias de Salgados Café."""

    __tablename__ = "cafe_menu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (CheckConstraint("price >= 0", name="chk_cafe_menu_price"),)


class CafeOrder(Base):
    """Comandas registradas en Salgados Café con liquidación directa o cargo al folio."""

    __tablename__ = "cafe_order"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    booking_id: Mapped[int | None] = mapped_column(
        ForeignKey("booking.id", ondelete="SET NULL"), nullable=True
    )
    room_id: Mapped[int | None] = mapped_column(
        ForeignKey("room.id", ondelete="SET NULL"), nullable=True
    )
    table_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    guest_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    items_json: Mapped[str] = mapped_column(Text, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="chk_cafe_order_total"),
        Index("idx_cafe_order_booking", "booking_id"),
    )


class SpecialEvent(Base):
    """Eventos turísticos y reglas dinámicas de descuento o recargo por fechas (HU-12)."""

    __tablename__ = "special_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    discount_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0.00")
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("start_date <= end_date", name="chk_special_event_dates"),
        Index("idx_special_event_dates", "start_date", "end_date"),
    )


class Expense(Base):
    """Registro de egresos operativos con anulación lógica auditable."""

    __tablename__ = "expense"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    voided: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    voided_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_expense_amount"),
        Index("idx_expense_date", "expense_date"),
    )


sys.modules.setdefault("models.operations", sys.modules[__name__])
sys.modules.setdefault("apps.api.models.operations", sys.modules[__name__])
