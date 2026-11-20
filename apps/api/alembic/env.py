"""Entorno asíncrono de Alembic para SQLAlchemy 2.0 y PostgreSQL 16."""

import asyncio
from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

_API_DIR = str(Path(__file__).resolve().parents[1])
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from core.config import settings
from models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.async_database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo offline (generación de SQL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Ejecuta las migraciones sobre una conexión activa."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Crea un motor asíncrono y ejecuta las migraciones en el bucle de eventos."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Punto de entrada para migraciones en línea."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
