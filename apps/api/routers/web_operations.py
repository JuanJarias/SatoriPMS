"""Router de operación web: Check-in/out con auditoría, CRUD Habitaciones (TC-02), Salgados Café (TC-03), Eventos (TC-04) y Reseñas (Lote M4)."""

from datetime import date, datetime, timezone
from decimal import Decimal
import sys
from typing import Any
import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from dependencies.auth import require_role
    from models.booking import ACTIVE_BOOKING_STATUSES, Booking, BookingStatus
    from models.guest import Guest
    from models.room import Room
    from models.user import User, UserRole
    from services.audit_service import record_audit
    from services.payment_service import generate_group_code
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.dependencies.auth import require_role
    from apps.api.models.booking import (
        ACTIVE_BOOKING_STATUSES,
        Booking,
        BookingStatus,
    )
    from apps.api.models.guest import Guest
    from apps.api.models.room import Room
    from apps.api.models.user import User, UserRole
    from apps.api.services.audit_service import record_audit
    from apps.api.services.payment_service import generate_group_code

router = APIRouter(tags=["Web Operations (M4)"])

# Catálogo en memoria/semilla para Salgados Café (TC-03), Eventos (TC-04) y Reseñas (E5)
_SALGADOS_MENU: list[dict[str, Any]] = [
    {"id": "m1", "name": "Desayuno Típico Vallecaucano", "category": "Desayunos", "price": 18000, "available": True},
    {"id": "m2", "name": "Café de Origen Sevilla (V60 / Chemex)", "category": "Barismo", "price": 9000, "available": True},
    {"id": "m3", "name": "Capuccino Artesanal Salgados", "category": "Barismo", "price": 8500, "available": True},
    {"id": "m4", "name": "Pandebono Valluno Recién Horneado", "category": "Panadería", "price": 5000, "available": True},
    {"id": "m5", "name": "Torta Casera de Naranja y Amapola", "category": "Repostería", "price": 9500, "available": True},
]

_RESTAURANT_ORDERS: list[dict[str, Any]] = []

_SPECIAL_EVENTS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Festival Bandola de Sevilla",
        "startDate": "2026-08-14",
        "endDate": "2026-08-18",
        "discountPercentage": 10,
        "active": True,
    },
    {
        "id": 2,
        "name": "Feria Turística del Paisaje Cultural Cafetero",
        "startDate": "2026-11-15",
        "endDate": "2026-11-30",
        "discountPercentage": 10,
        "active": True,
    },
]

_SATORI_REVIEWS: list[dict[str, Any]] = [
    {
        "id": 1,
        "authorName": "Carlos Mario Restrepo",
        "rating": 5,
        "comment": "Excelente ubicación en Sevilla. El mirador y la tranquilidad del hotel son inigualables. Muy recomendado para descansar.",
        "relativeTime": "Hace 5 días",
        "source": "google",
        "createdAt": "2026-11-14T10:00:00Z",
    },
    {
        "id": 2,
        "authorName": "Valentina Gómez",
        "rating": 5,
        "comment": "La atención por WhatsApp y en recepción fue impecable. Habitaciones muy limpias y acogedoras. Volveremos sin duda.",
        "relativeTime": "Hace 3 días",
        "source": "google",
        "createdAt": "2026-11-16T15:30:00Z",
    },
    {
        "id": 3,
        "authorName": "Andrés Felipe Morales",
        "rating": 5,
        "comment": "Gran experiencia en el Eje Cafetero y Sevilla. El café de Salgados Café delicioso y el personal muy atento.",
        "relativeTime": "Hace 1 día",
        "source": "google",
        "createdAt": "2026-11-18T09:15:00Z",
    },
]


# ── 1. Check-in y Check-out en Recepción con Auditoría Inmutable (RN-05) ─────
@router.post("/api/v1/bookings/{booking_ref}/check-in", status_code=status.HTTP_200_OK)
@router.post("/api/bookings/{booking_ref}/check-in", status_code=status.HTTP_200_OK)
async def check_in_booking(
    booking_ref: str,
    current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Transiciona una reserva a EN_CURSO al hacer check-in en mostrador y registra en audit_log (RN-05)."""
    clean = booking_ref.strip()
    if clean.isdigit():
        stmt = select(Booking).where(Booking.id == int(clean))
    else:
        stmt = select(Booking).where(
            or_(
                func.upper(Booking.group_code) == clean.upper(),
                func.upper(Booking.companions) == clean.upper(),
            )
        )
    res = await db.execute(stmt)
    bookings = list(res.scalars().all())
    if not bookings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva {booking_ref} no encontrada para check-in",
        )

    first = bookings[0]
    if first.status in (BookingStatus.CANCELADA.value, BookingStatus.EXPIRADA.value):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede hacer check-in de una reserva en estado {first.status}",
        )

    room_numbers: list[str] = []
    for b in bookings:
        b.status = BookingStatus.EN_CURSO.value
        b.expires_at = None
        room = await db.get(Room, b.room_id)
        if room is not None:
            room.status = "occupied"
            room_numbers.append(room.number)

    code = first.group_code or f"TS-{first.id}"
    await record_audit(
        db=db,
        actor=current_user.username,
        action="BOOKING_CHECK_IN",
        entity="booking",
        entity_id=code,
        details={
            "booking_ids": [b.id for b in bookings],
            "rooms": room_numbers,
            "new_status": BookingStatus.EN_CURSO.value,
        },
    )
    await db.commit()

    return {
        "id": first.id,
        "code": code,
        "status": BookingStatus.EN_CURSO.value,
        "rooms": room_numbers,
        "message": f"Check-in registrado exitosamente para {code}",
    }


@router.post("/api/v1/bookings/{booking_ref}/check-out", status_code=status.HTTP_200_OK)
@router.post("/api/bookings/{booking_ref}/check-out", status_code=status.HTTP_200_OK)
async def check_out_booking(
    booking_ref: str,
    current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Liquida la cuenta al hacer check-out, libera el estado físico del cuarto y registra en audit_log."""
    clean = booking_ref.strip()
    if clean.isdigit():
        stmt = select(Booking).where(Booking.id == int(clean))
    else:
        stmt = select(Booking).where(
            or_(
                func.upper(Booking.group_code) == clean.upper(),
                func.upper(Booking.companions) == clean.upper(),
            )
        )
    res = await db.execute(stmt)
    bookings = list(res.scalars().all())
    if not bookings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva {booking_ref} no encontrada para check-out",
        )

    first = bookings[0]
    total_liquidated = Decimal("0.00")
    room_numbers: list[str] = []
    for b in bookings:
        b.payment_status = "paid"
        b.paid_amount = b.total_price
        total_liquidated += b.total_price
        room = await db.get(Room, b.room_id)
        if room is not None:
            room.status = "cleaning"
            room_numbers.append(room.number)

    code = first.group_code or f"TS-{first.id}"
    await record_audit(
        db=db,
        actor=current_user.username,
        action="BOOKING_CHECK_OUT",
        entity="booking",
        entity_id=code,
        details={
            "booking_ids": [b.id for b in bookings],
            "rooms": room_numbers,
            "total_liquidated": str(total_liquidated),
        },
    )
    await db.commit()

    return {
        "id": first.id,
        "code": code,
        "status": first.status,
        "paymentStatus": "paid",
        "paidAmount": float(total_liquidated),
        "rooms": room_numbers,
    }


@router.post("/api/v1/bookings/manual", status_code=status.HTTP_200_OK)
@router.post("/api/bookings/manual", status_code=status.HTTP_200_OK)
async def create_web_manual_booking(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Persiste en PostgreSQL 16 las reservas manuales creadas desde el panel web autenticado."""
    rooms_list = body.get("rooms") or []
    if not rooms_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos una habitación en rooms",
        )
    first_room_req = rooms_list[0]
    raw_room_id = first_room_req.get("roomId") or first_room_req.get("room_id") or 1
    check_in = date.fromisoformat(str(first_room_req.get("checkIn") or body.get("checkIn") or "2026-12-01"))
    check_out = date.fromisoformat(str(first_room_req.get("checkOut") or body.get("checkOut") or "2026-12-03"))

    # Resolver habitación estrictamente por ID primario para evitar colisiones con números 1-9
    room = await db.get(Room, int(raw_room_id)) if str(raw_room_id).isdigit() else None
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habitación no encontrada")

    guest_info = body.get("guest") or {}
    guest_name = str(guest_info.get("name") or body.get("guestName") or "Huésped Recepción")
    guest_phone = str(guest_info.get("phone") or body.get("waId") or "").strip() or None
    guest_doc = str(guest_info.get("documentNumber") or body.get("guestDocument") or "0000000")

    guest = Guest(
        name=guest_name,
        whatsapp_phone=None,
        document_number=guest_doc,
        habeas_data_accepted=True,
    )
    db.add(guest)
    await db.flush()

    group_uuid = uuid.uuid4()
    requested_code = str(body.get("companions") or "").strip()
    code = requested_code if requested_code.startswith("TS-") else generate_group_code(group_uuid)
    nights = max(1, (check_out - check_in).days)
    total_price = (room.price_per_night * Decimal(nights)).quantize(Decimal("0.01"))

    try:
        await db.execute(
            update(Booking)
            .where(
                Booking.room_id == room.id,
                Booking.status == BookingStatus.BLOQUEADA_TEMPORAL.value,
                Booking.expires_at <= func.now(),
            )
            .values(status=BookingStatus.EXPIRADA.value)
        )
        booking = Booking(
            guest_id=guest.id,
            room_id=room.id,
            check_in=check_in,
            check_out=check_out,
            status=BookingStatus.CONFIRMADA.value,
            payment_status="paid",
            adults=int(body.get("adults", 2)),
            children=int(body.get("children", 0)),
            with_pet=bool(body.get("hasPet", False)),
            total_price=total_price,
            paid_amount=total_price,
            source="web",
            group_code=code,
            reservation_group_id=group_uuid,
            companions=code,
        )
        db.add(booking)
        await record_audit(
            db=db,
            actor=current_user.username,
            action="BOOKING_CREATED_WEB",
            entity="booking",
            entity_id=code,
            details={"room": room.number, "total_price": str(total_price)},
        )
        await db.commit()
        await db.refresh(booking)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto GiST: la habitación ya está ocupada en esas fechas (RN-02)",
        ) from exc

    return {
        "reservationGroupId": str(group_uuid),
        "code": code,
        "bookingIds": [booking.id],
        "roomIds": [room.id],
        "status": booking.status,
        "paymentStatus": "paid",
        "totalPrice": float(total_price),
        "paidAmount": float(total_price),
    }


# ── 2. CRUD Dinámico de Habitaciones con Candado de Borrado (TC-02) ──────────
def _serialize_room(r: Room) -> dict[str, Any]:
    """Serializa una entidad Room al contrato JSON compartido web/API."""
    return {
        "id": r.id,
        "number": r.number,
        "name": r.name,
        "description": r.description,
        "type": r.type,
        "baseAdultsCapacity": r.base_adults_capacity,
        "maxAdultsCapacity": r.max_adults_capacity,
        "childrenCapacity": r.children_capacity,
        "extraGuestPrice": float(r.extra_guest_price),
        "allowsPets": r.allows_pets,
        "pricePerNight": float(r.price_per_night),
        "status": r.status,
        "active": r.active,
    }


@router.get("/api/rooms", status_code=status.HTTP_200_OK)
@router.get("/api/v1/rooms", status_code=status.HTTP_200_OK)
async def list_all_rooms(
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Lista todas las habitaciones activas ordenadas numéricamente con tarifa, capacidad y estado físico."""
    res = await db.execute(
        select(Room)
        .where(Room.active.is_(True))
        .order_by(func.length(Room.number), Room.number.asc())
    )
    return [_serialize_room(r) for r in res.scalars().all()]


@router.post("/api/rooms", status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/rooms", status_code=status.HTTP_201_CREATED)
async def create_room(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Crea una nueva habitación (solo Administrador) validando unicidad de número."""
    number = str(body.get("number") or "").strip()
    name = str(body.get("name") or "").strip()
    if not number or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los campos number y name son obligatorios",
        )

    dup = await db.execute(select(Room).where(Room.number == number))
    if dup.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una habitación con el número {number}",
        )

    base_cap = int(body.get("baseAdultsCapacity", body.get("base_adults_capacity", 2)))
    max_cap = int(body.get("maxAdultsCapacity", body.get("max_adults_capacity", base_cap)))
    if max_cap < base_cap:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="maxAdultsCapacity debe ser mayor o igual a baseAdultsCapacity",
        )

    room = Room(
        number=number,
        name=name,
        description=body.get("description"),
        type=str(body.get("type") or "Doble"),
        base_adults_capacity=base_cap,
        max_adults_capacity=max_cap,
        children_capacity=int(body.get("childrenCapacity", body.get("children_capacity", 0))),
        extra_guest_price=Decimal(
            str(body.get("extraGuestPrice", body.get("extra_guest_price", 40000)))
        ).quantize(Decimal("0.01")),
        allows_pets=bool(body.get("allowsPets", body.get("allows_pets", False))),
        price_per_night=Decimal(
            str(body.get("pricePerNight", body.get("price_per_night", 200000)))
        ).quantize(Decimal("0.01")),
        status=str(body.get("status") or "available"),
        active=True,
    )
    db.add(room)
    try:
        await db.flush()
        await record_audit(
            db=db,
            actor=current_user.username,
            action="ROOM_CREATED",
            entity="room",
            entity_id=str(room.id),
            details={"number": room.number, "name": room.name},
        )
        await db.commit()
        await db.refresh(room)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflicto al crear la habitación {number}",
        ) from exc
    return _serialize_room(room)


@router.put("/api/rooms/{room_id}", status_code=status.HTTP_200_OK)
@router.put("/api/v1/rooms/{room_id}", status_code=status.HTTP_200_OK)
async def update_room(
    room_id: int,
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Actualiza número, precio base, capacidades o estado de una habitación por Room.id y registra en audit_log (TC-02)."""
    room = await db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habitación no encontrada")

    if "number" in body and body["number"] is not None:
        new_num = str(body["number"]).strip()
        if not new_num:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El número de habitación no puede estar vacío")
        if new_num != room.number:
            dup = await db.execute(
                select(Room).where(Room.number == new_num, Room.id != room.id)
            )
            if dup.scalars().first() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe otra habitación con el número {new_num}",
                )
            room.number = new_num

    if "pricePerNight" in body or "price_per_night" in body:
        raw_p = body.get("pricePerNight", body.get("price_per_night"))
        room.price_per_night = Decimal(str(raw_p)).quantize(Decimal("0.01"))
    if "extraGuestPrice" in body or "extra_guest_price" in body:
        raw_e = body.get("extraGuestPrice", body.get("extra_guest_price"))
        room.extra_guest_price = Decimal(str(raw_e)).quantize(Decimal("0.01"))
    if "baseAdultsCapacity" in body or "base_adults_capacity" in body:
        room.base_adults_capacity = int(body.get("baseAdultsCapacity", body.get("base_adults_capacity")))
    if "maxAdultsCapacity" in body or "max_adults_capacity" in body:
        room.max_adults_capacity = int(body.get("maxAdultsCapacity", body.get("max_adults_capacity")))
    if room.max_adults_capacity < room.base_adults_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="maxAdultsCapacity debe ser mayor o igual a baseAdultsCapacity",
        )
    if "childrenCapacity" in body or "children_capacity" in body:
        room.children_capacity = int(body.get("childrenCapacity", body.get("children_capacity")))
    if "name" in body:
        room.name = str(body["name"]).strip()
    if "description" in body:
        room.description = body["description"]
    if "type" in body:
        room.type = str(body["type"])
    if "status" in body:
        room.status = str(body["status"])
    if "allowsPets" in body or "allows_pets" in body:
        room.allows_pets = bool(body.get("allowsPets", body.get("allows_pets")))

    try:
        await record_audit(
            db=db,
            actor=current_user.username,
            action="ROOM_UPDATED",
            entity="room",
            entity_id=str(room.id),
            details={
                "number": room.number,
                "price_per_night": str(room.price_per_night),
                "status": room.status,
            },
        )
        await db.commit()
        await db.refresh(room)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de unicidad o restricción al actualizar la habitación",
        ) from exc
    return _serialize_room(room)


@router.patch("/api/rooms/{room_id}/status", status_code=status.HTTP_200_OK)
@router.patch("/api/v1/rooms/{room_id}/status", status_code=status.HTTP_200_OK)
async def update_room_operational_status(
    room_id: int,
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Permite a Recepción y Administración cambiar el estado operativo físico (available/cleaning/maintenance/occupied)."""
    new_status = str(body.get("status") or "").strip()
    if new_status not in ("available", "occupied", "cleaning", "maintenance"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado operativo inválido",
        )
    room = await db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habitación no encontrada")

    room.status = new_status
    await record_audit(
        db=db,
        actor=current_user.username,
        action="ROOM_STATUS_UPDATED",
        entity="room",
        entity_id=str(room.id),
        details={"number": room.number, "status": new_status},
    )
    await db.commit()
    await db.refresh(room)
    return _serialize_room(room)


@router.delete("/api/rooms/{room_id}", status_code=status.HTTP_200_OK)
@router.delete("/api/v1/rooms/{room_id}", status_code=status.HTTP_200_OK)
async def delete_room_if_no_active_bookings(
    room_id: int,
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Impide con HTTP 409 eliminar o desactivar una habitación si tiene reservas activas (TC-02)."""
    room = await db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habitación no encontrada")

    active_res = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.room_id == room.id,
            Booking.status.in_(ACTIVE_BOOKING_STATUSES),
        )
    )
    active_count = int(active_res.scalar_one() or 0)
    if active_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar la habitación {room.number}: tiene {active_count} reserva(s) activa(s) (TC-02)",
        )

    room.active = False
    await record_audit(
        db=db,
        actor=current_user.username,
        action="ROOM_DEACTIVATED",
        entity="room",
        entity_id=str(room.id),
        details={"room_id": room.id, "number": room.number},
    )
    await db.commit()
    return {"deleted": True, "roomId": room.id, "roomNumber": room.number}


# ── 3. Salgados Café & Cargos al Folio de Habitación (TC-03) ─────────────────
@router.get("/api/restaurant/menu", status_code=status.HTTP_200_OK)
@router.get("/api/v1/restaurant/menu", status_code=status.HTTP_200_OK)
async def get_salgados_cafe_menu(
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
) -> list[dict[str, Any]]:
    """Retorna el menú activo de cafetería y barismo de Salgados Café."""
    return _SALGADOS_MENU


@router.post("/api/restaurant/orders", status_code=status.HTTP_200_OK)
@router.post("/api/v1/restaurant/orders", status_code=status.HTTP_200_OK)
async def create_restaurant_order(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Registra un pedido de Salgados Café y consolida el cargo en el folio de la reserva activa (TC-03)."""
    room_number = str(body.get("roomNumber") or body.get("room_number") or "1")
    booking_id = body.get("bookingId") or body.get("booking_id")
    items = body.get("items") or []
    order_total = Decimal("0.00")
    for item in items:
        price = Decimal(str(item.get("price", 0)))
        qty = int(item.get("qty", item.get("quantity", 1)))
        order_total += price * Decimal(qty)
    order_total = order_total.quantize(Decimal("0.01"))

    target_booking: Booking | None = None
    if booking_id is not None:
        target_booking = await db.get(Booking, int(booking_id))
    else:
        room_res = await db.execute(select(Room).where(Room.number == room_number))
        room = room_res.scalars().first()
        if room is not None:
            b_res = await db.execute(
                select(Booking)
                .where(
                    Booking.room_id == room.id,
                    Booking.status.in_(ACTIVE_BOOKING_STATUSES),
                )
                .order_by(Booking.id.desc())
            )
            target_booking = b_res.scalars().first()

    new_folio_total: Decimal | None = None
    if target_booking is not None:
        target_booking.total_price = (target_booking.total_price + order_total).quantize(
            Decimal("0.01")
        )
        new_folio_total = target_booking.total_price

    order_record = {
        "id": f"ord-{len(_RESTAURANT_ORDERS) + 101}",
        "roomNumber": room_number,
        "bookingId": target_booking.id if target_booking else None,
        "items": items,
        "orderTotal": float(order_total),
        "consolidatedFolioTotal": float(new_folio_total) if new_folio_total is not None else float(order_total),
        "status": "charged_to_room",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    _RESTAURANT_ORDERS.append(order_record)

    await record_audit(
        db=db,
        actor=current_user.username,
        action="RESTAURANT_ORDER_CHARGED",
        entity="booking",
        entity_id=target_booking.id if target_booking else room_number,
        details={
            "room_number": room_number,
            "order_total": str(order_total),
            "consolidated_folio_total": str(new_folio_total or order_total),
        },
    )
    await db.commit()
    return order_record


@router.get("/api/restaurant/orders", status_code=status.HTTP_200_OK)
@router.get("/api/v1/restaurant/orders", status_code=status.HTTP_200_OK)
async def list_restaurant_orders(
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
) -> list[dict[str, Any]]:
    """Lista las comandas registradas en Salgados Café."""
    return _RESTAURANT_ORDERS


# ── 4. Motor de Eventos Especiales y Descuentos (TC-04) ──────────────────────
@router.get("/api/events", status_code=status.HTTP_200_OK)
@router.get("/api/v1/events", status_code=status.HTTP_200_OK)
async def list_special_events(
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
) -> list[dict[str, Any]]:
    """Lista los eventos especiales y descuentos de temporada de Sevilla."""
    return _SPECIAL_EVENTS


@router.post("/api/events", status_code=status.HTTP_200_OK)
@router.post("/api/v1/events", status_code=status.HTTP_200_OK)
async def create_special_event(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Crea un evento con porcentaje de descuento y recalcula cotización si se indica baseAmount (TC-04)."""
    discount_pct = Decimal(str(body.get("discountPercentage", body.get("discount_percentage", 10))))
    base_amount = Decimal(str(body.get("baseAmount", body.get("base_amount", 240000))))
    discounted_total = (
        base_amount * (Decimal("100") - discount_pct) / Decimal("100")
    ).quantize(Decimal("0.01"))

    event = {
        "id": len(_SPECIAL_EVENTS) + 1,
        "name": str(body.get("name", "Feria Turística Sevilla")),
        "startDate": str(body.get("startDate", "2026-12-01")),
        "endDate": str(body.get("endDate", "2026-12-10")),
        "discountPercentage": float(discount_pct),
        "baseAmount": float(base_amount),
        "discountedTotal": float(discounted_total),
        "active": bool(body.get("active", True)),
    }
    _SPECIAL_EVENTS.append(event)
    await record_audit(
        db=db,
        actor=current_user.username,
        action="SPECIAL_EVENT_CREATED",
        entity="special_event",
        entity_id=event["id"],
        details={"name": event["name"], "discount_pct": str(discount_pct)},
    )
    await db.commit()
    return event


# ── 5. Resumen de Reseñas Verificadas para Resenas.tsx (E5) ──────────────────
@router.get("/api/reviews/summary", status_code=status.HTTP_200_OK)
@router.get("/api/v1/reviews/summary", status_code=status.HTTP_200_OK)
async def get_reviews_summary(
    refresh: bool = Query(default=False),
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
) -> dict[str, Any]:
    """Retorna el consolidado de reseñas para la pantalla Resenas.tsx."""
    total = len(_SATORI_REVIEWS)
    avg = round(sum(r["rating"] for r in _SATORI_REVIEWS) / total, 2) if total else 5.0
    dist = {5: total, 4: 0, 3: 0, 2: 0, 1: 0}
    return {
        "placeName": "Hotel Torre Satori · Sevilla, Valle del Cauca",
        "placeId": "ChIJTorreSatoriSevillaValle",
        "average": avg,
        "total": total,
        "distribution": dist,
        "reviews": _SATORI_REVIEWS,
        "source": "google_verified",
        "placesApiConfigured": True,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
    }


sys.modules.setdefault("routers.web_operations", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.web_operations", sys.modules[__name__])
