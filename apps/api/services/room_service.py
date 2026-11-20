"""Servicio de consulta de disponibilidad de habitaciones con filtrado inline en PostgreSQL 16 (Lote M2)."""

from datetime import date
from decimal import Decimal
import sys

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from models.booking import Booking, BookingStatus
    from models.operations import SpecialEvent
    from models.room import Room
    from schemas.room import RoomAvailabilityItem
    from services.pricing import (
        extra_guest_total,
        nightly_multipliers,
        room_stay_total,
    )
except ImportError:
    from apps.api.models.booking import Booking, BookingStatus
    from apps.api.models.operations import SpecialEvent
    from apps.api.models.room import Room
    from apps.api.schemas.room import RoomAvailabilityItem
    from apps.api.services.pricing import (
        extra_guest_total,
        nightly_multipliers,
        room_stay_total,
    )


async def load_active_events(
    db: AsyncSession,
    check_in: date,
    check_out: date,
) -> list[SpecialEvent]:
    """Eventos activos que cubren al menos una noche de la estadía [check_in, check_out)."""
    result = await db.execute(
        select(SpecialEvent).where(
            SpecialEvent.active.is_(True),
            SpecialEvent.start_date < check_out,
            SpecialEvent.end_date >= check_in,
        )
    )
    return list(result.scalars().all())


def calculate_room_stay_price(
    room: Room,
    check_in: date,
    check_out: date,
    adults: int,
    events: list[SpecialEvent] | None = None,
) -> tuple[int, int, Decimal]:
    """Calcula noches, adultos adicionales y precio total (RN-01) con eventos por noche."""
    multipliers = nightly_multipliers(check_in, check_out, events)
    nights = len(multipliers)
    extra_adults = max(0, adults - room.base_adults_capacity)
    base_cost = room_stay_total(room.price_per_night, multipliers)
    extra_cost = extra_guest_total(room.extra_guest_price, extra_adults, multipliers)
    total_price = (base_cost + extra_cost).quantize(Decimal("0.01"))
    return nights, extra_adults, total_price


async def get_available_rooms(
    db: AsyncSession,
    check_in: date,
    check_out: date,
    adults: int = 2,
    children: int = 0,
    with_pet: bool = False,
) -> list[RoomAvailabilityItem]:
    """Consulta habitaciones disponibles en PostgreSQL ignorando bloqueos con expires_at <= NOW()."""
    if check_in >= check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de check_in debe ser anterior a check_out",
        )
    if adults < 1 or children < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cantidad de adultos debe ser al menos 1 y niños no negativo",
        )

    # Subconsulta de habitaciones ocupadas que solapan el rango [check_in, check_out)
    # Ignora automáticamente bloqueos temporales vencidos (expires_at <= NOW())
    overlapping_active_bookings = (
        select(Booking.room_id)
        .where(
            func.daterange(Booking.check_in, Booking.check_out, "[)").op("&&")(
                func.daterange(check_in, check_out, "[)")
            ),
            or_(
                Booking.status.in_(
                    [
                        BookingStatus.PENDIENTE_PAGO.value,
                        BookingStatus.CONFIRMADA.value,
                        BookingStatus.EN_CURSO.value,
                    ]
                ),
                and_(
                    Booking.status == BookingStatus.BLOQUEADA_TEMPORAL.value,
                    Booking.expires_at > func.now(),
                ),
            ),
        )
        .scalar_subquery()
    )

    stmt = (
        select(Room)
        .where(
            Room.active.is_(True),
            Room.status == "available",
            Room.max_adults_capacity >= adults,
            Room.children_capacity >= children,
            Room.id.not_in(overlapping_active_bookings),
        )
        .order_by(func.length(Room.number), Room.number.asc())
    )

    if with_pet:
        stmt = stmt.where(Room.allows_pets.is_(True))

    result = await db.execute(stmt)
    rooms = result.scalars().all()

    events = await load_active_events(db, check_in, check_out)
    items: list[RoomAvailabilityItem] = []
    for room in rooms:
        nights, extra_adults, total_price = calculate_room_stay_price(
            room=room,
            check_in=check_in,
            check_out=check_out,
            adults=adults,
            events=events,
        )
        items.append(
            RoomAvailabilityItem(
                id=room.id,
                number=room.number,
                name=room.name,
                description=room.description,
                type=room.type,
                base_adults_capacity=room.base_adults_capacity,
                max_adults_capacity=room.max_adults_capacity,
                children_capacity=room.children_capacity,
                extra_guest_price=room.extra_guest_price,
                allows_pets=room.allows_pets,
                price_per_night=room.price_per_night,
                nights=nights,
                extra_adults=extra_adults,
                total_price=total_price,
            )
        )

    return items


sys.modules.setdefault("services.room_service", sys.modules[__name__])
sys.modules.setdefault("apps.api.services.room_service", sys.modules[__name__])
