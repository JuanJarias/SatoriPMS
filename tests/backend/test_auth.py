"""Pruebas de autenticación JWT, control de acceso RBAC (RN-10) y auditoría inmutable (Lote M1)."""

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import select

from apps.api.core.database import AsyncSessionLocal
from apps.api.core.security import hash_password
from apps.api.main import app
from apps.api.models import AuditLog, User, UserRole


async def _ensure_test_users() -> None:
    """Garantiza que existan los usuarios de prueba Administrador y Recepcionista en PostgreSQL."""
    async with AsyncSessionLocal() as session:
        for uname, pwd, role, full_name in [
            ("admin", "admin123", UserRole.ADMINISTRADOR.value, "Administrador Torre Satori"),
            ("recepcion", "recepcion123", UserRole.RECEPCIONISTA.value, "Recepción Torre Satori"),
        ]:
            res = await session.execute(select(User).where(User.username == uname))
            user = res.scalar_one_or_none()
            if user is None:
                session.add(
                    User(
                        username=uname,
                        password_hash=hash_password(pwd),
                        role=role,
                        name=full_name,
                        active=True,
                    )
                )
            else:
                user.password_hash = hash_password(pwd)
                user.role = role
                user.active = True
        await session.commit()


@pytest.mark.asyncio
async def test_login_success_returns_jwt_and_records_audit() -> None:
    """Verifica que un login válido retorne HTTP 200 con token JWT, permita consultar /me y registre LOGIN_SUCCESS en audit_log."""
    await _ensure_test_users()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert login_res.status_code == 200
        data = login_res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "Administrador"
        assert data["username"] == "admin"

        token = data["access_token"]
        me_res = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_res.status_code == 200
        assert me_res.json()["role"] == "Administrador"

    async with AsyncSessionLocal() as session:
        audit_res = await session.execute(
            select(AuditLog)
            .where(
                AuditLog.actor_username == "admin",
                AuditLog.action == "LOGIN_SUCCESS",
            )
            .order_by(AuditLog.id.desc())
        )
        latest_audit = audit_res.scalars().first()
        assert latest_audit is not None
        assert latest_audit.entity == "system_users"


@pytest.mark.asyncio
async def test_login_failure_and_tampered_token_return_401() -> None:
    """Verifica que credenciales erróneas o un JWT alterado retornen HTTP 401 y registren LOGIN_FAILED sin exponer la clave."""
    await _ensure_test_users()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        bad_res = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "clave_incorrecta_999"},
        )
        assert bad_res.status_code == 401

        tampered_res = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer token.falso.alterado"},
        )
        assert tampered_res.status_code == 401

    async with AsyncSessionLocal() as session:
        audit_res = await session.execute(
            select(AuditLog)
            .where(
                AuditLog.actor_username == "admin",
                AuditLog.action == "LOGIN_FAILED",
            )
            .order_by(AuditLog.id.desc())
        )
        failed_audit = audit_res.scalars().first()
        assert failed_audit is not None
        assert "clave_incorrecta_999" not in (failed_audit.details_json or "")


@pytest.mark.asyncio
async def test_receptionist_accessing_admin_function_receives_403() -> None:
    """Verifica que Recepcionista acceda a /me (200) pero reciba HTTP 403 Forbidden en ruta exclusiva de Administrador (/audit-logs)."""
    await _ensure_test_users()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        recep_login = await client.post(
            "/api/v1/auth/login",
            json={"username": "recepcion", "password": "recepcion123"},
        )
        assert recep_login.status_code == 200
        recep_token = recep_login.json()["access_token"]

        # 1. /api/v1/auth/me permite ['Administrador', 'Recepcionista'] -> 200 OK
        me_res = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {recep_token}"},
        )
        assert me_res.status_code == 200
        assert me_res.json()["role"] == "Recepcionista"

        # 2. /api/v1/auth/audit-logs exige ['Administrador'] -> Recepcionista recibe 403 Forbidden
        forbidden_res = await client.get(
            "/api/v1/auth/audit-logs",
            headers={"Authorization": f"Bearer {recep_token}"},
        )
        assert forbidden_res.status_code == 403

        # 3. Administrador sí accede a /api/v1/auth/audit-logs -> 200 OK
        admin_login = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        admin_token = admin_login.json()["access_token"]
        admin_logs_res = await client.get(
            "/api/v1/auth/audit-logs",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert admin_logs_res.status_code == 200
        assert len(admin_logs_res.json()) >= 1
