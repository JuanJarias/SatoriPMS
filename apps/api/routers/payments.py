"""Router del webhook de pagos con validación criptográfica HMAC-SHA256 e idempotencia (Lote M3)."""

import sys
from typing import Any

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from services.payment_service import process_payment_webhook
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.services.payment_service import process_payment_webhook

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
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Recibe notificaciones de pasarela, valida X-Hub-Signature-256 con HMAC-SHA256 y confirma la reserva."""
    raw_body = await request.body()
    return await process_payment_webhook(
        db=db,
        raw_body=raw_body,
        signature_header=x_hub_signature_256,
    )


sys.modules.setdefault("routers.payments", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.payments", sys.modules[__name__])
