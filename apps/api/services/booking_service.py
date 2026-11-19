"""Servicio de bloqueo temporal atómico de 15 minutos con protección GiST (RN-01, RN-02, RN-12)."""

from datetime import datetime, timedelta, timezone
import sys

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from models.booking import Booking, BookingStatus
    from models.guest import Guest
    from models.room import Room
    from schemas.booking import (
        LockRequest,
        LockResponse,
        UnlockRequest,
        UnlockResponse,
    )
    from services.room_service import calculate_room_stay_price
except ImportError:
    from apps.api.models.booking import Booking, BookingStatus
    from apps.api.models.guest import Guest
    from apps.api.models.room import Room
    from apps.api.schemas.booking import (
        LockRequest,
        LockResponse,
        UnlockRequest,
        UnlockResponse,
    )
    from apps.api.services.room_service import calculate_room_stay_price

LOCK_DURATION_MINUTES = 15


async def _resolve_guest_id(db: AsyncSession, payload: LockRequest) -> int:
    """Crea o actualiza el registro del huésped con consentimiento Ley 1581 de forma segura ante concurrencia."""
    if payload.whatsapp_phone:
        stmt = (
            pg_insert(Guest)
            .values(
                whatsapp_phone=payload.whatsapp_phone,
                document_number=payload.document_number,
                name=payload.guest_name,
                email=payload.email,
                habeas_data_accepted=True,
            )
            .on_conflict_do_update(
                index_elements=[Guest.whatsapp_phone],
                set_={
                    "name": payload.guest_name,
                    "habeas_data_accepted": True,
                    "updated_at": func.now(),
                },
            )
            .returning(Guest.id)
        )
        res = await db.execute(stmt)
        return int(res.scalar_one())

    guest = Guest(
        whatsapp_phone=None,
        document_number=payload.document_number,
        name=payload.guest_name,
        email=payload.email,
        habeas_data_accepted=True,
    )
    db.add(guest)
    await db.flush()
    return guest.id


async def create_booking_lock(
    db: AsyncSession,
    payload: LockRequest,
) -> LockResponse:
    """Crea un bloqueo temporal de 15 minutos expirando candados vencidos en la misma transacción."""
    # 1. Validar rango de fechas
    if payload.check_in >= payload.check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de check_in debe ser anterior a check_out",
        )

    # 2. RN-12: Validar consentimiento obligatorio de Ley 1581 (Habeas Data)
    if not payload.habeas_data_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe aceptar la autorización de tratamiento de datos personales (Ley 1581 / RN-12)",
        )

    # 3. Buscar habitación activa
    room_res = await db.execute(
        select(Room).where(Room.id == payload.room_id, Room.active.is_(True))
    )
    room = room_res.scalar_one_or_none()
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habitación no encontrada o inactiva",
        )

    # 4. RN-01: Validar capacidad máxima de adultos, niños y política de mascotas
    if (
        payload.adults > room.max_adults_capacity
        or payload.children > room.children_capacity
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Capacidad excedida (RN-01): máximo {room.max_adults_capacity} adultos "
                f"y {room.children_capacity} niños para la habitación {room.number}"
            ),
        )

    if payload.with_pet and not room.allows_pets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La habitación {room.number} no admite mascotas",
        )

    nights, extra_adults, total_price = calculate_room_stay_price(
        room=room,
        check_in=payload.check_in,
        check_out=payload.check_out,
        adults=payload.adults,
    )

    try:
        guest_id = await _resolve_guest_id(db, payload)

        # 5. RN-02 / Decisión 2: Expirar atómicamente en la misma transacción candados vencidos de esa habitación
        await db.execute(
            update(Booking)
            .where(
                Booking.room_id == room.id,
                Booking.status == BookingStatus.BLOQUEADA_TEMPORAL.value,
                Booking.expires_at <= func.now(),
            )
            .values(
                status=BookingStatus.EXPIRADA.value,
                updated_at=func.now(),
            )
        )

        # 6. Insertar fila BLOQUEADA_TEMPORAL con expires_at = NOW() + 15 min protegida por EXCLUDE USING gist
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=LOCK_DURATION_MINUTES
        )
        booking = Booking(
            guest_id=guest_id,
            room_id=room.id,
            check_in=payload.check_in,
            check_out=payload.check_out,
            status=BookingStatus.BLOQUEADA_TEMPORAL.value,
            expires_at=expires_at,
            payment_status="pending",
            adults=payload.adults,
            children=payload.children,
            with_pet=payload.with_pet,
            total_price=total_price,
            source=payload.source,
        )
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
    except (IntegrityError, OperationalError) as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La habitación no está disponible para el rango de fechas solicitado (conflicto GiST RN-02)",
        ) from exc

    return LockResponse(
        booking_id=booking.id,
        room_id=room.id,
        room_number=room.number,
        status=booking.status,
        check_in=booking.check_in,
        check_out=booking.check_out,
        nights=nights,
        adults=booking.adults,
        children=booking.children,
        extra_adults=extra_adults,
        total_price=booking.total_price,
        expires_at=booking.expires_at or expires_at,
    )


async def release_booking_lock(
    db: AsyncSession,
    payload: UnlockRequest,
) -> UnlockResponse:
    """Marca un bloqueo temporal como EXPIRADA para liberar inmediatamente el rango en el índice GiST."""
    result = await db.execute(
        select(Booking).where(Booking.id == payload.booking_id)
    )
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bloqueo no encontrado",
        )
    if booking.status == BookingStatus.BLOQUEADA_TEMPORAL.value:
        booking.status = BookingStatus.EXPIRADA.value
        await db.commit()
        await db.refresh(booking)

    return UnlockResponse(booking_id=booking.id, status=booking.status)


sys.modules.setdefault("services.booking_service", sys.modules[__name__])
sys.modules.setdefault("apps.api.services.booking_service", sys.modules[__name__])
