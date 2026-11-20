"""Exportación centralizada de modelos SQLAlchemy para Alembic y la API."""

import sys

try:
    from core.database import Base
    from models.audit_log import AuditLog
    from models.booking import ACTIVE_BOOKING_STATUSES, Booking, BookingStatus
    from models.conversation import Conversation
    from models.guest import Guest
    from models.operations import (
        CafeMenuItem,
        CafeOrder,
        Expense,
        FolioCharge,
        Product,
        SpecialEvent,
    )
    from models.room import Room
    from models.user import User, UserRole
except ImportError:
    from apps.api.core.database import Base
    from apps.api.models.audit_log import AuditLog
    from apps.api.models.booking import (
        ACTIVE_BOOKING_STATUSES,
        Booking,
        BookingStatus,
    )
    from apps.api.models.conversation import Conversation
    from apps.api.models.guest import Guest
    from apps.api.models.operations import (
        CafeMenuItem,
        CafeOrder,
        Expense,
        FolioCharge,
        Product,
        SpecialEvent,
    )
    from apps.api.models.room import Room
    from apps.api.models.user import User, UserRole

__all__ = [
    "ACTIVE_BOOKING_STATUSES",
    "AuditLog",
    "Base",
    "Booking",
    "BookingStatus",
    "CafeMenuItem",
    "CafeOrder",
    "Conversation",
    "Expense",
    "FolioCharge",
    "Guest",
    "Product",
    "Room",
    "SpecialEvent",
    "User",
    "UserRole",
]

sys.modules.setdefault("models", sys.modules[__name__])
sys.modules.setdefault("apps.api.models", sys.modules[__name__])
