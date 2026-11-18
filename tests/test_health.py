"""Pruebas del endpoint de salud /api/v1/health y extensión btree_gist (Lote M0)."""

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import text

from apps.api.core.database import AsyncSessionLocal
from apps.api.main import app


@pytest.mark.asyncio
async def test_health_endpoint_returns_200_and_db_connected() -> None:
    """Verifica que /api/v1/health responda HTTP 200 y confirme conexión activa a PostgreSQL 16."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "connected"}


@pytest.mark.asyncio
async def test_btree_gist_extension_and_nine_rooms_seeded() -> None:
    """Verifica que la extensión btree_gist esté activa y las 9 habitaciones estén cargadas."""
    async with AsyncSessionLocal() as session:
        ext_res = await session.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'btree_gist'")
        )
        assert ext_res.scalar_one_or_none() == "btree_gist"

        rooms_res = await session.execute(text("SELECT COUNT(*) FROM room"))
        assert rooms_res.scalar_one() == 9
