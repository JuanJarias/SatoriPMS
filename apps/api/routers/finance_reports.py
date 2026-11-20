"""Router de egresos operativos, resumen financiero real y exportación Excel (.xlsx) con openpyxl (Lote P5)."""

from datetime import date, datetime, timezone
from decimal import Decimal
from io import BytesIO
import sys
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from dependencies.auth import require_role
    from models.booking import Booking
    from models.guest import Guest
    from models.operations import Expense, FolioCharge, Product
    from models.room import Room
    from models.user import User, UserRole
    from services.audit_service import record_audit
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.dependencies.auth import require_role
    from apps.api.models.booking import Booking
    from apps.api.models.guest import Guest
    from apps.api.models.operations import Expense, FolioCharge, Product
    from apps.api.models.room import Room
    from apps.api.models.user import User, UserRole
    from apps.api.services.audit_service import record_audit

router = APIRouter(tags=["Finanzas, Egresos y Reportes Excel (P5)"])


def _serialize_expense(e: Expense) -> dict[str, Any]:
    return {
        "id": str(e.id),
        "numericId": e.id,
        "date": e.expense_date.isoformat(),
        "amount": float(e.amount),
        "category": e.category,
        "desc": e.description,
        "voided": e.voided,
        "voidedReason": e.voided_reason,
        "createdBy": e.created_by,
    }


@router.get("/api/v1/expenses", status_code=status.HTTP_200_OK)
async def list_expenses(
    _current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Lista los comprobantes de egreso ordenados del más reciente al más antiguo."""
    res = await db.execute(
        select(Expense).order_by(Expense.expense_date.desc(), Expense.id.desc())
    )
    return [_serialize_expense(e) for e in res.scalars().all()]


@router.post("/api/v1/expenses", status_code=status.HTTP_201_CREATED)
async def create_expense(
    body: dict[str, Any] = Body(...),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Registra un egreso operativo en PostgreSQL y deja traza en audit_log."""
    raw_amount = body.get("amount")
    desc = str(body.get("desc") or body.get("description") or "").strip()
    category = str(body.get("category") or "Otros").strip()
    raw_date = body.get("date") or body.get("expense_date") or date.today().isoformat()
    if not desc or raw_amount is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Descripción y monto son obligatorios")
    amount = Decimal(str(raw_amount)).quantize(Decimal("0.01"))
    if amount <= Decimal("0.00"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El monto debe ser positivo")

    exp = Expense(
        expense_date=date.fromisoformat(str(raw_date)),
        amount=amount,
        category=category,
        description=desc,
        voided=False,
        created_by=current_user.username,
    )
    db.add(exp)
    await db.flush()
    await record_audit(
        db=db,
        actor=current_user.username,
        action="EXPENSE_CREATED",
        entity="expense",
        entity_id=str(exp.id),
        details={"amount": str(amount), "category": category, "desc": desc},
    )
    await db.commit()
    await db.refresh(exp)
    return _serialize_expense(exp)


@router.post("/api/v1/expenses/{expense_id}/void", status_code=status.HTTP_200_OK)
async def void_expense(
    expense_id: int,
    body: dict[str, Any] | None = Body(default=None),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Anula lógicamente un egreso sin borrarlo para preservar trazabilidad contable."""
    exp = await db.get(Expense, expense_id)
    if exp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Egreso no encontrado")
    exp.voided = True
    exp.voided_reason = str((body or {}).get("reason") or "Anulado por Administración")
    await record_audit(
        db=db,
        actor=current_user.username,
        action="EXPENSE_VOIDED",
        entity="expense",
        entity_id=str(exp.id),
        details={"reason": exp.voided_reason},
    )
    await db.commit()
    await db.refresh(exp)
    return _serialize_expense(exp)


@router.get("/api/v1/finance/summary", status_code=status.HTTP_200_OK)
async def get_finance_summary(
    _current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Calcula KPIs financieros y desglose de canales directamente desde PostgreSQL."""
    bookings_res = await db.execute(select(Booking))
    bookings = list(bookings_res.scalars().all())
    charges_res = await db.execute(select(FolioCharge))
    charges = list(charges_res.scalars().all())
    exp_res = await db.execute(select(Expense).where(Expense.voided.is_(False)))
    active_expenses = list(exp_res.scalars().all())

    lodging_income = sum(
        (b.paid_amount for b in bookings if b.status != "CANCELADA" and b.status != "EXPIRADA"),
        Decimal("0.00"),
    )
    charges_income = sum((c.total_amount for c in charges), Decimal("0.00"))
    total_income = (lodging_income + charges_income).quantize(Decimal("0.01"))
    total_expenses = sum((e.amount for e in active_expenses), Decimal("0.00")).quantize(Decimal("0.01"))
    net_balance = (total_income - total_expenses).quantize(Decimal("0.01"))

    channels: dict[str, dict[str, Any]] = {}
    valid_bookings = [b for b in bookings if b.status in ("CONFIRMADA", "EN_CURSO", "BLOQUEADA_TEMPORAL")]
    for b in valid_bookings:
        key = "WhatsApp" if b.source == "chatbot" else "Recepción / Web"
        entry = channels.setdefault(key, {"channel": key, "bookings": 0, "income": 0.0})
        entry["bookings"] += 1
        entry["income"] += float(b.paid_amount)

    total_valid = len(valid_bookings) or 1
    channel_rows = [
        {
            **row,
            "pct": f"{round((row['bookings'] / total_valid) * 100)}%",
        }
        for row in channels.values()
    ]

    return {
        "totalIncome": float(total_income),
        "lodgingIncome": float(lodging_income),
        "chargesIncome": float(charges_income),
        "totalExpenses": float(total_expenses),
        "netBalance": float(net_balance),
        "channels": channel_rows,
    }


@router.get("/api/v1/reports/export.xlsx", status_code=status.HTTP_200_OK)
async def export_reports_xlsx(
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR.value])),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Genera y descarga un libro Excel (.xlsx) real con openpyxl (Resumen, Reservas, Egresos e Inventario)."""
    wb = Workbook()
    header_fill = PatternFill(start_color="1F3D2B", end_color="1F3D2B", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)

    def _style_headers(ws, headers: list[str]) -> None:
        ws.append(headers)
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font

    summary = await get_finance_summary(_current_user=current_user, db=db)

    ws_sum = wb.active
    ws_sum.title = "Resumen"
    _style_headers(ws_sum, ["Indicador", "Valor (COP)"])
    ws_sum.append(["Ingresos Totales", summary["totalIncome"]])
    ws_sum.append(["Ingresos Alojamiento", summary["lodgingIncome"]])
    ws_sum.append(["Ingresos Tienda y Salgados Café", summary["chargesIncome"]])
    ws_sum.append(["Egresos Activos", summary["totalExpenses"]])
    ws_sum.append(["Utilidad Neta", summary["netBalance"]])
    ws_sum.append(["Generado por", current_user.username])

    ws_book = wb.create_sheet("Reservas")
    _style_headers(
        ws_book,
        ["ID", "Código", "Habitación", "Huésped", "Check-in", "Check-out", "Estado", "Canal", "Total", "Pagado"],
    )
    b_res = await db.execute(select(Booking).order_by(Booking.id.desc()))
    for b in b_res.scalars().all():
        room = await db.get(Room, b.room_id)
        guest = await db.get(Guest, b.guest_id)
        ws_book.append([
            b.id,
            b.group_code or f"TS-{b.id}",
            room.number if room else str(b.room_id),
            guest.name if guest else "Huésped",
            b.check_in.isoformat(),
            b.check_out.isoformat(),
            b.status,
            b.source,
            float(b.total_price),
            float(b.paid_amount),
        ])

    ws_exp = wb.create_sheet("Egresos")
    _style_headers(ws_exp, ["ID", "Fecha", "Categoría", "Descripción", "Monto", "Anulado"])
    e_res = await db.execute(select(Expense).order_by(Expense.expense_date.desc(), Expense.id.desc()))
    for e in e_res.scalars().all():
        ws_exp.append([e.id, e.expense_date.isoformat(), e.category, e.description, float(e.amount), "Sí" if e.voided else "No"])

    ws_prod = wb.create_sheet("Inventario Tienda")
    _style_headers(ws_prod, ["Código", "Producto", "Categoría", "Precio", "Stock"])
    p_res = await db.execute(select(Product).where(Product.active.is_(True)).order_by(Product.id.asc()))
    for p in p_res.scalars().all():
        ws_prod.append([p.code, p.name, p.category, float(p.price), p.stock])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="Reporte_TorreSatori_{stamp}.xlsx"'},
    )


sys.modules.setdefault("routers.finance_reports", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.finance_reports", sys.modules[__name__])
