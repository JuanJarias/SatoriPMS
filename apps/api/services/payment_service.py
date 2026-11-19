"""Servicio de validación criptográfica HMAC-SHA256, idempotencia y confirmación de pagos (Lote M3)."""

from decimal import Decimal
import hashlib
import hmac
import json
import sys
from typing import Any
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.config import settings
    from models.booking import Booking, BookingStatus
    from services.audit_service import record_audit
except ImportError:
    from apps.api.core.config import settings
    from apps.api.models.booking import Booking, BookingStatus
    from apps.api.services.audit_service import record_audit


def generate_group_code(group_uuid: uuid.UUID | None = None) -> str:
    """Genera un código oficial de reserva con prefijo TS-XXXX (ej. TS-8F3A)."""
    uid = group_uuid or uuid.uuid4()
    suffix = uid.hex[-4:].upper()
    return f"TS-{suffix}"


def verify_webhook_signature(
    raw_body: bytes,
    signature_header: str | None,
    secret: str | None = None,
) -> bool:
    """Valida en tiempo constante la firma HMAC-SHA256 enviada en X-Hub-Signature-256."""
    if not signature_header:
        return False

    webhook_secret = secret if secret is not None else settings.PAYMENT_WEBHOOK_SECRET
    expected_hex = hmac.new(
        webhook_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    clean_received = signature_header.strip()
    if clean_received.lower().startswith("sha256="):
        clean_received = clean_received.split("=", 1)[1].strip()

    return hmac.compare_digest(expected_hex.lower(), clean_received.lower())


async def process_payment_webhook(
    db: AsyncSession,
    raw_body: bytes,
    signature_header: str | None,
) -> dict[str, Any]:
    """Procesa un webhook de pago validando HMAC, garantizando idempotencia y confirmando la reserva."""
    if not verify_webhook_signature(raw_body, signature_header):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma HMAC X-Hub-Signature-256 inválida o ausente",
        )

    try:
        payload: dict[str, Any] = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload JSON malformado en webhook de pagos",
        ) from exc

    payment_id = str(
        payload.get("payment_id")
        or payload.get("transaction_id")
        or ""
    ).strip()
    if not payment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo payment_id es obligatorio",
        )

    # 1. Idempotencia en base de datos: si payment_id ya existe, retornar 200 sin reprocesar
    existing_res = await db.execute(
        select(Booking).where(Booking.payment_id == payment_id)
    )
    existing_booking = existing_res.scalar_one_or_none()
    if existing_booking is not None:
        return {
            "status": "already_processed",
            "idempotent": True,
            "payment_id": payment_id,
            "booking_id": existing_booking.id,
            "group_code": existing_booking.group_code,
            "booking_status": existing_booking.status,
            "payment_status": existing_booking.payment_status,
            "paid_amount": str(existing_booking.paid_amount),
        }

    # 2. Localizar la reserva objetivo por booking_id o group_code / reservation_code
    booking_id = payload.get("booking_id")
    group_code_in = (
        payload.get("group_code")
        or payload.get("reservation_code")
        or payload.get("reference")
    )

    target_booking: Booking | None = None
    if booking_id is not None:
        res = await db.execute(
            select(Booking).where(Booking.id == int(booking_id))
        )
        target_booking = res.scalar_one_or_none()
    elif group_code_in:
        res = await db.execute(
            select(Booking).where(Booking.group_code == str(group_code_in).strip())
        )
        target_booking = res.scalars().first()

    if target_booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva asociada al pago no encontrada",
        )

    # 3. Transicionar de BLOQUEADA_TEMPORAL a CONFIRMADA y asignar código TS-XXXX
    group_uuid = target_booking.reservation_group_id or uuid.uuid4()
    target_booking.reservation_group_id = group_uuid
    group_code = target_booking.group_code or generate_group_code(group_uuid)
    target_booking.group_code = group_code
    if not target_booking.companions:
        target_booking.companions = group_code

    payment_option = str(payload.get("payment_option", "full")).lower()
    raw_amount = payload.get("amount")
    if raw_amount is not None:
        paid_amount = Decimal(str(raw_amount)).quantize(Decimal("0.01"))
    elif payment_option == "deposit":
        paid_amount = (target_booking.total_price / Decimal("2")).quantize(
            Decimal("0.01")
        )
    else:
        paid_amount = target_booking.total_price

    target_booking.status = BookingStatus.CONFIRMADA.value
    target_booking.expires_at = None
    target_booking.payment_id = payment_id
    target_booking.paid_amount = paid_amount
    target_booking.payment_status = (
        "partial" if paid_amount < target_booking.total_price else "paid"
    )

    await record_audit(
        db=db,
        actor="payment_webhook",
        action="PAYMENT_WEBHOOK_CONFIRMED",
        entity="booking",
        entity_id=target_booking.id,
        details={
            "payment_id": payment_id,
            "group_code": group_code,
            "paid_amount": str(paid_amount),
            "payment_status": target_booking.payment_status,
        },
    )
    await db.commit()
    await db.refresh(target_booking)

    return {
        "status": "confirmed",
        "idempotent": False,
        "payment_id": payment_id,
        "booking_id": target_booking.id,
        "group_code": target_booking.group_code,
        "booking_status": target_booking.status,
        "payment_status": target_booking.payment_status,
        "paid_amount": str(target_booking.paid_amount),
    }


sys.modules.setdefault("services.payment_service", sys.modules[__name__])
sys.modules.setdefault("apps.api.services.payment_service", sys.modules[__name__])
