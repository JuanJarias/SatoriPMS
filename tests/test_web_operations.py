"""Pruebas del Lote M4: Check-in/Check-out con auditoría, CRUD Habitaciones (TC-02), Salgados Café (TC-03), Eventos (TC-04) y Reseñas."""

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import delete, select

from apps.api.core.database import AsyncSessionLocal
from apps.api.main import app
from apps.api.models import AuditLog, Booking, BookingStatus, Room


@pytest.mark.asyncio
async def test_web_booking_creation_checkin_en_curso_and_checkout_with_audit() -> None:
    """Verifica creación de reserva desde web, transición a EN_CURSO en check-in con audit_log y liquidación en check-out."""
    async with AsyncSessionLocal() as session:
        room_res = await session.execute(select(Room).where(Room.number == "201"))
        room = room_res.scalar_one()
        room.status = "available"
        room.active = True
        await session.execute(delete(Booking).where(Booking.room_id == room.id))
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Crear reserva desde recepción web (POST /api/bookings/test-paid)
        create_res = await client.post(
            "/api/bookings/test-paid",
            json={
                "rooms": [
                    {
                        "roomId": 201,
                        "checkIn": "2026-12-10",
                        "checkOut": "2026-12-12",
                    }
                ],
                "guest": {
                    "name": "Laura Gómez",
                    "phone": "+573105551122",
                    "documentNumber": "1090807060",
                },
                "companions": "TS-2041",
            },
        )
        assert create_res.status_code == 200
        booking_id = create_res.json()["bookingIds"][0]
        assert create_res.json()["status"] == BookingStatus.CONFIRMADA.value

        # 2. Check-in manual en mostrador -> pasa a EN_CURSO y registra en audit_log
        checkin_res = await client.post(f"/api/v1/bookings/{booking_id}/check-in")
        assert checkin_res.status_code == 200
        assert checkin_res.json()["status"] == BookingStatus.EN_CURSO.value

        # 3. Check-out manual -> liquida cuenta y marca habitación en limpieza
        checkout_res = await client.post(f"/api/v1/bookings/{booking_id}/check-out")
        assert checkout_res.status_code == 200
        assert checkout_res.json()["paymentStatus"] == "paid"

    async with AsyncSessionLocal() as session:
        audit_res = await session.execute(
            select(AuditLog)
            .where(AuditLog.action == "BOOKING_CHECK_IN")
            .order_by(AuditLog.id.desc())
        )
        assert audit_res.scalars().first() is not None


@pytest.mark.asyncio
async def test_room_crud_and_delete_protection_when_booking_active_tc02() -> None:
    """Verifica TC-02: actualización dinámica de precio base de habitación y bloqueo HTTP 409 al intentar borrar con reserva activa."""
    async with AsyncSessionLocal() as session:
        room_res = await session.execute(select(Room).where(Room.number == "202"))
        room = room_res.scalar_one()
        room.active = True
        await session.execute(delete(Booking).where(Booking.room_id == room.id))
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Actualizar tarifa de Hab 202
        upd_res = await client.put(
            "/api/rooms/202",
            json={"pricePerNight": 165000, "status": "available"},
        )
        assert upd_res.status_code == 200
        assert upd_res.json()["pricePerNight"] == 165000.0

        # 2. Crear una reserva activa en Hab 202
        await client.post(
            "/api/bookings/test-paid",
            json={
                "rooms": [{"roomId": 202, "checkIn": "2026-12-15", "checkOut": "2026-12-17"}],
                "guest": {"name": "Huésped Activo TC02"},
            },
        )

        # 3. Intentar eliminar Hab 202 mientras tiene reserva activa -> 409 Conflict (candado de borrado TC-02)
        del_res = await client.delete("/api/rooms/202")
        assert del_res.status_code == 409
        assert "TC-02" in del_res.json()["detail"]

        # Restaurar precio original de Hab 202
        await client.put("/api/rooms/202", json={"pricePerNight": 160000})


@pytest.mark.asyncio
async def test_salgados_cafe_order_to_folio_tc03_events_tc04_and_reviews() -> None:
    """Verifica TC-03 (pedido Salgados Café cargado al folio), TC-04 (descuento 10% feria turística) y resumen de reseñas."""
    async with AsyncSessionLocal() as session:
        room_res = await session.execute(select(Room).where(Room.number == "203"))
        room = room_res.scalar_one()
        await session.execute(delete(Booking).where(Booking.room_id == room.id))
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Crear reserva activa en Hab 203 (2 noches x $160.000 = $320.000)
        b_res = await client.post(
            "/api/bookings/test-paid",
            json={
                "rooms": [{"roomId": 203, "checkIn": "2026-12-18", "checkOut": "2026-12-20"}],
                "guest": {"name": "Huésped Salgados TC03"},
            },
        )
        assert b_res.status_code == 200
        booking_id = b_res.json()["bookingIds"][0]

        # 1. TC-03: Cargar pedido de Salgados Café ($18.000 x 2 = $36.000) al folio de Hab 203 -> consolidado $356.000
        order_res = await client.post(
            "/api/restaurant/orders",
            json={
                "roomNumber": "203",
                "bookingId": booking_id,
                "items": [{"name": "Desayuno Típico Vallecaucano", "price": 18000, "qty": 2}],
            },
        )
        assert order_res.status_code == 200
        assert order_res.json()["orderTotal"] == 36000.0
        assert order_res.json()["consolidatedFolioTotal"] == 356000.0

        # 2. TC-04: Evento de feria turística con 10% de descuento sobre $240.000 -> $216.000
        ev_res = await client.post(
            "/api/events",
            json={
                "name": "Feria del Café Sevilla",
                "discountPercentage": 10,
                "baseAmount": 240000,
            },
        )
        assert ev_res.status_code == 200
        assert ev_res.json()["discountedTotal"] == 216000.0

        # 3. Resumen de reseñas para Resenas.tsx
        rev_res = await client.get("/api/reviews/summary")
        assert rev_res.status_code == 200
        assert rev_res.json()["total"] >= 3
        assert rev_res.json()["average"] == 5.0
