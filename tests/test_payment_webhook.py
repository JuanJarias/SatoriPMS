"""Pruebas del webhook de pagos POST /api/v1/payments/webhook: HMAC-SHA256, idempotencia y transición a CONFIRMADA (Lote M3)."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import hmac
import json

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import delete, func, select

from apps.api.core.config import settings
from apps.api.core.database import AsyncSessionLocal
from apps.api.main import app
from apps.api.models import AuditLog, Booking, BookingStatus, Guest, Room


def _sign_payload(raw_bytes: bytes, secret: str | None = None) -> str:
    """Calcula la cabecera X-Hub-Signature-256 válida para un cuerpo JSON en bytes."""
    key = (secret if secret is not None else settings.PAYMENT_WEBHOOK_SECRET).encode("utf-8")
    digest = hmac.new(key, raw_bytes, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


async def _create_locked_booking_for_webhook() -> int:
    """Limpia reservas de la habitación 2 (Familiar) y crea un bloqueo temporal BLOQUEADA_TEMPORAL."""
    async with AsyncSessionLocal() as session:
        room_res = await session.execute(select(Room).where(Room.number == "2"))
        room = room_res.scalar_one()
        await session.execute(delete(Booking).where(Booking.room_id == room.id))

        guest_res = await session.execute(
            select(Guest).where(Guest.whatsapp_phone == "+573000000301")
        )
        guest = guest_res.scalar_one_or_none()
        if guest is None:
            guest = Guest(
                whatsapp_phone="+573000000301",
                document_number="1098765432",
                name="Huésped Webhook M3",
                habeas_data_accepted=True,
            )
            session.add(guest)
            await session.flush()

        booking = Booking(
            guest_id=guest.id,
            room_id=room.id,
            check_in=date(2026, 12, 10),
            check_out=date(2026, 12, 12),
            status=BookingStatus.BLOQUEADA_TEMPORAL.value,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
            payment_status="pending",
            adults=2,
            total_price=Decimal("240000.00"),
            paid_amount=Decimal("0.00"),
        )
        session.add(booking)
        await session.commit()
        return booking.id


@pytest.mark.asyncio
async def test_webhook_rejects_invalid_or_missing_signature_with_401() -> None:
    """Verifica que una firma HMAC inválida o ausente retorne HTTP 401 y no confirme la reserva."""
    booking_id = await _create_locked_booking_for_webhook()
    raw_body = json.dumps(
        {
            "payment_id": "PAY-INVALID-SIG-001",
            "booking_id": booking_id,
            "payment_option": "full",
        }
    ).encode("utf-8")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Sin cabecera X-Hub-Signature-256 -> 401
        res_missing = await client.post("/api/v1/payments/webhook", content=raw_body)
        assert res_missing.status_code == 401

        # 2. Con firma HMAC falsa -> 401
        res_bad = await client.post(
            "/api/v1/payments/webhook",
            content=raw_body,
            headers={"X-Hub-Signature-256": "sha256=0000deadbeef0000"},
        )
        assert res_bad.status_code == 401

    async with AsyncSessionLocal() as session:
        b = await session.get(Booking, booking_id)
        assert b is not None
        assert b.status == BookingStatus.BLOQUEADA_TEMPORAL.value


@pytest.mark.asyncio
async def test_webhook_valid_signature_confirms_booking_and_idempotency_skips_duplicate() -> None:
    """Verifica que firma válida confirme la reserva con código TS-XXXX, audite y que un webhook duplicado retorne 200 sin reprocesar."""
    booking_id = await _create_locked_booking_for_webhook()
    payment_id = f"PAY-WOMPI-OK-{booking_id}"
    raw_body = json.dumps(
        {
            "payment_id": payment_id,
            "booking_id": booking_id,
            "payment_option": "deposit",
        }
    ).encode("utf-8")
    valid_sig = _sign_payload(raw_body)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Primer envío legítimo -> confirma reserva, genera TS-XXXX y audita
        res_first = await client.post(
            "/api/v1/payments/webhook",
            content=raw_body,
            headers={"X-Hub-Signature-256": valid_sig},
        )
        assert res_first.status_code == 200
        data_first = res_first.json()
        assert data_first["status"] == "confirmed"
        assert data_first["idempotent"] is False
        assert data_first["booking_status"] == BookingStatus.CONFIRMADA.value
        assert data_first["group_code"].startswith("TS-")
        assert data_first["payment_status"] == "partial"
        assert Decimal(data_first["paid_amount"]) == Decimal("120000.00")

        # 2. Segundo envío idéntico (reintento de pasarela) -> 200 OK idempotente sin reprocesar
        res_dup = await client.post(
            "/api/v1/payments/webhook",
            content=raw_body,
            headers={"X-Hub-Signature-256": valid_sig},
        )
        assert res_dup.status_code == 200
        data_dup = res_dup.json()
        assert data_dup["status"] == "already_processed"
        assert data_dup["idempotent"] is True
        assert data_dup["group_code"] == data_first["group_code"]

    # Verificar que en audit_log solo se registró 1 evento PAYMENT_WEBHOOK_CONFIRMED para este booking_id
    async with AsyncSessionLocal() as session:
        count_res = await session.execute(
            select(func.count(AuditLog.id)).where(
                AuditLog.action == "PAYMENT_WEBHOOK_CONFIRMED",
                AuditLog.entity_id == str(booking_id),
            )
        )
        assert count_res.scalar_one() == 1
