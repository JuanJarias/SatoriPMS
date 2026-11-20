"""Migración de habitaciones 101-303 a 1-9 con tarifas vigentes y creación de tablas operativas (Lote P1).

Revision ID: 004_rooms_1_to_9_and_operations
Revises: 003_conversations_and_payments
Create Date: 2026-11-19 19:45:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "004_rooms_1_to_9_and_operations"
down_revision: str | None = "003_conversations_and_payments"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_ROOM_UPGRADES = [
    ("101", "1", "Jardín", "Sencilla", 2, 2, 0, True, 180000.00, 40000.00),
    ("102", "2", "Familiar", "Familiar", 4, 5, 1, False, 290000.00, 40000.00),
    ("103", "3", "Patio", "Sencilla", 2, 2, 0, True, 170000.00, 40000.00),
    ("201", "4", "Balcón", "Doble", 2, 3, 1, False, 210000.00, 40000.00),
    ("202", "5", "Suite Satori", "Suite", 2, 4, 2, True, 380000.00, 40000.00),
    ("203", "6", "Cafetal", "Doble", 2, 3, 1, False, 220000.00, 40000.00),
    ("301", "7", "Mirador del Valle", "Suite", 2, 4, 1, False, 350000.00, 50000.00),
    ("302", "8", "Atardecer", "Doble", 2, 2, 0, False, 200000.00, 40000.00),
    ("303", "9", "Cordillera", "Familiar", 4, 6, 2, True, 320000.00, 45000.00),
]

_ROOM_DOWNGRADES = [
    ("1", "101", "Habitación Estándar 101", "ESTANDAR", 2, 3, 1, True, 120000.00, 20000.00),
    ("2", "102", "Habitación Estándar 102", "ESTANDAR", 2, 3, 1, True, 120000.00, 20000.00),
    ("3", "103", "Habitación Estándar 103", "ESTANDAR", 2, 3, 1, False, 120000.00, 20000.00),
    ("4", "201", "Habitación Doble 201", "DOBLE", 2, 4, 2, True, 160000.00, 25000.00),
    ("5", "202", "Habitación Doble 202", "DOBLE", 2, 4, 2, True, 160000.00, 25000.00),
    ("6", "203", "Habitación Doble 203", "DOBLE", 2, 4, 2, False, 160000.00, 25000.00),
    ("7", "301", "Suite Mirador 301", "SUITE", 4, 6, 2, True, 220000.00, 30000.00),
    ("8", "302", "Suite Mirador 302", "SUITE", 4, 6, 2, True, 220000.00, 30000.00),
    ("9", "303", "Suite Presidencial 303", "SUITE", 4, 6, 2, True, 250000.00, 30000.00),
]


def upgrade() -> None:
    # 1. Migrar habitaciones 101-303 -> 1-9 conservando room.id para preservar FKs
    for old_num, new_num, name, rtype, base_cap, max_cap, ch_cap, pets, price, extra in _ROOM_UPGRADES:
        op.execute(
            sa.text(
                """
                UPDATE room
                SET number = :new_num,
                    name = :name,
                    type = :rtype,
                    base_adults_capacity = :base_cap,
                    max_adults_capacity = :max_cap,
                    children_capacity = :ch_cap,
                    allows_pets = :pets,
                    price_per_night = :price,
                    extra_guest_price = :extra
                WHERE number = :old_num
                """
            ).bindparams(
                old_num=old_num,
                new_num=new_num,
                name=name,
                rtype=rtype,
                base_cap=base_cap,
                max_cap=max_cap,
                ch_cap=ch_cap,
                pets=pets,
                price=price,
                extra=extra,
            )
        )

    # 2. Catálogo de productos de Tienda Hotel
    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=60), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price >= 0", name="chk_product_price"),
        sa.CheckConstraint("stock >= 0", name="chk_product_stock"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    # 3. Cargos al folio de habitación / reserva
    op.create_table(
        "folio_charge",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=True),
        sa.Column("room_id", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=30), nullable=False, server_default="tienda"),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("paid", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="chk_folio_charge_qty"),
        sa.CheckConstraint("total_amount >= 0", name="chk_folio_charge_total"),
        sa.ForeignKeyConstraint(["booking_id"], ["booking.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["room_id"], ["room.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_folio_charge_booking", "folio_charge", ["booking_id"], unique=False)
    op.create_index("idx_folio_charge_room", "folio_charge", ["room_id"], unique=False)

    # 4. Carta de Salgados Café
    op.create_table(
        "cafe_menu",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price >= 0", name="chk_cafe_menu_price"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    # 5. Comandas de Salgados Café
    op.create_table(
        "cafe_order",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_code", sa.String(length=30), nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=True),
        sa.Column("room_id", sa.Integer(), nullable=True),
        sa.Column("table_number", sa.String(length=20), nullable=True),
        sa.Column("guest_name", sa.String(length=100), nullable=True),
        sa.Column("items_json", sa.Text(), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("total_amount >= 0", name="chk_cafe_order_total"),
        sa.ForeignKeyConstraint(["booking_id"], ["booking.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["room_id"], ["room.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_code"),
    )
    op.create_index("idx_cafe_order_booking", "cafe_order", ["booking_id"], unique=False)

    # 6. Eventos especiales y descuentos/recargos dinámicos (HU-12)
    op.create_table(
        "special_event",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("discount_percentage", sa.Numeric(precision=5, scale=2), nullable=False, server_default="0.00"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("start_date <= end_date", name="chk_special_event_dates"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_special_event_dates", "special_event", ["start_date", "end_date"], unique=False)

    # 7. Egresos operativos
    op.create_table(
        "expense",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("voided", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("voided_reason", sa.String(length=255), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("amount > 0", name="chk_expense_amount"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_expense_date", "expense", ["expense_date"], unique=False)

    # 8. Semilla limpia solo de catálogos reales (sin huéspedes, reservas ni egresos ficticios)
    op.execute(
        """
        INSERT INTO product (code, name, category, price, stock, active)
        VALUES
            ('p1', 'Agua Cristal 600 ml', 'Bebidas', 3000.00, 24, TRUE),
            ('p2', 'Gaseosa Postobón 400 ml', 'Bebidas', 4000.00, 12, TRUE),
            ('p3', 'Cerveza Club Colombia', 'Bebidas', 7000.00, 8, TRUE),
            ('p4', 'Papas Margarita pollo', 'Snacks', 3500.00, 15, TRUE),
            ('p5', 'Chocolatina Jet', 'Snacks', 2500.00, 10, TRUE),
            ('p6', 'Salgados Café Origen Especial 250g', 'Café de Origen', 25000.00, 20, TRUE),
            ('p7', 'Salgados Café Drip Bag (Pack x 5)', 'Café de Origen', 16000.00, 18, TRUE),
            ('p8', 'Protector solar FPS 50', 'Cuidado personal', 28000.00, 4, TRUE),
            ('p9', 'Cepillo y crema dental', 'Cuidado personal', 6000.00, 9, TRUE)
        ON CONFLICT (code) DO NOTHING;
        """
    )

    op.execute(
        """
        INSERT INTO cafe_menu (code, name, category, description, price, available)
        VALUES
            ('m1', 'Desayuno Típico Vallecaucano', 'breakfast', 'Huevos al gusto, calentado o arepa con queso, fruta de temporada y café Salgados.', 18000.00, TRUE),
            ('m2', 'Desayuno Continental Satori', 'breakfast', 'Canasta de panes artesanales, mermelada de mora silvestre, mantequilla, huevos y jugo.', 16000.00, TRUE),
            ('m3', 'Café Espresso Salgados', 'coffee', 'Extracción 30ml de café especial tostión media-alta.', 5000.00, TRUE),
            ('m4', 'Café Filtrado V60 / Chemex', 'coffee', 'Método artesanal con notas a panela, cítricos y chocolate.', 9000.00, TRUE),
            ('m5', 'Cappuccino de la Casa', 'coffee', 'Espresso doble con leche texturizada al vapor y canela.', 7500.00, TRUE),
            ('m6', 'Cata Guiada & Barismo Salgados', 'experience', 'Recorrido sensorial por 3 variedades de café de origen Sevilla con barista profesional.', 45000.00, TRUE),
            ('m7', 'Tarta de Café y Arequipe', 'bakery', 'Porción individual con reducción de café Salgados.', 8500.00, TRUE)
        ON CONFLICT (code) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.drop_index("idx_expense_date", table_name="expense")
    op.drop_table("expense")
    op.drop_index("idx_special_event_dates", table_name="special_event")
    op.drop_table("special_event")
    op.drop_index("idx_cafe_order_booking", table_name="cafe_order")
    op.drop_table("cafe_order")
    op.drop_table("cafe_menu")
    op.drop_index("idx_folio_charge_room", table_name="folio_charge")
    op.drop_index("idx_folio_charge_booking", table_name="folio_charge")
    op.drop_table("folio_charge")
    op.drop_table("product")

    for cur_num, old_num, name, rtype, base_cap, max_cap, ch_cap, pets, price, extra in _ROOM_DOWNGRADES:
        op.execute(
            sa.text(
                """
                UPDATE room
                SET number = :old_num,
                    name = :name,
                    type = :rtype,
                    base_adults_capacity = :base_cap,
                    max_adults_capacity = :max_cap,
                    children_capacity = :ch_cap,
                    allows_pets = :pets,
                    price_per_night = :price,
                    extra_guest_price = :extra
                WHERE number = :cur_num
                """
            ).bindparams(
                cur_num=cur_num,
                old_num=old_num,
                name=name,
                rtype=rtype,
                base_cap=base_cap,
                max_cap=max_cap,
                ch_cap=ch_cap,
                pets=pets,
                price=price,
                extra=extra,
            )
        )
