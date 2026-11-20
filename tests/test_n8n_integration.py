"""Pruebas de integración del flujo n8n V10 (cero Redis, sesiones PostgreSQL, bloqueo, confirmación TS-XXXX y RN-03)."""

import json
from pathlib import Path

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import delete, select

from apps.api.core.config import settings
from apps.api.core.database import AsyncSessionLocal
from apps.api.main import app
from apps.api.models import Booking, Conversation, Room

_SVC_HEADERS = {"X-Service-Key": settings.N8N_INTERNAL_API_KEY}


def test_n8n_v10_workflow_has_zero_redis_nodes() -> None:
    """Verifica que flows/n8n/V10_ChatbotReservas.json haya eliminado los 7 nodos Redis y use /api/v1/conversations/session/."""
    flow_path = Path(__file__).resolve().parents[1] / "flows" / "n8n" / "V10_ChatbotReservas.json"
    assert flow_path.exists()
    data = json.loads(flow_path.read_text(encoding="utf-8"))

    redis_nodes = [
        n["name"]
        for n in data.get("nodes", [])
        if "redis" in n.get("type", "").lower()
    ]
    assert redis_nodes == []

    session_http_nodes = [
        n["name"]
        for n in data.get("nodes", [])
        if n.get("type") == "n8n-nodes-base.httpRequest"
        and "/api/v1/conversations/session/" in str(n.get("parameters", {}).get("url", ""))
    ]
    assert len(session_http_nodes) == 7


@pytest.mark.asyncio
async def test_postgresql_conversation_session_crud_and_agent_escalation() -> None:
    """Verifica el ciclo GET/PUT/DELETE de sesiones en PostgreSQL y el escalamiento a agente humano."""
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Conversation))
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as anon_client:
        unauth_res = await anon_client.get("/api/v1/conversations/session/session:573110001122")
        assert unauth_res.status_code == 401

        bad_esc = await anon_client.post(
            "/api/notifications/agent-request",
            json={"wa_id": "573110001122", "name": "Carlos Restrepo"},
        )
        assert bad_esc.status_code == 401

        login_res = await anon_client.post(
            "/api/v1/auth/login",
            json={"username": "recepcion", "password": "recepcion123"},
        )
        assert login_res.status_code == 200
        jwt_headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    async with AsyncClient(transport=transport, base_url="http://test", headers=_SVC_HEADERS) as client:
        # 1. Consulta inicial de sesión inexistente -> value: None
        get_empty = await client.get("/api/v1/conversations/session/session:573110001122")
        assert get_empty.status_code == 200
        assert get_empty.json()["value"] is None

        # 2. Guardar sesión desde n8n -> PUT
        session_obj = {
            "state": "reserva",
            "step": "fechas",
            "agent_active": False,
            "wa_id": "573110001122",
            "sender_name": "Carlos Restrepo",
            "last_activity": 1795115000000,
        }
        put_res = await client.put(
            "/api/v1/conversations/session/session:573110001122",
            json={"value": json.dumps(session_obj), "ttl": 660},
        )
        assert put_res.status_code == 200
        assert put_res.json()["status"] == "saved"

        # 3. Recuperar sesión -> value contiene el JSON exacto que espera n8n V10
        get_saved = await client.get("/api/v1/conversations/session/session:573110001122")
        assert get_saved.status_code == 200
        loaded = json.loads(get_saved.json()["value"])
        assert loaded["step"] == "fechas"
        assert loaded["sender_name"] == "Carlos Restrepo"

        # 4. Escalar a agente humano -> POST /api/notifications/agent-request
        esc_res = await client.post(
            "/api/notifications/agent-request",
            json={"wa_id": "573110001122", "name": "Carlos Restrepo"},
        )
        assert esc_res.status_code == 200
        assert esc_res.json()["agent_available"] is True

        # 5. Listar bandeja de conversaciones -> GET /api/conversations (requiere JWT web)
        list_res = await client.get("/api/conversations", headers=jwt_headers)
        assert list_res.status_code == 200
        assert len(list_res.json()) == 1
        assert list_res.json()[0]["status"] == "escalated"

        # 6. Borrar sesión inactiva -> DELETE
        del_res = await client.delete("/api/v1/conversations/session/session:573110001122")
        assert del_res.status_code == 200
        assert del_res.json()["deleted"] is True


@pytest.mark.asyncio
async def test_n8n_v10_end_to_end_booking_lifecycle_and_rn03_cancellation() -> None:
    """Simula el recorrido completo de n8n V10: disponibilidad -> lock -> confirm (TS-XXXX) -> group -> pay-remaining -> cancellation (RN-03)."""
    async with AsyncSessionLocal() as session:
        room_res = await session.execute(select(Room).where(Room.number == "3"))
        room = room_res.scalar_one()
        await session.execute(delete(Booking).where(Booking.room_id == room.id))
        await session.commit()
        room_id = room.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=_SVC_HEADERS) as client:
        # 1. Disponibilidad en formato camelCase de n8n V10
        avail_res = await client.get(
            "/api/rooms/availability",
            params={
                "checkIn": "2026-12-25",
                "checkOut": "2026-12-27",
                "adults": 2,
                "children": 0,
                "pet": "false",
            },
        )
        assert avail_res.status_code == 200
        room_3 = next(r for r in avail_res.json() if r["number"] == "3")
        assert room_3["pricePerNight"] == 170000.0

        # 2. Bloqueo temporal de 15 min desde n8n V10
        lock_res = await client.post(
            "/api/bookings/lock",
            json={
                "waId": "573120009988",
                "roomId": room_id,
                "checkIn": "2026-12-25",
                "checkOut": "2026-12-27",
            },
        )
        assert lock_res.status_code == 200
        lock_token = lock_res.json()["lockToken"]
        assert lock_res.json()["ttlSeconds"] == 900

        # 3. Confirmación de reserva con abono del 50% (deposit)
        confirm_res = await client.post(
            "/api/bookings/confirm",
            json={
                "waId": "573120009988",
                "guestName": "Valentina Gómez",
                "guestDocument": "1054862079",
                "checkIn": "2026-12-25",
                "checkOut": "2026-12-27",
                "adults": 2,
                "children": 0,
                "hasPet": False,
                "rooms": [{"roomId": room_id, "lockToken": lock_token}],
                "paymentOption": "deposit",
            },
        )
        assert confirm_res.status_code == 200
        c_data = confirm_res.json()
        code = c_data["code"]
        assert code.startswith("TS-")
        # El chatbot deja la reserva pendiente de pago: solo el pago aprobado la confirma
        assert c_data["status"] == "pending_payment"
        assert c_data["paymentStatus"] == "pending"
        assert c_data["paidAmount"] == 0.0

        doc = {"X-Guest-Document": "1054862079"}

        # 4. El pago aprobado de la pasarela confirma con el 50% abonado (Wompi, vía n8n)
        pay_ext = await client.post(
            f"/api/bookings/group/{code}/confirm-external-payment",
            json={"paymentOption": "deposit", "transactionId": "txn-e2e-lifecycle-1"},
        )
        assert pay_ext.status_code == 200
        assert pay_ext.json()["status"] == "confirmed"
        assert pay_ext.json()["paymentStatus"] == "partial"
        assert pay_ext.json()["paidAmount"] == 170000.0
        assert pay_ext.json()["remainingAmount"] == 170000.0

        # 5. Consulta por código TS-XXXX con el documento del titular
        group_res = await client.get(f"/api/bookings/group/{code}", headers=doc)
        assert group_res.status_code == 200
        assert group_res.json()["canPayRemaining"] is True
        assert group_res.json()["refundPolicy"]["refundPercentage"] == 100
        assert group_res.json()["guestDocument"] == "******2079"

        # 6. Pago del saldo restante
        pay_rem_res = await client.post(
            f"/api/bookings/group/{code}/pay-remaining", json={"document": "1054862079"}
        )
        assert pay_rem_res.status_code == 200
        assert pay_rem_res.json()["paymentStatus"] == "paid"
        assert pay_rem_res.json()["remainingAmount"] == 0.0

        # 7. Cancelación con cálculo de reembolso RN-03 (>72h antes de 2026-12-25 -> 100% de 340.000)
        cancel_res = await client.post(
            f"/api/bookings/group/{code}/cancellation", json={"document": "1054862079"}
        )
        assert cancel_res.status_code == 200
        cancel_data = cancel_res.json()
        assert cancel_data["status"] == "cancelled"
        assert cancel_data["refundPercentage"] == 100
        assert cancel_data["refundAmount"] == 340000.0
        assert "3" in cancel_data["freedRoomNumbers"]
