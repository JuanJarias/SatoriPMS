"""Router de catálogo y disponibilidad de habitaciones (Lote M2)."""

from datetime import date
import sys

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from dependencies.auth import require_service_or_role
    from models.user import User, UserRole
    from schemas.room import RoomAvailabilityItem
    from services.room_service import get_available_rooms
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.dependencies.auth import require_service_or_role
    from apps.api.models.user import User, UserRole
    from apps.api.schemas.room import RoomAvailabilityItem
    from apps.api.services.room_service import get_available_rooms

router = APIRouter(prefix="/api/v1/rooms", tags=["Rooms & Availability"])


@router.get(
    "/availability",
    response_model=list[RoomAvailabilityItem],
    status_code=status.HTTP_200_OK,
)
async def check_rooms_availability(
    check_in: date = Query(..., description="Fecha de llegada (YYYY-MM-DD)"),
    check_out: date = Query(..., description="Fecha de salida (YYYY-MM-DD)"),
    adults: int = Query(default=2, ge=1, description="Cantidad de adultos"),
    children: int = Query(default=0, ge=0, description="Cantidad de niños"),
    with_pet: bool = Query(default=False, description="Viaja con mascota"),
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> list[RoomAvailabilityItem]:
    """Retorna las habitaciones disponibles filtrando en PostgreSQL e ignorando candados con expires_at <= NOW()."""
    return await get_available_rooms(
        db=db,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        children=children,
        with_pet=with_pet,
    )


sys.modules.setdefault("routers.rooms", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.rooms", sys.modules[__name__])
