"""Reglas portadas del servidor anterior: documento del titular, código TS-XXXX aleatorio,
pago externo, precios por noche con eventos especiales y listado de monitoreo."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import delete, select

from apps.api.core.config import settings
from apps.api.core.database import AsyncSessionLocal
from apps.api.main import app
from apps.api.models import Booking, Room
from apps.api.models.operations import SpecialEvent
from apps.api.services.payment_service import generate_group_code
from apps.api.services.pricing import (
    average_multiplier,
    nightly_multipliers,
    room_stay_total,
)

_SVC = {"X-Service-Key": settings.N8N_INTERNAL_API_KEY}
_NIGHTLY = Decimal("100000")
_NOT_FOUND = "No se encontró una reserva con ese código y documento"


def _event(start: date, end: date, discount: float, active: bool = True):
    return SimpleNamespace(
        start_date=start,
        end_date=end,
        discount_percentage=Decimal(str(discount)),
        active=active,
    )


# ── Precios por noche (regla provisional, pendiente de confirmar con el cliente) ──


def test_without_events_every_night_keeps_base_price() -> None:
    m = nightly_multipliers(date(2026, 12, 1), date(2026, 12, 4), [])
    assert len(m) == 3
    assert room_stay_total(_NIGHTLY, m) == Decimal("300000.00")


def test_surcharge_only_applies_to_nights_inside_the_event() -> None:
    # Recargo del 20% (descuento negativo) desde el 20 de diciembre; noches 18, 19, 20 y 21.
    m = nightly_multipliers(date(2026, 12, 18), date(2026, 12, 22), [_event(date(2026, 12, 20), date(2027, 1, 10), -20)])
    assert room_stay_total(_NIGHTLY, m) == Decimal("440000.00")


def test_discount_applies_and_event_end_date_is_inclusive() -> None:
    m = nightly_multipliers(date(2026, 11, 21), date(2026, 11, 24), [_event(date(2026, 11, 15), date(2026, 11, 22), 15)])
    assert room_stay_total(_NIGHTLY, m) == Decimal("270000.00")


def test_overlapping_events_combine_and_inactive_are_ignored() -> None:
    events = [
        _event(date(2026, 12, 1), date(2026, 12, 31), 10),
        _event(date(2026, 12, 1), date(2026, 12, 31), -25),
        _event(date(2026, 12, 1), date(2026, 12, 31), 50, active=False),
    ]
    m = nightly_multipliers(date(2026, 12, 5), date(2026, 12, 6), events)
    assert room_stay_total(_NIGHTLY, m) == Decimal("115000.00")
    assert average_multiplier(m) == Decimal("1.15")


def test_multiplier_never_goes_below_zero() -> None:
    events = [_event(date(2026, 12, 1), date(2026, 12, 31), 80), _event(date(2026, 12, 1), date(2026, 12, 31), 50)]
    m = nightly_multipliers(date(2026, 12, 5), date(2026, 12, 6), events)
    assert room_stay_total(_NIGHTLY, m) == Decimal("0.00")


def test_group_code_is_random_and_uses_unambiguous_alphabet() -> None:
    codes = {generate_group_code() for _ in range(200)}
    assert len(codes) > 150
    for code in codes:
        assert code.startswith("TS-") and len(code) == 7
        assert not set(code[3:]) & set("01OI")


# ── Flujo del chatbot con documento, pago externo y eventos ──────────────────────


async def _prepare_room_three() -> int:
    async with AsyncSessionLocal() as session:
        room = (await session.execute(select(Room).where(Room.number == "3"))).scalar_one()
        await session.execute(delete(Booking).where(Booking.room_id == room.id))
        await session.execute(delete(SpecialEvent))
        await session.commit()
        return room.id


async def _create_pending(client: AsyncClient, room_id: int, document: str, check_in: str, check_out: str) -> dict:
    lock = await client.post(
        "/api/bookings/lock",
        json={"waId": "573120001111", "roomId": room_id, "checkIn": check_in, "checkOut": check_out},
    )
    assert lock.status_code == 200
    res = await client.post(
        "/api/bookings/confirm",
        json={
            "waId": "573120001111",
            "guestName": "Titular Prueba",
            "guestDocument": document,
            "companions": "Camila Soto",
            "checkIn": check_in,
            "checkOut": check_out,
            "adults": 2,
            "rooms": [{"roomId": room_id, "lockToken": lock.json()["lockToken"]}],
            "paymentOption": "deposit",
        },
    )
    assert res.status_code == 200
    return res.json()


@pytest.mark.asyncio
async def test_holder_document_is_verified_and_masked_for_the_chatbot() -> None:
    room_id = await _prepare_room_three()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=_SVC) as client:
        data = await _create_pending(client, room_id, "1094555666", "2027-02-10", "2027-02-12")
        code = data["code"]

        # Sin documento: el chatbot recibe 400
        assert (await client.get(f"/api/bookings/group/{code}")).status_code == 400
        assert (await client.post(f"/api/bookings/group/{code}/cancellation")).status_code == 400

        # Documento equivocado: responde igual que si la reserva no existiera
        bad = await client.get(f"/api/bookings/group/{code}", headers={"X-Guest-Document": "999"})
        missing = await client.get("/api/bookings/group/TS-ZZZZ", headers={"X-Guest-Document": "999"})
        assert bad.status_code == missing.status_code == 404
        assert bad.json()["detail"] == missing.json()["detail"] == _NOT_FOUND
        wrong_cancel = await client.post(f"/api/bookings/group/{code}/cancellation", json={"document": "999"})
        assert wrong_cancel.status_code == 404

        # Documento correcto (aunque venga con puntos): se devuelve enmascarado
        ok = await client.get(f"/api/bookings/group/{code}", headers={"X-Guest-Document": "1.094.555.666"})
        assert ok.status_code == 200
        assert ok.json()["guestDocument"] == "******5666"
        assert ok.json()["companions"] == "Camila Soto"
        assert ok.json()["status"] == "pending_payment"

        # La búsqueda es exacta: un prefijo del código no encuentra nada
        partial = await client.get(f"/api/bookings/group/{code[:5]}", headers={"X-Guest-Document": "1094555666"})
        assert partial.status_code == 404


@pytest.mark.asyncio
async def test_external_payment_confirms_the_pending_booking_and_is_idempotent() -> None:
    room_id = await _prepare_room_three()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=_SVC) as client:
        data = await _create_pending(client, room_id, "1094555666", "2027-03-10", "2027-03-12")
        code = data["code"]
        assert data["status"] == "pending_payment" and data["paidAmount"] == 0.0

        first = await client.post(
            f"/api/bookings/group/{code}/confirm-external-payment",
            json={"paymentOption": "deposit", "transactionId": "txn-idem-1"},
        )
        assert first.status_code == 200
        assert first.json()["status"] == "confirmed"
        assert first.json()["paymentStatus"] == "partial"
        assert first.json()["paidAmount"] == data["totalPrice"] / 2

        again = await client.post(
            f"/api/bookings/group/{code}/confirm-external-payment",
            json={"paymentOption": "deposit", "transactionId": "txn-idem-1"},
        )
        assert again.status_code == 200 and again.json()["idempotent"] is True

        by_body = await client.post(
            "/api/bookings/confirm-external-payment",
            json={"reservationCode": code, "paymentOption": "full", "transactionId": "txn-idem-2"},
        )
        assert by_body.status_code == 200 and by_body.json()["paymentStatus"] == "paid"

    anonymous = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    async with anonymous as client:
        denied = await client.post(f"/api/bookings/group/{code}/confirm-external-payment", json={})
        assert denied.status_code == 401


@pytest.mark.asyncio
async def test_pending_payment_holds_the_room() -> None:
    room_id = await _prepare_room_three()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=_SVC) as client:
        await _create_pending(client, room_id, "1094555666", "2027-04-10", "2027-04-12")
        other = await client.post(
            "/api/bookings/lock",
            json={"waId": "573120002222", "roomId": room_id, "checkIn": "2027-04-11", "checkOut": "2027-04-13"},
        )
        assert other.status_code == 409


@pytest.mark.asyncio
async def test_special_events_adjust_the_quote_and_the_booking_per_night() -> None:
    room_id = await _prepare_room_three()
    async with AsyncSessionLocal() as session:
        room = await session.get(Room, room_id)
        nightly = room.price_per_night
        session.add(
            SpecialEvent(
                name="Temporada alta",
                start_date=date(2027, 5, 3),
                end_date=date(2027, 5, 10),
                discount_percentage=Decimal("-20.00"),  # negativo = recargo del 20%
                active=True,
            )
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=_SVC) as client:
        # Estadía del 1 al 5 de mayo: noches 1 y 2 sin recargo; 3 y 4 con +20%
        avail = await client.get(
            "/api/rooms/availability",
            params={"checkIn": "2027-05-01", "checkOut": "2027-05-05", "adults": 2},
        )
        quote = next(r for r in avail.json() if r["id"] == room_id)
        expected = float(nightly * 2 + nightly * Decimal("1.2") * 2)
        assert quote["totalPrice"] == pytest.approx(expected)

        data = await _create_pending(client, room_id, "1094555666", "2027-05-01", "2027-05-05")
        assert data["totalPrice"] == pytest.approx(expected)

    async with AsyncSessionLocal() as session:
        await session.execute(delete(SpecialEvent))
        await session.commit()


@pytest.mark.asyncio
async def test_debug_listing_uses_the_n8n_status_contract() -> None:
    room_id = await _prepare_room_three()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=_SVC) as client:
        data = await _create_pending(client, room_id, "1094555666", "2027-06-10", "2027-06-12")
        rows = (await client.get("/api/bookings/debug")).json()
        row = next(r for r in rows if r["bookingCode"] == data["code"])
        assert row["status"] == "pending_payment"
        assert row["paymentStatus"] == "pending"
        assert row["guestDocument"] == "1094555666"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as anon:
        assert (await anon.get("/api/bookings/debug")).status_code == 401
        login_rec = await anon.post(
            "/api/v1/auth/login",
            json={"username": "recepcion", "password": "recepcion123"},
        )
        rec_hdrs = {"Authorization": f"Bearer {login_rec.json()['access_token']}"}
        assert (await anon.get("/api/bookings/debug", headers=rec_hdrs)).status_code == 403


@pytest.mark.asyncio
async def test_pending_payment_has_24h_expiration_and_frees_room_when_stale() -> None:
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import update
    from apps.api.models import Booking
    from apps.api.services.expiration_service import expire_stale_booking_locks

    room_id = await _prepare_room_three()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=_SVC) as client:
        data = await _create_pending(client, room_id, "1094555666", "2027-07-10", "2027-07-12")
        code = data["code"]
        debug_rows = (await client.get("/api/bookings/debug")).json()
        row = next(r for r in debug_rows if r["bookingCode"] == code)
        assert row["expiresAt"] is not None

        # Simular vencimiento de las 24 h del link Wompi
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Booking)
                .where(Booking.group_code == code)
                .values(expires_at=datetime.now(timezone.utc) - timedelta(minutes=1))
            )
            await session.commit()

        # Al correr el job, la reserva PENDIENTE_PAGO pasa a EXPIRADA y libera la habitación
        expired = await expire_stale_booking_locks()
        assert any(item["bookingCode"] == code and item["previousStatus"] == "PENDIENTE_PAGO" for item in expired)

        avail = await client.get(
            "/api/rooms/availability",
            params={"checkIn": "2027-07-10", "checkOut": "2027-07-12", "adults": 2},
        )
        assert any(r["id"] == room_id for r in avail.json())
