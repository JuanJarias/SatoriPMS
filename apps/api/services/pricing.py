"""Tarifas por noche con eventos especiales (descuentos y recargos).

Regla provisional, pendiente de confirmar con el cliente: cada noche de la estadía se
multiplica por ``1 - Σ descuentos + Σ recargos`` de los eventos activos que cubren esa
noche (las fechas de inicio y fin son inclusivas), con piso en 0. El recargo por
persona adicional se escala con el multiplicador promedio de la estadía.

``SpecialEvent.discount_percentage`` es firmado: un valor positivo es un descuento y uno
negativo es un recargo (así lo captura la pantalla de eventos de la aplicación web).
Alternativa a evaluar con el cliente: aplicar el primer evento a toda la estadía.
"""

from collections.abc import Iterable
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
import sys
from typing import Protocol

_HUNDRED = Decimal("100")
_CENT = Decimal("0.01")


class EventLike(Protocol):
    """Campos mínimos de un evento especial para calcular tarifas."""

    start_date: date
    end_date: date
    discount_percentage: Decimal
    active: bool


def nightly_multipliers(
    check_in: date,
    check_out: date,
    events: Iterable[EventLike] | None,
) -> list[Decimal]:
    """Multiplicador de tarifa de cada noche de la estadía (de check_in a check_out sin incluirlo)."""
    active_events = [e for e in (events or []) if e.active]
    multipliers: list[Decimal] = []
    night = check_in
    while night < check_out:
        net_discount = Decimal("0")
        for event in active_events:
            if event.start_date <= night <= event.end_date:
                net_discount += Decimal(str(event.discount_percentage))
        multiplier = Decimal("1") - (net_discount / _HUNDRED)
        multipliers.append(max(multiplier, Decimal("0")))
        night += timedelta(days=1)
    return multipliers


def room_stay_total(price_per_night: Decimal, multipliers: list[Decimal]) -> Decimal:
    """Total de alojamiento de una habitación sumando cada noche con su multiplicador."""
    total = sum((price_per_night * m for m in multipliers), Decimal("0"))
    return total.quantize(_CENT, rounding=ROUND_HALF_UP)


def average_multiplier(multipliers: list[Decimal]) -> Decimal:
    """Multiplicador promedio de la estadía (1 si no hay noches)."""
    if not multipliers:
        return Decimal("1")
    return sum(multipliers, Decimal("0")) / Decimal(len(multipliers))


def extra_guest_total(
    extra_guest_price: Decimal,
    extra_adults: int,
    multipliers: list[Decimal],
) -> Decimal:
    """Recargo por adultos adicionales, escalado por el multiplicador promedio."""
    if extra_adults <= 0 or not multipliers:
        return Decimal("0.00")
    base = extra_guest_price * Decimal(extra_adults) * Decimal(len(multipliers))
    return (base * average_multiplier(multipliers)).quantize(_CENT, rounding=ROUND_HALF_UP)


sys.modules.setdefault("services.pricing", sys.modules[__name__])
sys.modules.setdefault("apps.api.services.pricing", sys.modules[__name__])
