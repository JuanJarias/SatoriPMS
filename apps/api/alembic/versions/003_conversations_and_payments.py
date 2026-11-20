"""Tabla conversation para persistencia de sesiones WhatsApp/n8n en PostgreSQL sin Redis (Lote M3).

Revision ID: 003_conversations_and_payments
Revises: 002_system_users
Create Date: 2026-11-19 14:30:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "003_conversations_and_payments"
down_revision: str | None = "002_system_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "conversation",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_key", sa.String(length=120), nullable=False),
        sa.Column("wa_id", sa.String(length=40), nullable=True),
        sa.Column("sender_name", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=40), nullable=False, server_default="menu"),
        sa.Column("step", sa.String(length=40), nullable=False, server_default="inicio"),
        sa.Column("agent_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("session_data", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_key"),
    )
    op.create_index("ix_conversation_session_key", "conversation", ["session_key"], unique=True)
    op.create_index("ix_conversation_wa_id", "conversation", ["wa_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_conversation_wa_id", table_name="conversation")
    op.drop_index("ix_conversation_session_key", table_name="conversation")
    op.drop_table("conversation")
