"""Pruebas de operación web con RBAC JWT, check-in/out auditado, CRUD habitaciones (TC-02), Salgados Café (TC-03), Eventos (TC-04) y Reseñas."""

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import delete, select

from apps.api.core.database import AsyncSessionLocal
from apps.api.main import app
from apps.api.models import AuditLog, Booking, BookingStatus, Room


async def _login_headers(client: AsyncClient, username: str, password: str) -> dict[str, str]:
    res = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.mark.asyncio
async def test_web_booking_creation_checkin_en_curso_and_checkout_with_audit() -> None:
    """Verifica creación de reserva manual con JWT, transición a EN_CURSO en check-in con audit_log y liquidación en check-out."""
    async with AsyncSessionLocal() as session:
        room_res = await session.execute(select(Room).where(Room.number == "4"))
        room = room_res.scalar_one()
        room.status = "available"
        room.active = True
        await session.execute(delete(Booking).where(Booking.room_id == room.id))
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 0. Endpoints demo abiertos deben estar retirados (404) y las rutas operativas exigen JWT (401)
        removed_res = await client.post("/api/bookings/test-paid", json={})
        assert removed_res.status_code == 404
        unauth_res = await client.get("/api/v1/bookings")
        assert unauth_res.status_code == 401

        recep_headers = await _login_headers(client, "recepcion", "recepcion123")

        # 1. Crear reserva desde recepción web autenticada (POST /api/v1/bookings/manual)
        create_res = await client.post(
            "/api/v1/bookings/manual",
            headers=recep_headers,
            json={
                "rooms": [
                    {
                        "roomId": room.id,
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

        # 2. Check-in manual en mostrador -> pasa a EN_CURSO y registra actor real en audit_log
        checkin_res = await client.post(
            f"/api/v1/bookings/{booking_id}/check-in",
            headers=recep_headers,
        )
        assert checkin_res.status_code == 200
        assert checkin_res.json()["status"] == BookingStatus.EN_CURSO.value

        # 3. Check-out manual -> liquida cuenta y marca habitación en limpieza
        checkout_res = await client.post(
            f"/api/v1/bookings/{booking_id}/check-out",
            headers=recep_headers,
        )
        assert checkout_res.status_code == 200
        assert checkout_res.json()["paymentStatus"] == "paid"

        # Recepción sí puede restaurar estado operativo vía PATCH /status
        patch_res = await client.patch(
            f"/api/v1/rooms/{room.id}/status",
            headers=recep_headers,
            json={"status": "available"},
        )
        assert patch_res.status_code == 200

    async with AsyncSessionLocal() as session:
        audit_res = await session.execute(
            select(AuditLog)
            .where(AuditLog.action == "BOOKING_CHECK_IN")
            .order_by(AuditLog.id.desc())
        )
        latest = audit_res.scalars().first()
        assert latest is not None
        assert latest.actor_username == "recepcion"


@pytest.mark.asyncio
async def test_room_crud_and_delete_protection_when_booking_active_tc02() -> None:
    """Verifica RBAC Admin vs Recepción, actualización dinámica de tarifa y bloqueo HTTP 409 al borrar con reserva activa (TC-02)."""
    async with AsyncSessionLocal() as session:
        room_res = await session.execute(select(Room).where(Room.number == "5"))
        room = room_res.scalar_one()
        room.active = True
        await session.execute(delete(Booking).where(Booking.room_id == room.id))
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        recep_headers = await _login_headers(client, "recepcion", "recepcion123")
        admin_headers = await _login_headers(client, "admin", "admin123")

        # 0. Recepcionista no puede editar tarifas ni eliminar habitaciones -> 403 Forbidden
        forbidden_upd = await client.put(
            f"/api/v1/rooms/{room.id}",
            headers=recep_headers,
            json={"pricePerNight": 385000},
        )
        assert forbidden_upd.status_code == 403
        forbidden_del = await client.delete(
            f"/api/v1/rooms/{room.id}",
            headers=recep_headers,
        )
        assert forbidden_del.status_code == 403

        # 1. Administrador sí actualiza tarifa de Hab 5 (Suite Satori)
        upd_res = await client.put(
            f"/api/v1/rooms/{room.id}",
            headers=admin_headers,
            json={"pricePerNight": 385000, "status": "available"},
        )
        assert upd_res.status_code == 200
        assert upd_res.json()["pricePerNight"] == 385000.0

        # 2. Crear una reserva activa en Hab 5
        await client.post(
            "/api/v1/bookings/manual",
            headers=recep_headers,
            json={
                "rooms": [{"roomId": room.id, "checkIn": "2026-12-15", "checkOut": "2026-12-17"}],
                "guest": {"name": "Huésped Activo TC02"},
            },
        )

        # 3. Intentar eliminar Hab 5 mientras tiene reserva activa -> 409 Conflict (candado de borrado TC-02)
        del_res = await client.delete(f"/api/v1/rooms/{room.id}", headers=admin_headers)
        assert del_res.status_code == 409
        assert "TC-02" in del_res.json()["detail"]

        # Restaurar precio original de Hab 5
        await client.put(
            f"/api/v1/rooms/{room.id}",
            headers=admin_headers,
            json={"pricePerNight": 380000},
        )


@pytest.mark.asyncio
async def test_salgados_cafe_order_to_folio_tc03_events_tc04_and_reviews() -> None:
    """Verifica TC-03 (Salgados Café al folio), TC-04 (eventos solo Admin con 10% descuento) y resumen de reseñas."""
    async with AsyncSessionLocal() as session:
        room_res = await session.execute(select(Room).where(Room.number == "6"))
        room = room_res.scalar_one()
        await session.execute(delete(Booking).where(Booking.room_id == room.id))
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        recep_headers = await _login_headers(client, "recepcion", "recepcion123")
        admin_headers = await _login_headers(client, "admin", "admin123")

        # Crear reserva activa en Hab 6 Cafetal (2 noches x $220.000 = $440.000)
        b_res = await client.post(
            "/api/v1/bookings/manual",
            headers=recep_headers,
            json={
                "rooms": [{"roomId": room.id, "checkIn": "2026-12-18", "checkOut": "2026-12-20"}],
                "guest": {"name": "Huésped Salgados TC03"},
            },
        )
        assert b_res.status_code == 200
        booking_id = b_res.json()["bookingIds"][0]

        # 1. TC-03: Cargar pedido de Salgados Café ($18.000 x 2 = $36.000) al folio de Hab 6 -> consolidado $476.000
        order_res = await client.post(
            "/api/v1/restaurant/orders",
            headers=recep_headers,
            json={
                "roomNumber": "6",
                "bookingId": booking_id,
                "items": [{"name": "Desayuno Típico Vallecaucano", "price": 18000, "qty": 2}],
            },
        )
        assert order_res.status_code == 200
        assert order_res.json()["orderTotal"] == 36000.0
        assert order_res.json()["consolidatedFolioTotal"] == 476000.0

        # 2. TC-04: Recepcionista no puede crear eventos (403); Administrador sí (200)
        forbidden_ev = await client.post(
            "/api/v1/events",
            headers=recep_headers,
            json={"name": "No autorizado", "discountPercentage": 10},
        )
        assert forbidden_ev.status_code == 403

        ev_res = await client.post(
            "/api/v1/events",
            headers=admin_headers,
            json={
                "name": "Feria del Café Sevilla",
                "discountPercentage": 10,
                "baseAmount": 240000,
            },
        )
        assert ev_res.status_code == 200
        assert ev_res.json()["discountedTotal"] == 216000.0

        # 3. Resumen de reseñas para Resenas.tsx (requiere JWT)
        rev_unauth = await client.get("/api/v1/reviews/summary")
        assert rev_unauth.status_code == 401
        rev_res = await client.get("/api/v1/reviews/summary", headers=recep_headers)
        assert rev_res.status_code == 200
        assert rev_res.json()["total"] >= 3
        assert rev_res.json()["average"] == 5.0
