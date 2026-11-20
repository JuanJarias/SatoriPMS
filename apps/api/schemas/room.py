"""Esquemas Pydantic para consulta de catálogo y disponibilidad de habitaciones (Lote M2)."""

from decimal import Decimal
import sys

from pydantic import BaseModel, ConfigDict


class RoomAvailabilityItem(BaseModel):
    """Habitación disponible con tarifa calculada según noches y recargo RN-01."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    name: str
    description: str | None = None
    type: str
    base_adults_capacity: int
    max_adults_capacity: int
    children_capacity: int
    extra_guest_price: Decimal
    allows_pets: bool
    price_per_night: Decimal
    nights: int
    extra_adults: int
    total_price: Decimal


sys.modules.setdefault("schemas.room", sys.modules[__name__])
sys.modules.setdefault("apps.api.schemas.room", sys.modules[__name__])
