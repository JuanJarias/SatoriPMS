"""Pruebas del endpoint POST /api/v1/bookings/lock: RN-01, RN-12, expiración atómica y concurrencia HTTP 409 (Lote M2)."""

import asyncio
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import delete, select

from apps.api.core.database import AsyncSessionLocal
from apps.api.main import app
from apps.api.models import Booking, BookingStatus, Guest, Room


async def _prepare_room_101() -> tuple[int, int]:
    """Limpia reservas de la habitación 101 y retorna (guest_id, room_id)."""
    async with AsyncSessionLocal() as session:
        room_res = await session.execute(select(Room).where(Room.number == "101"))
        room = room_res.scalar_one()
        await session.execute(delete(Booking).where(Booking.room_id == room.id))

        guest_res = await session.execute(
            select(Guest).where(Guest.whatsapp_phone == "+573000000202")
        )
        guest = guest_res.scalar_one_or_none()
        if guest is None:
            guest = Guest(
                whatsapp_phone="+573000000202",
                name="Huésped Candado M2",
                habeas_data_accepted=True,
            )
            session.add(guest)
            await session.flush()

        guest_id, room_id = guest.id, room.id
        await session.commit()
        return guest_id, room_id


@pytest.mark.asyncio
async def test_lock_validates_ley_1581_rn12_and_capacity_rn01() -> None:
    """Verifica que POST /api/v1/bookings/lock rechace sin consentimiento Ley 1581 (RN-12) o si excede capacidad (RN-01)."""
    _, room_id = await _prepare_room_101()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Sin consentimiento Ley 1581 (habeas_data_accepted = False) -> 400 Bad Request
        res_no_consent = await client.post(
            "/api/v1/bookings/lock",
            json={
                "room_id": room_id,
                "check_in": "2026-12-15",
                "check_out": "2026-12-18",
                "adults": 2,
                "habeas_data_accepted": False,
            },
        )
        assert res_no_consent.status_code == 400
        assert "1581" in res_no_consent.json()["detail"]

        # 2. Excediendo capacidad máxima de Hab 101 (max_adults_capacity=3, enviamos adults=4) -> 400 Bad Request
        res_overflow = await client.post(
            "/api/v1/bookings/lock",
            json={
                "room_id": room_id,
                "check_in": "2026-12-15",
                "check_out": "2026-12-18",
                "adults": 4,
                "habeas_data_accepted": True,
            },
        )
        assert res_overflow.status_code == 400
        assert "RN-01" in res_overflow.json()["detail"]


@pytest.mark.asyncio
async def test_lock_atomically_expires_past_lock_and_creates_new_15m_lock() -> None:
    """Verifica que antes de insertar, POST /api/v1/bookings/lock expire atómicamente candados vencidos de esa habitación."""
    guest_id, room_id = await _prepare_room_101()

    # Insertar un bloqueo temporal ya vencido hace 2 minutos en las mismas fechas
    async with AsyncSessionLocal() as session:
        expired_lock = Booking(
            guest_id=guest_id,
            room_id=room_id,
            check_in=date(2026, 12, 15),
            check_out=date(2026, 12, 18),
            status=BookingStatus.BLOQUEADA_TEMPORAL.value,
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=2),
            adults=2,
            total_price=Decimal("360000.00"),
        )
        session.add(expired_lock)
        await session.commit()
        old_lock_id = expired_lock.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v1/bookings/lock",
            json={
                "room_id": room_id,
                "check_in": "2026-12-15",
                "check_out": "2026-12-18",
                "adults": 3,
                "children": 1,
                "guest_name": "Nuevo Huésped",
                "whatsapp_phone": "+573109998877",
                "habeas_data_accepted": True,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == BookingStatus.BLOQUEADA_TEMPORAL.value
        assert data["extra_adults"] == 1
        assert Decimal(data["total_price"]) == Decimal("420000.00")

    # Confirmar en PostgreSQL que el bloqueo viejo pasó a EXPIRADA en la misma transacción
    async with AsyncSessionLocal() as session:
        old_row = await session.get(Booking, old_lock_id)
        assert old_row is not None
        assert old_row.status == BookingStatus.EXPIRADA.value


@pytest.mark.asyncio
async def test_concurrent_http_lock_requests_return_one_200_and_nine_409() -> None:
    """Lanza 10 peticiones HTTP POST /api/v1/bookings/lock simultáneas; exactamente 1 retorna 200 y 9 retornan 409 Conflict."""
    _, room_id = await _prepare_room_101()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:

        async def send_lock(i: int) -> int:
            response = await client.post(
                "/api/v1/bookings/lock",
                json={
                    "room_id": room_id,
                    "check_in": "2026-12-20",
                    "check_out": "2026-12-23",
                    "adults": 2,
                    "guest_name": f"Concurrente {i}",
                    "whatsapp_phone": f"+5731500000{i:02d}",
                    "habeas_data_accepted": True,
                },
            )
            return response.status_code

        statuses = await asyncio.gather(*(send_lock(i) for i in range(10)))

    assert statuses.count(200) == 1
    assert statuses.count(409) == 9
