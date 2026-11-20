"""Pruebas de la restricción GiST anti-sobreventa (RN-02) y concurrencia en PostgreSQL 16 (Lote M0)."""

import asyncio
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, OperationalError

from apps.api.core.database import AsyncSessionLocal
from apps.api.models import Booking, BookingStatus, Guest, Room


async def _prepare_test_guest_and_room() -> tuple[int, int]:
    """Crea o recupera un huésped de prueba y limpia reservas previas de la habitación 1."""
    async with AsyncSessionLocal() as session:
        room_res = await session.execute(select(Room).where(Room.number == "1"))
        room = room_res.scalar_one()

        await session.execute(delete(Booking).where(Booking.room_id == room.id))

        guest_res = await session.execute(
            select(Guest).where(Guest.whatsapp_phone == "+573000000001")
        )
        guest = guest_res.scalar_one_or_none()
        if guest is None:
            guest = Guest(
                whatsapp_phone="+573000000001",
                document_number="1111111111",
                name="Huésped Prueba RN02",
                email="rn02@satoripms.local",
                habeas_data_accepted=True,
            )
            session.add(guest)
            await session.flush()

        guest_id, room_id = guest.id, room.id
        await session.commit()
        return guest_id, room_id


@pytest.mark.asyncio
async def test_gist_rejects_overlapping_active_bookings() -> None:
    """Verifica que dos reservas activas solapadas en la misma habitación lancen IntegrityError."""
    guest_id, room_id = await _prepare_test_guest_and_room()

    async with AsyncSessionLocal() as session:
        b1 = Booking(
            guest_id=guest_id,
            room_id=room_id,
            check_in=date(2026, 12, 10),
            check_out=date(2026, 12, 15),
            status=BookingStatus.CONFIRMADA.value,
            adults=2,
            total_price=Decimal("600000.00"),
        )
        session.add(b1)
        await session.commit()

    async with AsyncSessionLocal() as session:
        b2_overlap = Booking(
            guest_id=guest_id,
            room_id=room_id,
            check_in=date(2026, 12, 12),
            check_out=date(2026, 12, 18),
            status=BookingStatus.BLOQUEADA_TEMPORAL.value,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
            adults=2,
            total_price=Decimal("720000.00"),
        )
        session.add(b2_overlap)
        with pytest.raises(IntegrityError):
            await session.commit()
        await session.rollback()


@pytest.mark.asyncio
async def test_gist_allows_contiguous_half_open_dates_and_inactive_statuses() -> None:
    """Verifica que el intervalo '[)' permita check-in el día de check-out previo y permita solapar sobre CANCELADA/EXPIRADA."""
    guest_id, room_id = await _prepare_test_guest_and_room()

    async with AsyncSessionLocal() as session:
        # 1. Reserva CANCELADA en el mismo rango no debe bloquear nuevas reservas
        cancelled = Booking(
            guest_id=guest_id,
            room_id=room_id,
            check_in=date(2026, 12, 1),
            check_out=date(2026, 12, 5),
            status=BookingStatus.CANCELADA.value,
            adults=2,
            total_price=Decimal("480000.00"),
        )
        # 2. Reserva CONFIRMADA en el mismo rango [2026-12-01, 2026-12-05)
        active_first = Booking(
            guest_id=guest_id,
            room_id=room_id,
            check_in=date(2026, 12, 1),
            check_out=date(2026, 12, 5),
            status=BookingStatus.CONFIRMADA.value,
            adults=2,
            total_price=Decimal("480000.00"),
        )
        # 3. Reserva contigua [2026-12-05, 2026-12-08) entra el mismo día que sale la anterior
        active_contiguous = Booking(
            guest_id=guest_id,
            room_id=room_id,
            check_in=date(2026, 12, 5),
            check_out=date(2026, 12, 8),
            status=BookingStatus.EN_CURSO.value,
            adults=2,
            total_price=Decimal("360000.00"),
        )
        session.add_all([cancelled, active_first, active_contiguous])
        await session.commit()


@pytest.mark.asyncio
async def test_concurrent_bookings_only_one_succeeds_rn02() -> None:
    """Lanza 10 transacciones simultáneas para la misma habitación y fechas; exactamente 1 triunfa y 9 fallan por GiST."""
    guest_id, room_id = await _prepare_test_guest_and_room()

    async def attempt_booking(idx: int) -> bool:
        async with AsyncSessionLocal() as session:
            booking = Booking(
                guest_id=guest_id,
                room_id=room_id,
                check_in=date(2026, 12, 20),
                check_out=date(2026, 12, 24),
                status=BookingStatus.BLOQUEADA_TEMPORAL.value,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
                adults=2,
                total_price=Decimal("480000.00"),
            )
            session.add(booking)
            try:
                await session.commit()
                return True
            except (IntegrityError, OperationalError):
                await session.rollback()
                return False

    results = await asyncio.gather(*(attempt_booking(i) for i in range(10)))
    assert results.count(True) == 1
    assert results.count(False) == 9
