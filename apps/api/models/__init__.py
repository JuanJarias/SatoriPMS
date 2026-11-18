"""Exportación centralizada de modelos SQLAlchemy para Alembic y la API."""

import sys

try:
    from core.database import Base
    from models.audit_log import AuditLog
    from models.booking import ACTIVE_BOOKING_STATUSES, Booking, BookingStatus
    from models.guest import Guest
    from models.room import Room
except ImportError:
    from apps.api.core.database import Base
    from apps.api.models.audit_log import AuditLog
    from apps.api.models.booking import (
        ACTIVE_BOOKING_STATUSES,
        Booking,
        BookingStatus,
    )
    from apps.api.models.guest import Guest
    from apps.api.models.room import Room

__all__ = [
    "ACTIVE_BOOKING_STATUSES",
    "AuditLog",
    "Base",
    "Booking",
    "BookingStatus",
    "Guest",
    "Room",
]

sys.modules.setdefault("models", sys.modules[__name__])
sys.modules.setdefault("apps.api.models", sys.modules[__name__])
