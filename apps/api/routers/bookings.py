"""Router de bloqueo temporal atómico de 15 minutos y liberación de reservas (Lote M2)."""

import sys

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from dependencies.auth import require_service_or_role
    from models.user import User, UserRole
    from schemas.booking import (
        LockRequest,
        LockResponse,
        UnlockRequest,
        UnlockResponse,
    )
    from services.booking_service import (
        create_booking_lock,
        release_booking_lock,
    )
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.dependencies.auth import require_service_or_role
    from apps.api.models.user import User, UserRole
    from apps.api.schemas.booking import (
        LockRequest,
        LockResponse,
        UnlockRequest,
        UnlockResponse,
    )
    from apps.api.services.booking_service import (
        create_booking_lock,
        release_booking_lock,
    )

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings & Atomic Lock"])


@router.post(
    "/lock",
    response_model=LockResponse,
    status_code=status.HTTP_200_OK,
)
async def lock_room(
    payload: LockRequest,
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> LockResponse:
    """Adquiere el candado GiST de 15 minutos tras validar RN-01, RN-12 y expirar bloqueos vencidos."""
    return await create_booking_lock(db=db, payload=payload)


@router.post(
    "/unlock",
    response_model=UnlockResponse,
    status_code=status.HTTP_200_OK,
)
async def unlock_room(
    payload: UnlockRequest,
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> UnlockResponse:
    """Libera manualmente un bloqueo temporal marcándolo como EXPIRADA."""
    return await release_booking_lock(db=db, payload=payload)


sys.modules.setdefault("routers.bookings", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.bookings", sys.modules[__name__])
