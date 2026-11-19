"""Motor y sesión asíncrona de SQLAlchemy 2.0 para PostgreSQL 16."""

from collections.abc import AsyncGenerator
import sys

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

try:
    from core.config import settings
except ImportError:
    from apps.api.core.config import settings


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos relacionales."""


engine = create_async_engine(
    settings.async_database_url,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=20,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia de FastAPI que provee una sesión asíncrona por petición."""
    async with AsyncSessionLocal() as session:
        yield session


# Alias de módulo para evitar doble registro de metadatos entre ejecuciones desde raíz o apps/api
sys.modules.setdefault("core.database", sys.modules[__name__])
sys.modules.setdefault("apps.api.core.database", sys.modules[__name__])
