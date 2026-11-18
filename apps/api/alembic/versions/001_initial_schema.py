"""Esquema inicial con btree_gist, restricción EXCLUDE GiST (RN-02) y 9 habitaciones.

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-11-18 09:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Extensión btree_gist obligatoria para combinar igualdad escalar (=) e intersección de rangos (&&)
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    # 2. Catálogo de habitaciones (9 habitaciones de Torre Satori)
    op.create_table(
        "room",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("number", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("base_adults_capacity", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("max_adults_capacity", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("children_capacity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("extra_guest_price", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0.00"),
        sa.Column("allows_pets", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("price_per_night", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="available"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.CheckConstraint("max_adults_capacity >= base_adults_capacity", name="chk_room_capacity"),
        sa.CheckConstraint(
            "status IN ('available', 'occupied', 'cleaning', 'maintenance')",
            name="chk_room_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("number"),
    )
    op.create_index("idx_room_type", "room", ["type"], unique=False)
    op.create_index("idx_room_status", "room", ["status"], unique=False)

    # 3. Huéspedes (con consentimiento Ley 1581)
    op.create_table(
        "guest",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("whatsapp_phone", sa.String(length=20), nullable=True),
        sa.Column("document_number", sa.String(length=50), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("habeas_data_accepted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("whatsapp_phone"),
    )

    # 4. Reservas con candado atómico EXCLUDE USING gist (RN-02)
    op.create_table(
        "booking",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guest_id", sa.Integer(), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("check_in", sa.Date(), nullable=False),
        sa.Column("check_out", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="BLOQUEADA_TEMPORAL"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payment_status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("payment_id", sa.String(length=100), nullable=True),
        sa.Column("adults", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("children", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("with_pet", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("total_price", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0.00"),
        sa.Column("paid_amount", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0.00"),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="chatbot"),
        sa.Column("group_code", sa.String(length=20), nullable=True),
        sa.Column("reservation_group_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("companions", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("check_in < check_out", name="chk_booking_dates"),
        sa.CheckConstraint("adults >= 0 AND children >= 0", name="chk_booking_people"),
        sa.CheckConstraint(
            "status IN ('BLOQUEADA_TEMPORAL', 'CONFIRMADA', 'EN_CURSO', 'EXPIRADA', 'CANCELADA')",
            name="chk_booking_status",
        ),
        postgresql.ExcludeConstraint(
            (sa.column("room_id"), "="),
            (sa.column("daterange(check_in, check_out, '[)')", is_literal=True), "&&"),
            name="no_overlapping_bookings",
            using="gist",
            where=sa.text("status IN ('BLOQUEADA_TEMPORAL', 'CONFIRMADA', 'EN_CURSO')"),
        ),
        sa.ForeignKeyConstraint(["guest_id"], ["guest.id"]),
        sa.ForeignKeyConstraint(["room_id"], ["room.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_id"),
    )
    op.create_index("idx_booking_room", "booking", ["room_id"], unique=False)
    op.create_index("idx_booking_guest", "booking", ["guest_id"], unique=False)
    op.create_index("idx_booking_status", "booking", ["status"], unique=False)
    op.create_index("idx_booking_group_code", "booking", ["group_code"], unique=False)

    # 5. Auditoría inmutable
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actor_username", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=True),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # 6. Semilla inicial de las 9 habitaciones del Hotel Torre Satori (Sevilla, Valle del Cauca)
    op.execute(
        """
        INSERT INTO room (number, name, type, base_adults_capacity, max_adults_capacity, children_capacity, allows_pets, price_per_night, extra_guest_price)
        VALUES
            ('101', 'Habitación Estándar 101', 'ESTANDAR', 2, 3, 1, TRUE,  120000.00, 20000.00),
            ('102', 'Habitación Estándar 102', 'ESTANDAR', 2, 3, 1, TRUE,  120000.00, 20000.00),
            ('103', 'Habitación Estándar 103', 'ESTANDAR', 2, 3, 1, FALSE, 120000.00, 20000.00),
            ('201', 'Habitación Doble 201',    'DOBLE',    2, 4, 2, TRUE,  160000.00, 25000.00),
            ('202', 'Habitación Doble 202',    'DOBLE',    2, 4, 2, TRUE,  160000.00, 25000.00),
            ('203', 'Habitación Doble 203',    'DOBLE',    2, 4, 2, FALSE, 160000.00, 25000.00),
            ('301', 'Suite Mirador 301',       'SUITE',    4, 6, 2, TRUE,  220000.00, 30000.00),
            ('302', 'Suite Mirador 302',       'SUITE',    4, 6, 2, TRUE,  220000.00, 30000.00),
            ('303', 'Suite Presidencial 303',  'SUITE',    4, 6, 2, TRUE,  250000.00, 30000.00)
        ON CONFLICT (number) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_index("idx_booking_group_code", table_name="booking")
    op.drop_index("idx_booking_status", table_name="booking")
    op.drop_index("idx_booking_guest", table_name="booking")
    op.drop_index("idx_booking_room", table_name="booking")
    op.drop_table("booking")
    op.drop_table("guest")
    op.drop_index("idx_room_status", table_name="room")
    op.drop_index("idx_room_type", table_name="room")
    op.drop_table("room")
