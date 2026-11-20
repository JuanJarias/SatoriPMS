"""Tabla system_users para autenticación JWT y roles RBAC Administrador/Recepcionista (Lote M1).

Revision ID: 002_system_users
Revises: 001_initial_schema
Create Date: 2026-11-19 13:30:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

from core.security import hash_password

revision: str = "002_system_users"
down_revision: str | None = "001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "system_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False, server_default="Recepcionista"),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "role IN ('Administrador', 'Recepcionista')",
            name="chk_system_users_role",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_system_users_username", "system_users", ["username"], unique=True)

    admin_hash = hash_password("admin123")
    recep_hash = hash_password("recepcion123")

    op.execute(
        sa.text(
            """
            INSERT INTO system_users (username, password_hash, role, name, active)
            VALUES
                ('admin', :admin_hash, 'Administrador', 'Administrador Torre Satori', TRUE),
                ('recepcion', :recep_hash, 'Recepcionista', 'Recepción Torre Satori', TRUE)
            ON CONFLICT (username) DO NOTHING
            """
        ).bindparams(admin_hash=admin_hash, recep_hash=recep_hash)
    )


def downgrade() -> None:
    op.drop_index("ix_system_users_username", table_name="system_users")
    op.drop_table("system_users")
