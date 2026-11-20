"""Job periódico de expiración de bloqueos temporales (RN-02) y notificación a n8n."""

import logging
import sys
from typing import Any

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.config import settings
    from core.database import AsyncSessionLocal
    from models.booking import Booking, BookingStatus
    from models.guest import Guest
    from models.room import Room
    from services.audit_service import record_audit
    from services.event_bus import publish_pms_event
except ImportError:
    from apps.api.core.config import settings
    from apps.api.core.database import AsyncSessionLocal
    from apps.api.models.booking import Booking, BookingStatus
    from apps.api.models.guest import Guest
    from apps.api.models.room import Room
    from apps.api.services.audit_service import record_audit
    from apps.api.services.event_bus import publish_pms_event

logger = logging.getLogger(__name__)


async def _notify_n8n_expired(expired_items: list[dict[str, Any]]) -> None:
    """Avisa opcionalmente al webhook de n8n cuando vencen candados de 15 min."""
    webhook_url = settings.N8N_EXPIRED_WEBHOOK_URL.strip()
    if not webhook_url or not expired_items:
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                webhook_url,
                headers={"X-Service-Key": settings.N8N_INTERNAL_API_KEY},
                json={"event": "booking.locks_expired", "items": expired_items},
            )
    except Exception as exc:
        logger.warning("No se pudo notificar expiración a n8n: %s", exc)


async def expire_stale_booking_locks(
    db: AsyncSession | None = None,
) -> list[dict[str, Any]]:
    """Marca como EXPIRADA los bloqueos BLOQUEADA_TEMPORAL con expires_at <= NOW() y avisa a n8n/SSE."""
    own_session = db is None
    session = AsyncSessionLocal() if own_session else db
    expired_items: list[dict[str, Any]] = []

    try:
        res = await session.execute(
            select(Booking).where(
                Booking.status == BookingStatus.BLOQUEADA_TEMPORAL.value,
                Booking.expires_at.is_not(None),
                Booking.expires_at <= func.now(),
            )
        )
        stale_bookings = list(res.scalars().all())
        if not stale_bookings:
            return []

        for b in stale_bookings:
            b.status = BookingStatus.EXPIRADA.value
            room = await session.get(Room, b.room_id)
            guest = await session.get(Guest, b.guest_id)
            expired_items.append(
                {
                    "bookingId": b.id,
                    "roomId": b.room_id,
                    "roomNumber": room.number if room else None,
                    "waId": guest.whatsapp_phone if guest else None,
                    "checkIn": b.check_in.isoformat(),
                    "checkOut": b.check_out.isoformat(),
                }
            )

        await record_audit(
            db=session,
            actor="apscheduler",
            action="BOOKING_LOCKS_EXPIRED_BATCH",
            entity="booking",
            entity_id=str(len(expired_items)),
            details={"booking_ids": [item["bookingId"] for item in expired_items]},
        )
        await session.commit()
    finally:
        if own_session:
            await session.close()

    publish_pms_event("booking.expired", {"expired": expired_items})
    await _notify_n8n_expired(expired_items)
    return expired_items


sys.modules.setdefault("services.expiration_service", sys.modules[__name__])
sys.modules.setdefault("apps.api.services.expiration_service", sys.modules[__name__])
