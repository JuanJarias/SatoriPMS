"""Puerto de pasarela de pagos (Wompi + Sandbox), validación criptográfica HMAC/SHA-256 e idempotencia (Lotes M3 y P4)."""

from decimal import Decimal
import hashlib
import hmac
import json
import sys
from typing import Any, Protocol
import uuid

from fastapi import HTTPException, status
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.config import settings
    from models.booking import Booking, BookingStatus
    from services.audit_service import record_audit
    from services.event_bus import publish_pms_event
except ImportError:
    from apps.api.core.config import settings
    from apps.api.models.booking import Booking, BookingStatus
    from apps.api.services.audit_service import record_audit
    from apps.api.services.event_bus import publish_pms_event


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


def verify_wompi_event_checksum(
    payload: dict[str, Any],
    header_checksum: str | None = None,
    events_secret: str | None = None,
) -> bool:
    """Valida el checksum SHA-256 de eventos oficiales de Wompi (propiedades + timestamp + events_secret)."""
    secret = events_secret if events_secret is not None else settings.WOMPI_EVENTS_SECRET
    sig_block = payload.get("signature") if isinstance(payload.get("signature"), dict) else {}
    checksum = (header_checksum or sig_block.get("checksum") or "").strip().lower()
    properties = sig_block.get("properties")
    timestamp = payload.get("timestamp")
    if not secret or not checksum or not isinstance(properties, list) or timestamp is None:
        return False

    data_obj = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    concat_parts: list[str] = []
    for prop_path in properties:
        curr: Any = data_obj
        for part in str(prop_path).split("."):
            if isinstance(curr, dict):
                curr = curr.get(part)
            else:
                curr = None
                break
        if curr is None:
            return False
        concat_parts.append(str(curr))
    concat_parts.append(str(timestamp))
    concat_parts.append(secret)
    expected = hashlib.sha256("".join(concat_parts).encode("utf-8")).hexdigest().lower()
    return hmac.compare_digest(expected, checksum)


class PaymentGatewayPort(Protocol):
    """Puerto hexagonal para generar enlaces de cobro (Sandbox o Wompi)."""

    async def create_checkout_link(
        self,
        reference: str,
        amount_cop: Decimal,
        description: str,
        redirect_url: str | None = None,
    ) -> dict[str, Any]:
        ...


class SandboxPaymentGateway:
    """Adaptador Sandbox local determinista para pruebas y desarrollo sin red."""

    async def create_checkout_link(
        self,
        reference: str,
        amount_cop: Decimal,
        description: str,
        redirect_url: str | None = None,
    ) -> dict[str, Any]:
        link_id = f"sbx_{uuid.uuid4().hex[:10]}"
        return {
            "provider": "sandbox",
            "linkId": link_id,
            "reference": reference,
            "amountCop": float(amount_cop),
            "checkoutUrl": f"https://checkout.wompi.co/l/sandbox-{link_id}?reference={reference}",
            "description": description,
            "redirectUrl": redirect_url,
        }


class WompiPaymentGateway:
    """Adaptador HTTP oficial para Payment Links de Wompi (sandbox o producción)."""

    def _base_url(self) -> str:
        if settings.WOMPI_ENVIRONMENT.lower() == "production":
            return "https://production.wompi.co/v1"
        return "https://sandbox.wompi.co/v1"

    async def create_checkout_link(
        self,
        reference: str,
        amount_cop: Decimal,
        description: str,
        redirect_url: str | None = None,
    ) -> dict[str, Any]:
        if not settings.WOMPI_PRIVATE_KEY:
            return await SandboxPaymentGateway().create_checkout_link(
                reference=reference,
                amount_cop=amount_cop,
                description=description,
                redirect_url=redirect_url,
            )

        amount_in_cents = int((amount_cop * Decimal("100")).quantize(Decimal("1")))
        body: dict[str, Any] = {
            "name": f"Torre Satori · {reference}",
            "description": description,
            "single_use": True,
            "collect_shipping": False,
            "currency": "COP",
            "amount_in_cents": amount_in_cents,
            "sku": reference,
        }
        if redirect_url:
            body["redirect_url"] = redirect_url

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self._base_url()}/payment_links",
                headers={"Authorization": f"Bearer {settings.WOMPI_PRIVATE_KEY}"},
                json=body,
            )
            resp.raise_for_status()
            data = resp.json().get("data") or {}
            link_id = str(data.get("id") or "")
            return {
                "provider": "wompi",
                "linkId": link_id,
                "reference": reference,
                "amountCop": float(amount_cop),
                "checkoutUrl": f"https://checkout.wompi.co/l/{link_id}",
                "description": description,
                "redirectUrl": redirect_url,
            }


def get_payment_gateway() -> PaymentGatewayPort:
    """Resuelve el adaptador activo según PAYMENT_PROVIDER y presencia de WOMPI_PRIVATE_KEY."""
    if settings.PAYMENT_PROVIDER.lower() == "wompi" and settings.WOMPI_PRIVATE_KEY:
        return WompiPaymentGateway()
    return SandboxPaymentGateway()


def _extract_payment_fields(payload: dict[str, Any]) -> tuple[str, int | None, str | None, str, Decimal | None, str]:
    """Normaliza tanto payload interno HMAC como eventos transaction.updated de Wompi."""
    if payload.get("event") == "transaction.updated" and isinstance(payload.get("data"), dict):
        tx = payload["data"].get("transaction") or {}
        payment_id = str(tx.get("id") or "").strip()
        ref = str(tx.get("reference") or "").strip() or None
        tx_status = str(tx.get("status") or "").upper()
        cents = tx.get("amount_in_cents")
        amount = (Decimal(str(cents)) / Decimal("100")).quantize(Decimal("0.01")) if cents is not None else None
        return payment_id, None, ref, "wompi", amount, tx_status

    payment_id = str(payload.get("payment_id") or payload.get("transaction_id") or "").strip()
    booking_id = int(payload["booking_id"]) if payload.get("booking_id") is not None else None
    ref = str(
        payload.get("group_code")
        or payload.get("reservation_code")
        or payload.get("reference")
        or ""
    ).strip() or None
    payment_option = str(payload.get("payment_option", "full")).lower()
    raw_amount = payload.get("amount")
    amount = Decimal(str(raw_amount)).quantize(Decimal("0.01")) if raw_amount is not None else None
    return payment_id, booking_id, ref, payment_option, amount, "APPROVED"


async def process_payment_webhook(
    db: AsyncSession,
    raw_body: bytes,
    signature_header: str | None,
    wompi_checksum_header: str | None = None,
) -> dict[str, Any]:
    """Procesa un webhook de pago validando HMAC o checksum Wompi, garantizando idempotencia y confirmando la reserva."""
    try:
        payload: dict[str, Any] = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        if not verify_webhook_signature(raw_body, signature_header):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firma HMAC X-Hub-Signature-256 inválida o ausente",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload JSON malformado en webhook de pagos",
        ) from exc

    is_hmac_valid = verify_webhook_signature(raw_body, signature_header)
    is_wompi_valid = verify_wompi_event_checksum(payload, wompi_checksum_header)
    if not (is_hmac_valid or is_wompi_valid):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma HMAC X-Hub-Signature-256 o checksum Wompi inválido o ausente",
        )

    payment_id, booking_id, group_code_in, payment_option, parsed_amount, tx_status = _extract_payment_fields(payload)
    if not payment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo payment_id es obligatorio",
        )

    if tx_status != "APPROVED":
        return {"status": "ignored", "tx_status": tx_status, "payment_id": payment_id}

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

    # 2. Localizar la reserva objetivo por booking_id o group_code / reference
    target_booking: Booking | None = None
    if booking_id is not None:
        res = await db.execute(select(Booking).where(Booking.id == booking_id))
        target_booking = res.scalar_one_or_none()
    elif group_code_in:
        res = await db.execute(
            select(Booking).where(Booking.group_code == group_code_in)
        )
        target_booking = res.scalars().first()
        if target_booking is None and group_code_in.isdigit():
            target_booking = await db.get(Booking, int(group_code_in))

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

    if parsed_amount is not None:
        paid_amount = parsed_amount
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

    publish_pms_event(
        "booking.confirmed",
        {"bookingId": target_booking.id, "code": group_code},
    )

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
