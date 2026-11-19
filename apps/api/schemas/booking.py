"""Esquemas Pydantic para solicitud y respuesta de bloqueo temporal de 15 minutos (Lote M2)."""

from datetime import date, datetime
from decimal import Decimal
import sys

from pydantic import BaseModel, Field


class LockRequest(BaseModel):
    """Payload de entrada para crear un bloqueo temporal atómico (RN-01, RN-02, RN-12)."""

    room_id: int = Field(..., ge=1, description="ID de la habitación a bloquear")
    check_in: date
    check_out: date
    adults: int = Field(default=2, ge=1)
    children: int = Field(default=0, ge=0)
    with_pet: bool = False
    guest_name: str = Field(default="Huésped Torre Satori", min_length=1, max_length=100)
    whatsapp_phone: str | None = Field(default=None, max_length=20)
    document_number: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=100)
    habeas_data_accepted: bool = Field(
        default=False,
        description="Consentimiento obligatorio de tratamiento de datos personales (Ley 1581 / RN-12)",
    )
    source: str = Field(default="chatbot", pattern="^(chatbot|web)$")


class LockResponse(BaseModel):
    """Respuesta exitosa tras adquirir el candado GiST por 15 minutos en PostgreSQL 16."""

    booking_id: int
    room_id: int
    room_number: str
    status: str
    check_in: date
    check_out: date
    nights: int
    adults: int
    children: int
    extra_adults: int
    total_price: Decimal
    expires_at: datetime


class UnlockRequest(BaseModel):
    """Solicitud para liberar manualmente un bloqueo temporal antes de su vencimiento."""

    booking_id: int = Field(..., ge=1)


class UnlockResponse(BaseModel):
    """Confirmación de liberación de bloqueo temporal."""

    booking_id: int
    status: str


sys.modules.setdefault("schemas.booking", sys.modules[__name__])
sys.modules.setdefault("apps.api.schemas.booking", sys.modules[__name__])
