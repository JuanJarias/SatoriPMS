"""Estado PENDIENTE_PAGO para reservas del chatbot a la espera del pago (Wompi).

Revision ID: 005_pending_payment_status
Revises: 004_rooms_1_to_9_and_operations
Create Date: 2026-11-19 22:30:00

La reserva creada por el chatbot retiene la habitación (queda dentro de la restricción
EXCLUDE GiST) hasta que llega el pago aprobado; entonces pasa a CONFIRMADA.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "005_pending_payment_status"
down_revision: str | None = "004_rooms_1_to_9_and_operations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_OLD_STATES = "'BLOQUEADA_TEMPORAL', 'CONFIRMADA', 'EN_CURSO'"
_NEW_STATES = "'BLOQUEADA_TEMPORAL', 'PENDIENTE_PAGO', 'CONFIRMADA', 'EN_CURSO'"


def _rebuild(active_states: str, all_states: str) -> None:
    op.execute("ALTER TABLE booking DROP CONSTRAINT no_overlapping_bookings")
    op.drop_constraint("chk_booking_status", "booking", type_="check")
    op.create_check_constraint("chk_booking_status", "booking", f"status IN ({all_states})")
    op.execute(
        "ALTER TABLE booking ADD CONSTRAINT no_overlapping_bookings "
        "EXCLUDE USING gist (room_id WITH =, daterange(check_in, check_out, '[)') WITH &&) "
        f"WHERE (status IN ({active_states}))"
    )


def upgrade() -> None:
    _rebuild(_NEW_STATES, _NEW_STATES + ", 'EXPIRADA', 'CANCELADA'")


def downgrade() -> None:
    op.execute("UPDATE booking SET status = 'CONFIRMADA' WHERE status = 'PENDIENTE_PAGO'")
    _rebuild(_OLD_STATES, _OLD_STATES + ", 'EXPIRADA', 'CANCELADA'")
