"""Router de operación web: Check-in/out con auditoría, CRUD Habitaciones (TC-02), Salgados Café (TC-03), Eventos (TC-04) y Reseñas (Lote M4)."""

from datetime import date, datetime, timezone
from decimal import Decimal
import json
import sys
from typing import Any
import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from dependencies.auth import require_role
    from models.booking import ACTIVE_BOOKING_STATUSES, Booking, BookingStatus
    from models.guest import Guest
    from models.operations import (
        CafeMenuItem,
        CafeOrder,
        FolioCharge,
        Product,
        SpecialEvent,
    )
    from models.room import Room
    from models.user import User, UserRole
    from services.audit_service import record_audit
    from services.event_bus import publish_pms_event
    from services.payment_service import generate_unique_group_code
    from services.room_service import calculate_room_stay_price, load_active_events
    from services.reviews_service import fetch_google_reviews_summary
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.dependencies.auth import require_role
    from apps.api.models.booking import (
        ACTIVE_BOOKING_STATUSES,
        Booking,
        BookingStatus,
    )
    from apps.api.models.guest import Guest
    from apps.api.models.operations import (
        CafeMenuItem,
        CafeOrder,
        FolioCharge,
        Product,
        SpecialEvent,
    )
    from apps.api.models.room import Room
    from apps.api.models.user import User, UserRole
    from apps.api.services.audit_service import record_audit
    from apps.api.services.event_bus import publish_pms_event
    from apps.api.services.payment_service import generate_unique_group_code
    from apps.api.services.room_service import (
        calculate_room_stay_price,
        load_active_events,
    )
    from apps.api.services.reviews_service import fetch_google_reviews_summary

router = APIRouter(tags=["Web Operations (M4 & P5)"])


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
    publish_pms_event("booking.checkin", {"code": code, "rooms": room_numbers})

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
        await db.execute(
            update(FolioCharge)
            .where(FolioCharge.booking_id == b.id, FolioCharge.paid.is_(False))
            .values(paid=True)
        )
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
    publish_pms_event("booking.checkout", {"code": code, "rooms": room_numbers})

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

    if check_in >= check_out:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="checkIn debe ser anterior a checkOut")

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
    code = requested_code if requested_code.startswith("TS-") else await generate_unique_group_code(db)
    events = await load_active_events(db, check_in, check_out)
    _, _, total_price = calculate_room_stay_price(
        room=room,
        check_in=check_in,
        check_out=check_out,
        adults=int(body.get("adults", 2)),
        events=events,
    )

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
    publish_pms_event("room.status", {"roomId": room.id, "status": new_status})
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
def _serialize_menu_item(m: CafeMenuItem) -> dict[str, Any]:
    return {
        "id": m.id,
        "code": m.code,
        "name": m.name,
        "category": m.category,
        "description": m.description,
        "price": float(m.price),
        "available": m.available,
    }


def _serialize_cafe_order(o: CafeOrder, room_number: str | None = None) -> dict[str, Any]:
    try:
        items = json.loads(o.items_json)
    except json.JSONDecodeError:
        items = []
    return {
        "id": o.order_code,
        "numericId": o.id,
        "bookingId": o.booking_id,
        "roomId": o.room_id,
        "roomNumber": room_number,
        "tableNumber": o.table_number,
        "guestName": o.guest_name,
        "items": items,
        "total": float(o.total_amount),
        "orderTotal": float(o.total_amount),
        "status": o.status,
        "createdAt": o.created_at.isoformat() if o.created_at else None,
    }


async def _find_active_booking_for_room(
    db: AsyncSession,
    room_id: int | None = None,
    room_number: str | None = None,
    booking_id: int | None = None,
) -> tuple[Booking | None, Room | None]:
    target_room: Room | None = await db.get(Room, room_id) if room_id is not None else None
    if target_room is None and room_number:
        r_res = await db.execute(select(Room).where(Room.number == room_number.strip()))
        target_room = r_res.scalars().first()

    target_booking: Booking | None = await db.get(Booking, booking_id) if booking_id is not None else None
    if target_booking is None and target_room is not None:
        b_res = await db.execute(
            select(Booking)
            .where(
                Booking.room_id == target_room.id,
                Booking.status.in_(ACTIVE_BOOKING_STATUSES),
            )
            .order_by(Booking.id.desc())
        )
        target_booking = b_res.scalars().first()
    elif target_booking is not None and target_room is None:
        target_room = await db.get(Room, target_booking.room_id)
    return target_booking, target_room


@router.get("/api/restaurant/menu", status_code=status.HTTP_200_OK)
@router.get("/api/v1/restaurant/menu", status_code=status.HTTP_200_OK)
async def get_salgados_cafe_menu(
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Retorna la carta de Salgados Café persistida en PostgreSQL."""
    res = await db.execute(select(CafeMenuItem).order_by(CafeMenuItem.id.asc()))
    return [_serialize_menu_item(m) for m in res.scalars().all()]


@router.post("/api/v1/restaurant/menu", status_code=status.HTTP_201_CREATED)
async def create_cafe_menu_item(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Agrega un producto a la carta de Salgados Café (solo Administrador)."""
    name = str(body.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name es obligatorio")
    code = str(body.get("code") or f"m-{uuid.uuid4().hex[:6]}").strip()
    item = CafeMenuItem(
        code=code,
        name=name,
        category=str(body.get("category") or "coffee"),
        description=body.get("description"),
        price=Decimal(str(body.get("price", 0))).quantize(Decimal("0.01")),
        available=bool(body.get("available", True)),
    )
    db.add(item)
    await db.flush()
    await record_audit(
        db=db,
        actor=current_user.username,
        action="CAFE_MENU_CREATED",
        entity="cafe_menu",
        entity_id=str(item.id),
        details={"name": item.name, "price": str(item.price)},
    )
    await db.commit()
    await db.refresh(item)
    return _serialize_menu_item(item)


@router.post("/api/restaurant/orders", status_code=status.HTTP_200_OK)
@router.post("/api/v1/restaurant/orders", status_code=status.HTTP_200_OK)
async def create_restaurant_order(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Registra una comanda de Salgados Café en PostgreSQL y consolida el folio si aplica (TC-03)."""
    room_number_in = body.get("roomNumber") or body.get("room_number")
    room_id_in = body.get("roomId") or body.get("room_id")
    booking_id_in = body.get("bookingId") or body.get("booking_id")
    items = body.get("items") or []
    order_status = str(body.get("status") or ("charged_to_room" if (room_number_in or room_id_in or booking_id_in) else "pending"))

    order_total = Decimal("0.00")
    for item in items:
        price = Decimal(str(item.get("price", 0)))
        qty = int(item.get("qty", item.get("quantity", 1)))
        order_total += price * Decimal(qty)
    order_total = order_total.quantize(Decimal("0.01"))

    target_booking, target_room = await _find_active_booking_for_room(
        db=db,
        room_id=int(room_id_in) if room_id_in is not None and str(room_id_in).isdigit() else None,
        room_number=str(room_number_in) if room_number_in is not None else None,
        booking_id=int(booking_id_in) if booking_id_in is not None else None,
    )

    new_folio_total: Decimal | None = None
    if order_status == "charged_to_room" and target_booking is not None:
        target_booking.total_price = (target_booking.total_price + order_total).quantize(
            Decimal("0.01")
        )
        new_folio_total = target_booking.total_price
        for item in items:
            qty = int(item.get("qty", item.get("quantity", 1)))
            unit_p = Decimal(str(item.get("price", 0))).quantize(Decimal("0.01"))
            db.add(
                FolioCharge(
                    booking_id=target_booking.id,
                    room_id=target_room.id if target_room else target_booking.room_id,
                    source="restaurante",
                    description=f"Restaurante: {item.get('name', 'Consumo Salgados Café')}",
                    quantity=qty,
                    unit_price=unit_p,
                    total_amount=(unit_p * Decimal(qty)).quantize(Decimal("0.01")),
                    paid=False,
                    created_by=current_user.username,
                )
            )

    order_code = f"ord-{uuid.uuid4().hex[:6].upper()}"
    order_row = CafeOrder(
        order_code=order_code,
        booking_id=target_booking.id if target_booking else None,
        room_id=target_room.id if target_room else None,
        table_number=str(body.get("tableNumber")) if body.get("tableNumber") else None,
        guest_name=str(body.get("guestName")) if body.get("guestName") else None,
        items_json=json.dumps(items, ensure_ascii=False),
        total_amount=order_total,
        status=order_status,
        created_by=current_user.username,
    )
    db.add(order_row)
    await db.flush()

    resolved_room_num = target_room.number if target_room else (str(room_number_in) if room_number_in else None)
    await record_audit(
        db=db,
        actor=current_user.username,
        action="RESTAURANT_ORDER_CHARGED",
        entity="cafe_order",
        entity_id=order_row.order_code,
        details={
            "room_number": resolved_room_num,
            "order_total": str(order_total),
            "consolidated_folio_total": str(new_folio_total or order_total),
        },
    )
    await db.commit()
    await db.refresh(order_row)

    publish_pms_event("restaurant.order_created", {"orderCode": order_row.order_code})
    res_payload = _serialize_cafe_order(order_row, room_number=resolved_room_num)
    res_payload["consolidatedFolioTotal"] = float(new_folio_total) if new_folio_total is not None else float(order_total)
    return res_payload


@router.get("/api/restaurant/orders", status_code=status.HTTP_200_OK)
@router.get("/api/v1/restaurant/orders", status_code=status.HTTP_200_OK)
async def list_restaurant_orders(
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Lista las comandas de Salgados Café persistidas en PostgreSQL."""
    res = await db.execute(select(CafeOrder).order_by(CafeOrder.id.desc()))
    orders = res.scalars().all()
    out: list[dict[str, Any]] = []
    for o in orders:
        r = await db.get(Room, o.room_id) if o.room_id else None
        out.append(_serialize_cafe_order(o, room_number=r.number if r else None))
    return out


@router.patch("/api/v1/restaurant/orders/{order_ref}/status", status_code=status.HTTP_200_OK)
async def update_restaurant_order_status(
    order_ref: str,
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Actualiza el estado de una comanda de Salgados Café."""
    new_status = str(body.get("status") or "").strip()
    if new_status not in ("pending", "preparing", "delivered", "paid", "charged_to_room", "cancelled"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado de comanda inválido")

    if order_ref.isdigit():
        order = await db.get(CafeOrder, int(order_ref))
    else:
        res = await db.execute(select(CafeOrder).where(CafeOrder.order_code == order_ref))
        order = res.scalars().first()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comanda no encontrada")

    order.status = new_status
    await record_audit(
        db=db,
        actor=current_user.username,
        action="RESTAURANT_ORDER_STATUS_UPDATED",
        entity="cafe_order",
        entity_id=order.order_code,
        details={"status": new_status},
    )
    await db.commit()
    await db.refresh(order)
    r = await db.get(Room, order.room_id) if order.room_id else None
    return _serialize_cafe_order(order, room_number=r.number if r else None)


# ── 4. Tienda del Hotel, Inventario y Cargos al Folio ────────────────────────
def _serialize_product(p: Product) -> dict[str, Any]:
    return {
        "id": p.code,
        "numericId": p.id,
        "code": p.code,
        "name": p.name,
        "category": p.category,
        "price": float(p.price),
        "stock": p.stock,
        "active": p.active,
    }


@router.get("/api/v1/store/products", status_code=status.HTTP_200_OK)
async def list_store_products(
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Lista los productos activos del inventario de la Tienda del Hotel."""
    res = await db.execute(
        select(Product).where(Product.active.is_(True)).order_by(Product.id.asc())
    )
    return [_serialize_product(p) for p in res.scalars().all()]


@router.post("/api/v1/store/products", status_code=status.HTTP_201_CREATED)
async def create_store_product(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Crea un producto en el inventario de Tienda (solo Administrador)."""
    name = str(body.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name es obligatorio")
    code = str(body.get("code") or f"p-{uuid.uuid4().hex[:6]}").strip()
    prod = Product(
        code=code,
        name=name,
        category=str(body.get("category") or "Bebidas").strip(),
        price=Decimal(str(body.get("price", 0))).quantize(Decimal("0.01")),
        stock=int(body.get("stock", 0)),
        active=True,
    )
    db.add(prod)
    await db.flush()
    await record_audit(
        db=db,
        actor=current_user.username,
        action="PRODUCT_CREATED",
        entity="product",
        entity_id=prod.code,
        details={"name": prod.name, "price": str(prod.price), "stock": prod.stock},
    )
    await db.commit()
    await db.refresh(prod)
    return _serialize_product(prod)


@router.put("/api/v1/store/products/{product_ref}", status_code=status.HTTP_200_OK)
async def update_store_product(
    product_ref: str,
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Actualiza precio, stock o datos de un producto de Tienda (solo Administrador)."""
    if product_ref.isdigit():
        prod = await db.get(Product, int(product_ref))
    else:
        res = await db.execute(select(Product).where(Product.code == product_ref))
        prod = res.scalars().first()
    if prod is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    if "name" in body and str(body["name"]).strip():
        prod.name = str(body["name"]).strip()
    if "category" in body:
        prod.category = str(body["category"]).strip()
    if "price" in body:
        prod.price = Decimal(str(body["price"])).quantize(Decimal("0.01"))
    if "stock" in body:
        new_stock = int(body["stock"])
        if new_stock < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El stock no puede ser negativo")
        prod.stock = new_stock

    await record_audit(
        db=db,
        actor=current_user.username,
        action="PRODUCT_UPDATED",
        entity="product",
        entity_id=prod.code,
        details={"price": str(prod.price), "stock": prod.stock},
    )
    await db.commit()
    await db.refresh(prod)
    return _serialize_product(prod)


@router.delete("/api/v1/store/products/{product_ref}", status_code=status.HTTP_200_OK)
async def delete_store_product(
    product_ref: str,
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Desactiva un producto de la Tienda del Hotel (solo Administrador)."""
    if product_ref.isdigit():
        prod = await db.get(Product, int(product_ref))
    else:
        res = await db.execute(select(Product).where(Product.code == product_ref))
        prod = res.scalars().first()
    if prod is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    prod.active = False
    await record_audit(
        db=db,
        actor=current_user.username,
        action="PRODUCT_DEACTIVATED",
        entity="product",
        entity_id=prod.code,
    )
    await db.commit()
    return {"deleted": True, "code": prod.code}


@router.post("/api/v1/store/sales", status_code=status.HTTP_200_OK)
async def register_store_sale(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Descuenta inventario en PostgreSQL y carga el consumo al folio si chargeToRoom es verdadero."""
    items = body.get("items") or []
    if not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito está vacío")

    charge_to_room = bool(body.get("chargeToRoom", False))
    room_id_in = body.get("roomId")
    room_number_in = body.get("roomNumber")
    booking_id_in = body.get("bookingId")

    target_booking: Booking | None = None
    target_room: Room | None = None
    if charge_to_room:
        target_booking, target_room = await _find_active_booking_for_room(
            db=db,
            room_id=int(room_id_in) if room_id_in is not None and str(room_id_in).isdigit() else None,
            room_number=str(room_number_in) if room_number_in is not None else None,
            booking_id=int(booking_id_in) if booking_id_in is not None else None,
        )

    sale_total = Decimal("0.00")
    for entry in items:
        ref = str(entry.get("productId") or entry.get("id") or "").strip()
        qty = int(entry.get("qty", 1))
        if qty <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cantidad inválida")
        if ref.isdigit():
            prod = await db.get(Product, int(ref))
        else:
            res = await db.execute(select(Product).where(Product.code == ref, Product.active.is_(True)))
            prod = res.scalars().first()
        if prod is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Producto {ref} no encontrado")
        if prod.stock < qty:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Stock insuficiente para {prod.name} (disponible: {prod.stock})",
            )
        prod.stock -= qty
        line_total = (prod.price * Decimal(qty)).quantize(Decimal("0.01"))
        sale_total += line_total
        if charge_to_room:
            db.add(
                FolioCharge(
                    booking_id=target_booking.id if target_booking else None,
                    room_id=target_room.id if target_room else None,
                    source="tienda",
                    description=prod.name,
                    quantity=qty,
                    unit_price=prod.price,
                    total_amount=line_total,
                    paid=False,
                    created_by=current_user.username,
                )
            )

    if charge_to_room and target_booking is not None:
        target_booking.total_price = (target_booking.total_price + sale_total).quantize(Decimal("0.01"))

    await record_audit(
        db=db,
        actor=current_user.username,
        action="STORE_SALE_REGISTERED",
        entity="store",
        entity_id=target_room.number if target_room else "directo",
        details={"total": str(sale_total), "charge_to_room": charge_to_room},
    )
    await db.commit()
    publish_pms_event("store.sale", {"total": float(sale_total), "chargeToRoom": charge_to_room})
    return {"status": "ok", "total": float(sale_total), "chargedToRoom": charge_to_room}


@router.get("/api/v1/folio-charges", status_code=status.HTTP_200_OK)
async def list_folio_charges(
    room_id: int | None = Query(default=None),
    booking_id: int | None = Query(default=None),
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Lista cargos al folio pendientes o históricos."""
    stmt = select(FolioCharge).order_by(FolioCharge.id.desc())
    if room_id is not None:
        stmt = stmt.where(FolioCharge.room_id == room_id)
    if booking_id is not None:
        stmt = stmt.where(FolioCharge.booking_id == booking_id)
    res = await db.execute(stmt)
    rows = res.scalars().all()
    out: list[dict[str, Any]] = []
    for c in rows:
        room = await db.get(Room, c.room_id) if c.room_id else None
        out.append(
            {
                "id": c.id,
                "bookingId": c.booking_id,
                "roomId": c.room_id,
                "roomNumber": room.number if room else None,
                "source": c.source,
                "desc": c.description,
                "qty": c.quantity,
                "amount": float(c.total_amount),
                "paid": c.paid,
                "createdAt": c.created_at.isoformat() if c.created_at else None,
            }
        )
    return out


# ── 5. Motor de Eventos Especiales y Descuentos en DB (HU-12 / TC-04) ────────
def _serialize_event(ev: SpecialEvent) -> dict[str, Any]:
    return {
        "id": ev.id,
        "name": ev.name,
        "description": ev.description,
        "startDate": ev.start_date.isoformat(),
        "endDate": ev.end_date.isoformat(),
        "discountPercentage": float(ev.discount_percentage),
        "active": ev.active,
    }


@router.get("/api/events", status_code=status.HTTP_200_OK)
@router.get("/api/v1/events", status_code=status.HTTP_200_OK)
async def list_special_events(
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Lista eventos especiales y reglas de descuento/recargo persistidos en PostgreSQL."""
    res = await db.execute(select(SpecialEvent).order_by(SpecialEvent.start_date.asc(), SpecialEvent.id.asc()))
    return [_serialize_event(ev) for ev in res.scalars().all()]


@router.post("/api/events", status_code=status.HTTP_200_OK)
@router.post("/api/v1/events", status_code=status.HTTP_200_OK)
async def create_special_event(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Crea y persiste un evento en PostgreSQL y calcula discountedTotal si se envía baseAmount (TC-04)."""
    discount_pct = Decimal(str(body.get("discountPercentage", body.get("discount_percentage", 10)))).quantize(Decimal("0.01"))
    base_amount = Decimal(str(body.get("baseAmount", body.get("base_amount", 240000)))).quantize(Decimal("0.01"))
    start_d = date.fromisoformat(str(body.get("startDate") or "2026-12-01"))
    end_d = date.fromisoformat(str(body.get("endDate") or "2026-12-10"))
    if start_d > end_d:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="startDate debe ser <= endDate")

    ev = SpecialEvent(
        name=str(body.get("name") or "Feria Turística Sevilla").strip(),
        description=body.get("description"),
        start_date=start_d,
        end_date=end_d,
        discount_percentage=discount_pct,
        active=bool(body.get("active", True)),
    )
    db.add(ev)
    await db.flush()
    await record_audit(
        db=db,
        actor=current_user.username,
        action="SPECIAL_EVENT_CREATED",
        entity="special_event",
        entity_id=ev.id,
        details={"name": ev.name, "discount_pct": str(discount_pct)},
    )
    await db.commit()
    await db.refresh(ev)

    discounted_total = (
        base_amount * (Decimal("100") - discount_pct) / Decimal("100")
    ).quantize(Decimal("0.01"))
    payload = _serialize_event(ev)
    payload["baseAmount"] = float(base_amount)
    payload["discountedTotal"] = float(discounted_total)
    return payload


@router.patch("/api/v1/events/{event_id}/toggle", status_code=status.HTTP_200_OK)
async def toggle_special_event(
    event_id: int,
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Activa o desactiva un evento especial en PostgreSQL."""
    ev = await db.get(SpecialEvent, event_id)
    if ev is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado")
    ev.active = not ev.active
    await record_audit(
        db=db,
        actor=current_user.username,
        action="SPECIAL_EVENT_TOGGLED",
        entity="special_event",
        entity_id=ev.id,
        details={"active": ev.active},
    )
    await db.commit()
    await db.refresh(ev)
    return _serialize_event(ev)


@router.put("/api/v1/events/{event_id}", status_code=status.HTTP_200_OK)
async def update_special_event(
    event_id: int,
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Edita un evento especial existente en PostgreSQL."""
    ev = await db.get(SpecialEvent, event_id)
    if ev is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado")
    if "name" in body and str(body["name"]).strip():
        ev.name = str(body["name"]).strip()
    if "description" in body:
        ev.description = body["description"]
    if "startDate" in body:
        ev.start_date = date.fromisoformat(str(body["startDate"]))
    if "endDate" in body:
        ev.end_date = date.fromisoformat(str(body["endDate"]))
    if ev.start_date > ev.end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="startDate debe ser <= endDate")
    if "discountPercentage" in body:
        ev.discount_percentage = Decimal(str(body["discountPercentage"])).quantize(Decimal("0.01"))
    if "active" in body:
        ev.active = bool(body["active"])

    await record_audit(
        db=db,
        actor=current_user.username,
        action="SPECIAL_EVENT_UPDATED",
        entity="special_event",
        entity_id=ev.id,
    )
    await db.commit()
    await db.refresh(ev)
    return _serialize_event(ev)


@router.delete("/api/v1/events/{event_id}", status_code=status.HTTP_200_OK)
async def delete_special_event(
    event_id: int,
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Elimina un evento especial de PostgreSQL."""
    ev = await db.get(SpecialEvent, event_id)
    if ev is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado")
    await db.delete(ev)
    await record_audit(
        db=db,
        actor=current_user.username,
        action="SPECIAL_EVENT_DELETED",
        entity="special_event",
        entity_id=event_id,
    )
    await db.commit()
    return {"deleted": True, "id": event_id}


# ── 6. Resumen de Reseñas Reales desde Google Places API (E5 / P5) ───────────
@router.get("/api/reviews/summary", status_code=status.HTTP_200_OK)
@router.get("/api/v1/reviews/summary", status_code=status.HTTP_200_OK)
async def get_reviews_summary(
    refresh: bool = Query(default=False),
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
) -> dict[str, Any]:
    """Retorna el consolidado real de Google Places API (nunca inventa reseñas falsas)."""
    return await fetch_google_reviews_summary(refresh=refresh)


sys.modules.setdefault("routers.web_operations", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.web_operations", sys.modules[__name__])
