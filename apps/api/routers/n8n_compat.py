"""Router de compatibilidad para el flujo n8n V10 (origin/main) y operaciones de grupo de reservas (Lote M3)."""

from datetime import date, datetime, time, timezone
from decimal import Decimal
import sys
from typing import Any
import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from dependencies.auth import require_role, require_service_or_role, resolve_actor_name
    from models.booking import Booking, BookingStatus
    from models.guest import Guest
    from models.room import Room
    from models.user import User, UserRole
    from schemas.booking import LockRequest
    from services.audit_service import record_audit
    from services.booking_service import create_booking_lock
    from services.event_bus import publish_pms_event
    from services.payment_service import generate_group_code
    from services.room_service import (
        calculate_room_stay_price,
        get_available_rooms,
    )
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.dependencies.auth import (
        require_role,
        require_service_or_role,
        resolve_actor_name,
    )
    from apps.api.models.booking import Booking, BookingStatus
    from apps.api.models.guest import Guest
    from apps.api.models.room import Room
    from apps.api.models.user import User, UserRole
    from apps.api.schemas.booking import LockRequest
    from apps.api.services.audit_service import record_audit
    from apps.api.services.booking_service import create_booking_lock
    from apps.api.services.event_bus import publish_pms_event
    from apps.api.services.payment_service import generate_group_code
    from apps.api.services.room_service import (
        calculate_room_stay_price,
        get_available_rooms,
    )

router = APIRouter(tags=["n8n V10 & Group Bookings"])


def _calculate_rn03_refund(
    check_in_date: date,
    paid_amount: Decimal,
) -> tuple[int, int, Decimal, str]:
    """Calcula horas hasta el check-in (15:00), porcentaje y monto de reembolso según RN-03."""
    checkin_dt = datetime.combine(check_in_date, time(15, 0), tzinfo=timezone.utc)
    now_dt = datetime.now(timezone.utc)
    hours_until = int((checkin_dt - now_dt).total_seconds() // 3600)

    if hours_until > 72:
        pct = 100
        desc = "Reembolso del 100% de lo abonado (+72h antes del check-in)"
    elif hours_until >= 24:
        pct = 50
        desc = "Reembolso del 50% de lo abonado (entre 24h y 72h antes del check-in)"
    else:
        pct = 0
        desc = "Sin reembolso (menos de 24h antes del check-in)"

    refund_amount = (
        paid_amount * Decimal(pct) / Decimal("100")
    ).quantize(Decimal("0.01"))
    return hours_until, pct, refund_amount, desc


async def _find_bookings_by_code(
    db: AsyncSession,
    code: str,
) -> list[Booking]:
    """Busca todas las reservas de un grupo por código TS-XXXX, prefijo de UUID o ID numérico."""
    clean = code.strip()
    upper_code = clean.upper()
    if not upper_code.startswith("TS-") and len(clean) == 4:
        upper_code = f"TS-{upper_code}"

    conditions = [
        func.upper(Booking.group_code) == upper_code,
        func.upper(Booking.companions) == upper_code,
    ]
    if clean.isdigit():
        conditions.append(Booking.id == int(clean))
    try:
        parsed_uuid = uuid.UUID(clean)
        conditions.append(Booking.reservation_group_id == parsed_uuid)
    except ValueError:
        pass

    stmt = (
        select(Booking)
        .where(or_(*conditions))
        .order_by(Booking.id.asc())
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.get("/api/rooms/availability", status_code=status.HTTP_200_OK)
async def compat_rooms_availability(
    checkIn: date | None = Query(default=None),
    checkOut: date | None = Query(default=None),
    check_in: date | None = Query(default=None),
    check_out: date | None = Query(default=None),
    adults: int = Query(default=2, ge=1),
    children: int = Query(default=0, ge=0),
    pet: bool = Query(default=False),
    with_pet: bool = Query(default=False),
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Endpoint compatible con n8n V10 (camelCase) y API v1 (snake_case) para disponibilidad."""
    c_in = checkIn or check_in
    c_out = checkOut or check_out
    if c_in is None or c_out is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe indicar checkIn/check_in y checkOut/check_out",
        )
    items = await get_available_rooms(
        db=db,
        check_in=c_in,
        check_out=c_out,
        adults=adults,
        children=children,
        with_pet=bool(pet or with_pet),
    )
    return [
        {
            "id": r.id,
            "number": r.number,
            "name": r.name,
            "description": r.description,
            "type": r.type,
            "baseAdultsCapacity": r.base_adults_capacity,
            "base_adults_capacity": r.base_adults_capacity,
            "maxAdultsCapacity": r.max_adults_capacity,
            "max_adults_capacity": r.max_adults_capacity,
            "childrenCapacity": r.children_capacity,
            "children_capacity": r.children_capacity,
            "extraGuestPrice": float(r.extra_guest_price),
            "extra_guest_price": str(r.extra_guest_price),
            "allowsPets": r.allows_pets,
            "allows_pets": r.allows_pets,
            "pricePerNight": float(r.price_per_night),
            "price_per_night": str(r.price_per_night),
            "nights": r.nights,
            "extraAdults": r.extra_adults,
            "extra_adults": r.extra_adults,
            "totalPrice": float(r.total_price),
            "total_price": str(r.total_price),
        }
        for r in items
    ]


@router.post("/api/bookings/lock", status_code=status.HTTP_200_OK)
async def compat_lock_room(
    body: dict[str, Any] = Body(...),
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Crea bloqueo temporal de 15 min compatible con el nodo 'API Bloquear Habitación 15 min' de n8n V10."""
    room_id = body.get("roomId") or body.get("room_id")
    check_in_raw = body.get("checkIn") or body.get("check_in")
    check_out_raw = body.get("checkOut") or body.get("check_out")
    if room_id is None or not check_in_raw or not check_out_raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="roomId, checkIn y checkOut son obligatorios",
        )

    lock_req = LockRequest(
        room_id=int(room_id),
        check_in=date.fromisoformat(str(check_in_raw)),
        check_out=date.fromisoformat(str(check_out_raw)),
        adults=int(body.get("adults", 2)),
        children=int(body.get("children", 0)),
        with_pet=bool(body.get("withPet", body.get("with_pet", False))),
        guest_name=str(body.get("guestName") or body.get("guest_name") or "Huésped WhatsApp"),
        whatsapp_phone=str(body.get("waId") or body.get("whatsapp_phone") or "") or None,
        document_number=str(body.get("guestDocument") or body.get("document_number") or "") or None,
        habeas_data_accepted=bool(body.get("habeas_data_accepted", True)),
        source=str(body.get("source", "chatbot")),
    )
    lock_res = await create_booking_lock(db=db, payload=lock_req)
    return {
        "lockToken": str(lock_res.booking_id),
        "booking_id": lock_res.booking_id,
        "roomId": lock_res.room_id,
        "roomNumber": lock_res.room_number,
        "status": lock_res.status,
        "ttlSeconds": 900,
        "totalPrice": float(lock_res.total_price),
        "expiresAt": lock_res.expires_at.isoformat(),
    }


@router.post("/api/bookings/unlock", status_code=status.HTTP_200_OK)
async def compat_unlock_rooms(
    body: dict[str, Any] | None = Body(default=None),
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    """Libera uno o varios bloqueos temporales de n8n V10 marcándolos como EXPIRADA en PostgreSQL."""
    if not body:
        return {"released": 0}

    booking_ids: list[int] = []
    room_ids: list[int] = []

    locks_list = body.get("locks")
    if isinstance(locks_list, list):
        for item in locks_list:
            if isinstance(item, dict):
                tok = item.get("lockToken") or item.get("booking_id")
                r_id = item.get("roomId") or item.get("room_id")
                if tok is not None and str(tok).isdigit():
                    booking_ids.append(int(tok))
                elif r_id is not None:
                    room_ids.append(int(r_id))
    else:
        tok = body.get("lockToken") or body.get("booking_id")
        r_id = body.get("roomId") or body.get("room_id")
        if tok is not None and str(tok).isdigit():
            booking_ids.append(int(tok))
        elif r_id is not None:
            room_ids.append(int(r_id))

    released = 0
    if booking_ids:
        res = await db.execute(
            update(Booking)
            .where(
                Booking.id.in_(booking_ids),
                Booking.status == BookingStatus.BLOQUEADA_TEMPORAL.value,
            )
            .values(status=BookingStatus.EXPIRADA.value)
        )
        released += int(res.rowcount or 0)
    if room_ids:
        res = await db.execute(
            update(Booking)
            .where(
                Booking.room_id.in_(room_ids),
                Booking.status == BookingStatus.BLOQUEADA_TEMPORAL.value,
            )
            .values(status=BookingStatus.EXPIRADA.value)
        )
        released += int(res.rowcount or 0)

    await db.commit()
    return {"released": released}


@router.post("/api/bookings/confirm", status_code=status.HTTP_200_OK)
@router.post("/api/v1/bookings/confirm", status_code=status.HTTP_200_OK)
async def confirm_bookings_batch(
    body: dict[str, Any] = Body(...),
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Confirma una o varias habitaciones bloqueadas asignando código TS-XXXX y registrando en audit_log."""
    check_in_raw = body.get("checkIn") or body.get("check_in")
    check_out_raw = body.get("checkOut") or body.get("check_out")
    if not check_in_raw or not check_out_raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="checkIn y checkOut son obligatorios",
        )
    check_in = date.fromisoformat(str(check_in_raw))
    check_out = date.fromisoformat(str(check_out_raw))
    if check_in >= check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="checkIn debe ser anterior a checkOut",
        )

    adults = int(body.get("adults", 2))
    children = int(body.get("children", 0))
    has_pet = bool(body.get("hasPet", body.get("with_pet", False)))
    wa_id = str(body.get("waId") or body.get("whatsapp_phone") or "").strip() or None
    guest_name = str(body.get("guestName") or body.get("guest_name") or "Huésped Torre Satori").strip()
    guest_doc = str(body.get("guestDocument") or body.get("document_number") or "").strip() or None
    companions_in = str(body.get("companions") or "").strip()
    payment_option = str(body.get("paymentOption") or body.get("payment_option") or "deposit").lower()
    source = str(body.get("source") or "chatbot").lower()

    rooms_input = body.get("rooms") or []
    if not isinstance(rooms_input, list) or not rooms_input:
        single_room_id = body.get("roomId") or body.get("room_id")
        single_token = body.get("lockToken") or body.get("booking_id")
        if single_room_id is not None:
            rooms_input = [{"roomId": single_room_id, "lockToken": single_token}]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe especificar al menos una habitación en rooms",
            )

    # 1. Resolver o actualizar huésped titular con consentimiento Ley 1581
    if wa_id:
        guest_stmt = (
            pg_insert(Guest)
            .values(
                whatsapp_phone=wa_id,
                document_number=guest_doc,
                name=guest_name,
                habeas_data_accepted=True,
            )
            .on_conflict_do_update(
                index_elements=[Guest.whatsapp_phone],
                set_={
                    "name": guest_name,
                    "document_number": guest_doc,
                    "habeas_data_accepted": True,
                },
            )
            .returning(Guest.id)
        )
        guest_id = int((await db.execute(guest_stmt)).scalar_one())
    else:
        guest = Guest(
            name=guest_name,
            document_number=guest_doc,
            habeas_data_accepted=True,
        )
        db.add(guest)
        await db.flush()
        guest_id = guest.id

    group_uuid = uuid.uuid4()
    group_code = generate_group_code(group_uuid)

    # 2. Calcular tarifa de grupo con RN-01
    room_objs: list[Room] = []
    for item in rooms_input:
        r_id = int(item.get("roomId") or item.get("room_id"))
        room = await db.get(Room, r_id)
        if room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Habitación {r_id} no encontrada",
            )
        room_objs.append(room)

    nights = (check_out - check_in).days
    total_base_cap = sum(r.base_adults_capacity for r in room_objs)
    total_max_cap = sum(r.max_adults_capacity for r in room_objs)
    if adults > total_max_cap:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cantidad de adultos supera la capacidad máxima de las habitaciones seleccionadas (RN-01)",
        )

    extra_adults = max(0, adults - total_base_cap)
    extra_unit_price = room_objs[0].extra_guest_price
    extra_cost = extra_unit_price * Decimal(extra_adults) * Decimal(nights)

    room_totals: list[Decimal] = []
    for idx, room in enumerate(room_objs):
        rt = room.price_per_night * Decimal(nights)
        if idx == 0:
            rt += extra_cost
        room_totals.append(rt.quantize(Decimal("0.01")))

    total_group_price = sum(room_totals, Decimal("0.00")).quantize(Decimal("0.01"))
    if payment_option == "full":
        group_paid = total_group_price
        final_payment_status = "paid"
    elif payment_option == "deposit":
        group_paid = (total_group_price / Decimal("2")).quantize(Decimal("0.01"))
        final_payment_status = "partial"
    else:
        group_paid = Decimal("0.00")
        final_payment_status = "pending"

    confirmed_bookings: list[Booking] = []
    try:
        for idx, item in enumerate(rooms_input):
            room = room_objs[idx]
            lock_token = item.get("lockToken") or item.get("booking_id")
            room_total = room_totals[idx]
            room_paid = (
                group_paid
                if len(room_objs) == 1
                else (group_paid * (room_total / total_group_price)).quantize(Decimal("0.01"))
            )

            existing_lock: Booking | None = None
            if lock_token is not None and str(lock_token).isdigit():
                candidate = await db.get(Booking, int(lock_token))
                if (
                    candidate is not None
                    and candidate.room_id == room.id
                    and candidate.status == BookingStatus.BLOQUEADA_TEMPORAL.value
                ):
                    existing_lock = candidate

            if existing_lock is None:
                # Buscar si hay un bloqueo temporal activo de esa habitación en las mismas fechas
                lock_q = await db.execute(
                    select(Booking).where(
                        Booking.room_id == room.id,
                        Booking.check_in == check_in,
                        Booking.check_out == check_out,
                        Booking.status == BookingStatus.BLOQUEADA_TEMPORAL.value,
                    )
                )
                existing_lock = lock_q.scalars().first()

            if existing_lock is not None:
                existing_lock.guest_id = guest_id
                existing_lock.status = BookingStatus.CONFIRMADA.value
                existing_lock.expires_at = None
                existing_lock.payment_status = final_payment_status
                existing_lock.adults = adults
                existing_lock.children = children
                existing_lock.with_pet = has_pet
                existing_lock.total_price = room_total
                existing_lock.paid_amount = room_paid
                existing_lock.group_code = group_code
                existing_lock.reservation_group_id = group_uuid
                existing_lock.companions = companions_in or group_code
                confirmed_bookings.append(existing_lock)
            else:
                # Expirar candados vencidos antes de insertar
                await db.execute(
                    update(Booking)
                    .where(
                        Booking.room_id == room.id,
                        Booking.status == BookingStatus.BLOQUEADA_TEMPORAL.value,
                        Booking.expires_at <= func.now(),
                    )
                    .values(status=BookingStatus.EXPIRADA.value)
                )
                new_b = Booking(
                    guest_id=guest_id,
                    room_id=room.id,
                    check_in=check_in,
                    check_out=check_out,
                    status=BookingStatus.CONFIRMADA.value,
                    expires_at=None,
                    payment_status=final_payment_status,
                    adults=adults,
                    children=children,
                    with_pet=has_pet,
                    total_price=room_total,
                    paid_amount=room_paid,
                    source=source,
                    group_code=group_code,
                    reservation_group_id=group_uuid,
                    companions=companions_in or group_code,
                )
                db.add(new_b)
                await db.flush()
                confirmed_bookings.append(new_b)

        await record_audit(
            db=db,
            actor=wa_id or guest_name,
            action="BOOKING_CONFIRMED",
            entity="booking",
            entity_id=group_code,
            details={
                "group_code": group_code,
                "room_ids": [r.id for r in room_objs],
                "total_price": str(total_group_price),
                "paid_amount": str(group_paid),
                "payment_status": final_payment_status,
            },
        )
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto de disponibilidad GiST al confirmar la reserva (RN-02)",
        ) from exc

    remaining = (total_group_price - group_paid).quantize(Decimal("0.01"))
    publish_pms_event("booking.confirmed", {"code": group_code})
    return {
        "reservationGroupId": str(group_uuid),
        "code": group_code,
        "totalPrice": float(total_group_price),
        "bookingIds": [b.id for b in confirmed_bookings],
        "roomIds": [r.id for r in room_objs],
        "status": BookingStatus.CONFIRMADA.value,
        "paymentStatus": final_payment_status,
        "paidAmount": float(group_paid),
        "remainingAmount": float(remaining),
    }


@router.get("/api/bookings/group/{code}", status_code=status.HTTP_200_OK)
@router.get("/api/v1/bookings/group/{code}", status_code=status.HTTP_200_OK)
async def get_booking_group_by_code(
    code: str,
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Consulta detalles de una reserva grupal por código TS-XXXX e incluye política de reembolso RN-03."""
    bookings = await _find_bookings_by_code(db, code)
    if not bookings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró reserva con código {code}",
        )

    first = bookings[0]
    guest = await db.get(Guest, first.guest_id)
    room_summaries: list[dict[str, Any]] = []
    total_price = Decimal("0.00")
    paid_amount = Decimal("0.00")

    for b in bookings:
        total_price += b.total_price
        paid_amount += b.paid_amount
        room = await db.get(Room, b.room_id)
        if room is not None:
            room_summaries.append(
                {
                    "id": room.id,
                    "number": room.number,
                    "name": room.name,
                    "type": room.type,
                    "pricePerNight": float(room.price_per_night),
                }
            )

    pending_balance = (total_price - paid_amount).quantize(Decimal("0.01"))
    nights = (first.check_out - first.check_in).days
    hours_until, refund_pct, estimated_refund, policy_desc = _calculate_rn03_refund(
        first.check_in, paid_amount
    )

    is_active = first.status in (
        BookingStatus.CONFIRMADA.value,
        BookingStatus.BLOQUEADA_TEMPORAL.value,
        BookingStatus.EN_CURSO.value,
    )
    can_cancel = is_active and first.status != BookingStatus.CANCELADA.value
    can_pay_remaining = (
        is_active
        and first.payment_status == "partial"
        and pending_balance > Decimal("0.00")
    )

    status_labels = {
        BookingStatus.CONFIRMADA.value: "Confirmada",
        BookingStatus.BLOQUEADA_TEMPORAL.value: "Pendiente de pago",
        BookingStatus.EN_CURSO.value: "En curso",
        BookingStatus.CANCELADA.value: "Cancelada",
        BookingStatus.EXPIRADA.value: "Expirada",
    }
    payment_labels = {
        "paid": "Pagada",
        "partial": "Abono 50%",
        "pending": "Pendiente de pago",
        "refunded": "Reembolsada",
    }

    resolved_code = first.group_code or f"TS-{first.id}"
    return {
        "code": resolved_code,
        "reservationGroupId": str(first.reservation_group_id) if first.reservation_group_id else None,
        "guestName": guest.name if guest else None,
        "guestPhone": guest.whatsapp_phone if guest else None,
        "guestDocument": guest.document_number if guest else None,
        "checkIn": first.check_in.isoformat(),
        "checkOut": first.check_out.isoformat(),
        "nights": nights,
        "adults": first.adults,
        "children": first.children,
        "companions": first.companions,
        "withPet": first.with_pet,
        "totalPrice": float(total_price),
        "paidAmount": float(paid_amount),
        "pendingBalance": float(pending_balance),
        "status": first.status,
        "statusLabel": status_labels.get(first.status, first.status),
        "paymentStatus": first.payment_status,
        "paymentStatusLabel": payment_labels.get(first.payment_status, first.payment_status),
        "rooms": room_summaries,
        "canCancel": can_cancel,
        "canPayRemaining": can_pay_remaining,
        "refundPolicy": {
            "hoursUntilCheckin": hours_until,
            "refundPercentage": refund_pct,
            "estimatedRefund": float(estimated_refund),
            "policyDescription": policy_desc,
        },
    }


@router.post("/api/bookings/group/{code}/cancellation", status_code=status.HTTP_200_OK)
@router.post("/api/v1/bookings/group/{code}/cancellation", status_code=status.HTTP_200_OK)
async def cancel_booking_group(
    code: str,
    principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Cancela la reserva grupal pasando a CANCELADA, libera el índice GiST y calcula reembolso RN-03."""
    bookings = await _find_bookings_by_code(db, code)
    if not bookings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró reserva con código {code}",
        )

    first = bookings[0]
    if first.status == BookingStatus.CANCELADA.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta reserva ya se encuentra cancelada",
        )

    total_price = sum((b.total_price for b in bookings), Decimal("0.00"))
    paid_amount = sum((b.paid_amount for b in bookings), Decimal("0.00"))
    _, refund_pct, refund_amount, policy_desc = _calculate_rn03_refund(
        first.check_in, paid_amount
    )

    new_payment_status = (
        "refunded"
        if paid_amount > Decimal("0.00") and refund_pct > 0
        else first.payment_status
    )

    freed_rooms: list[str] = []
    for b in bookings:
        b.status = BookingStatus.CANCELADA.value
        b.payment_status = new_payment_status
        room = await db.get(Room, b.room_id)
        if room is not None:
            freed_rooms.append(room.number)

    resolved_code = first.group_code or code.upper()
    await record_audit(
        db=db,
        actor=resolve_actor_name(principal, "guest_or_reception"),
        action="BOOKING_CANCELLED",
        entity="booking",
        entity_id=resolved_code,
        details={
            "refund_percentage": refund_pct,
            "refund_amount": str(refund_amount),
            "freed_rooms": freed_rooms,
        },
    )
    await db.commit()
    publish_pms_event("booking.cancelled", {"code": resolved_code})

    return {
        "code": resolved_code,
        "reservationGroupId": str(first.reservation_group_id) if first.reservation_group_id else None,
        "status": BookingStatus.CANCELADA.value,
        "paymentStatus": new_payment_status,
        "totalPrice": float(total_price),
        "paidAmount": float(paid_amount),
        "refundPercentage": refund_pct,
        "refundAmount": float(refund_amount),
        "policyDescription": policy_desc,
        "cancelledBookingIds": [b.id for b in bookings],
        "freedRoomNumbers": freed_rooms,
        "cancelledAt": datetime.now(timezone.utc).isoformat(),
        "message": "Tu reserva ha sido cancelada exitosamente y las habitaciones han sido liberadas.",
    }


@router.post("/api/bookings/group/{code}/pay-remaining", status_code=status.HTTP_200_OK)
@router.post("/api/v1/bookings/group/{code}/pay-remaining", status_code=status.HTTP_200_OK)
async def pay_remaining_balance(
    code: str,
    _principal: User | str = Depends(
        require_service_or_role(
            [UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value]
        )
    ),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Liquida el 50% de saldo pendiente actualizando payment_status a 'paid' y registrando en audit_log."""
    bookings = await _find_bookings_by_code(db, code)
    if not bookings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró reserva con código {code}",
        )

    first = bookings[0]
    if first.status == BookingStatus.CANCELADA.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede pagar saldo de una reserva cancelada",
        )

    total_price = Decimal("0.00")
    for b in bookings:
        b.payment_status = "paid"
        b.paid_amount = b.total_price
        total_price += b.total_price

    resolved_code = first.group_code or code.upper()
    await record_audit(
        db=db,
        actor="guest_or_reception",
        action="BOOKING_PAY_REMAINING",
        entity="booking",
        entity_id=resolved_code,
        details={"total_paid": str(total_price)},
    )
    await db.commit()

    return {
        "reservationGroupId": str(first.reservation_group_id) if first.reservation_group_id else None,
        "code": resolved_code,
        "totalPrice": float(total_price),
        "bookingIds": [b.id for b in bookings],
        "roomIds": [b.room_id for b in bookings],
        "status": first.status,
        "paymentStatus": "paid",
        "paidAmount": float(total_price),
        "remainingAmount": 0.0,
    }


@router.get("/api/bookings", status_code=status.HTTP_200_OK)
@router.get("/api/v1/bookings", status_code=status.HTTP_200_OK)
async def list_bookings(
    _current_user: User = Depends(
        require_role([UserRole.ADMINISTRADOR.value, UserRole.RECEPCIONISTA.value])
    ),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Lista todas las reservas con datos del huésped y habitación para operación web (JWT)."""
    res = await db.execute(select(Booking).order_by(Booking.id.desc()))
    bookings = res.scalars().all()
    rows: list[dict[str, Any]] = []
    for b in bookings:
        guest = await db.get(Guest, b.guest_id)
        room = await db.get(Room, b.room_id)
        rows.append(
            {
                "id": b.id,
                "reservationGroupId": str(b.reservation_group_id) if b.reservation_group_id else None,
                "bookingCode": b.group_code or f"TS-{b.id}",
                "status": b.status,
                "paymentStatus": b.payment_status,
                "paidAmount": float(b.paid_amount),
                "checkIn": b.check_in.isoformat(),
                "checkOut": b.check_out.isoformat(),
                "roomId": b.room_id,
                "roomNumber": room.number if room else None,
                "roomName": room.name if room else None,
                "guestId": b.guest_id,
                "guestName": guest.name if guest else None,
                "guestPhone": guest.whatsapp_phone if guest else None,
                "guestDocument": guest.document_number if guest else None,
                "adults": b.adults,
                "children": b.children,
                "withPet": b.with_pet,
                "companions": b.companions,
                "totalPrice": float(b.total_price),
                "source": b.source,
                "expiresAt": b.expires_at.isoformat() if b.expires_at else None,
                "createdAt": b.created_at.isoformat() if b.created_at else None,
            }
        )
    return rows


sys.modules.setdefault("routers.n8n_compat", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.n8n_compat", sys.modules[__name__])
