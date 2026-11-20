"""Router del webhook de pagos con validación HMAC/Wompi e idempotencia y puerto de checkout (Lotes M3 y P4)."""

from decimal import Decimal
import sys
from typing import Any

from fastapi import APIRouter, Body, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from dependencies.auth import require_service_or_role
    from models.user import User, UserRole
    from services.payment_service import get_payment_gateway, process_payment_webhook
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.dependencies.auth import require_service_or_role
    from apps.api.models.user import User, UserRole
    from apps.api.services.payment_service import (
        get_payment_gateway,
        process_payment_webhook,
    )

router = APIRouter(prefix="/api/v1/payments", tags=["Payments & Webhooks"])


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
)
async def payment_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(
        default=None, alias="X-Hub-Signature-256"
    ),
    x_event_checksum: str | None = Header(
        default=None, alias="X-Event-Checksum"
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Recibe notificaciones de pasarela (Wompi/Sandbox), valida firma e idempotencia y confirma la reserva."""
    raw_body = await request.body()
    return await process_payment_webhook(
        db=db,
        raw_body=raw_body,
        signature_header=x_hub_signature_256,
        wompi_checksum_header=x_event_checksum,
    )


@router.post(
    "/checkout-link",
    status_code=status.HTTP_200_OK,
)
async def create_checkout_link(
    body: dict[str, Any] = Body(...),
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
) -> dict[str, Any]:
    """Genera un enlace de pago mediante el puerto de pasarela activo (Sandbox o Wompi)."""
    reference = str(body.get("reference") or body.get("code") or "TS-LOCK").strip()
    amount = Decimal(str(body.get("amount", 0))).quantize(Decimal("0.01"))
    description = str(body.get("description") or f"Reserva Hotel Torre Satori ({reference})")
    redirect_url = body.get("redirectUrl") or body.get("redirect_url")
    gateway = get_payment_gateway()
    return await gateway.create_checkout_link(
        reference=reference,
        amount_cop=amount,
        description=description,
        redirect_url=str(redirect_url) if redirect_url else None,
    )


sys.modules.setdefault("routers.payments", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.payments", sys.modules[__name__])
