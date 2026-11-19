"""Pruebas del endpoint GET /api/v1/rooms/availability con RN-01 y filtrado inline de expires_at (Lote M2)."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import delete, select, update

from apps.api.core.database import AsyncSessionLocal
from apps.api.main import app
from apps.api.models import Booking, BookingStatus, Guest, Room


async def _clear_bookings_and_get_room_101() -> tuple[int, int]:
    """Limpia reservas previas, restaura las 9 habitaciones a available y garantiza un huésped de prueba."""
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Booking))
        await session.execute(update(Room).values(status="available", active=True))
        room_res = await session.execute(select(Room).where(Room.number == "101"))
        room = room_res.scalar_one()

        guest_res = await session.execute(
            select(Guest).where(Guest.whatsapp_phone == "+573000000201")
        )
        guest = guest_res.scalar_one_or_none()
        if guest is None:
            guest = Guest(
                whatsapp_phone="+573000000201",
                name="Huésped Disponibilidad M2",
                habeas_data_accepted=True,
            )
            session.add(guest)
            await session.flush()

        guest_id, room_id = guest.id, room.id
        await session.commit()
        return guest_id, room_id


@pytest.mark.asyncio
async def test_availability_calculates_extra_guest_surcharge_and_filters_capacity_rn01() -> None:
    """Verifica que GET /api/v1/rooms/availability aplique recargo por adulto adicional (RN-01) y filtre por capacidad."""
    await _clear_bookings_and_get_room_101()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Para 3 adultos (2 noches): Hab 101 tiene base=2, max=3, precio=120000, extra=20000 -> (120000+20000)*2 = 280000.00
        res = await client.get(
            "/api/v1/rooms/availability",
            params={
                "check_in": "2026-12-10",
                "check_out": "2026-12-12",
                "adults": 3,
                "children": 0,
            },
        )
        assert res.status_code == 200
        rooms = res.json()
        assert len(rooms) == 9
        room_101 = next(r for r in rooms if r["number"] == "101")
        assert room_101["nights"] == 2
        assert room_101["extra_adults"] == 1
        assert Decimal(room_101["total_price"]) == Decimal("280000.00")

        # 2. Para 5 adultos: solo las 3 suites (301, 302, 303 con max_adults_capacity=6) cumplen RN-01
        res_suites = await client.get(
            "/api/v1/rooms/availability",
            params={
                "check_in": "2026-12-10",
                "check_out": "2026-12-12",
                "adults": 5,
            },
        )
        assert res_suites.status_code == 200
        suite_numbers = [r["number"] for r in res_suites.json()]
        assert suite_numbers == ["301", "302", "303"]


@pytest.mark.asyncio
async def test_availability_hides_active_lock_but_ignores_expired_lock_inline_rn02() -> None:
    """Verifica que un bloqueo vigente oculte la habitación, pero si expires_at <= NOW() se ignore dinámicamente en PostgreSQL."""
    guest_id, room_id = await _clear_bookings_and_get_room_101()

    # 1. Insertar bloqueo temporal vigente (+15 min) en Habitación 101
    async with AsyncSessionLocal() as session:
        lock = Booking(
            guest_id=guest_id,
            room_id=room_id,
            check_in=date(2026, 12, 10),
            check_out=date(2026, 12, 12),
            status=BookingStatus.BLOQUEADA_TEMPORAL.value,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
            adults=2,
            total_price=Decimal("240000.00"),
        )
        session.add(lock)
        await session.commit()
        lock_id = lock.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_active = await client.get(
            "/api/v1/rooms/availability",
            params={"check_in": "2026-12-10", "check_out": "2026-12-12", "adults": 2},
        )
        assert res_active.status_code == 200
        numbers_active = [r["number"] for r in res_active.json()]
        assert "101" not in numbers_active
        assert len(numbers_active) == 8

    # 2. Vencer expires_at en BD (-1 minuto) SIN cambiar el status (sigue en BLOQUEADA_TEMPORAL)
    async with AsyncSessionLocal() as session:
        db_lock = await session.get(Booking, lock_id)
        assert db_lock is not None
        db_lock.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        await session.commit()

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_expired = await client.get(
            "/api/v1/rooms/availability",
            params={"check_in": "2026-12-10", "check_out": "2026-12-12", "adults": 2},
        )
        assert res_expired.status_code == 200
        numbers_expired = [r["number"] for r in res_expired.json()]
        assert "101" in numbers_expired
        assert len(numbers_expired) == 9
