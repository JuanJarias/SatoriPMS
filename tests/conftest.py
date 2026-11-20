"""Configuración global de pytest: aísla todas las pruebas sobre la base de datos satoripms_test."""

import os
from pathlib import Path

from alembic import command
from alembic.config import Config as AlembicConfig
import psycopg
from sqlalchemy.engine import make_url


def _resolve_env_database_url() -> str:
    """Obtiene DATABASE_URL desde entorno o archivo .env raíz sin importar core.database."""
    env_val = os.environ.get("DATABASE_URL")
    if env_val:
        return env_val

    root_env = Path(__file__).resolve().parents[1] / ".env"
    if root_env.is_file():
        for raw_line in root_env.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            if key.strip() == "DATABASE_URL":
                return val.strip().strip('"').strip("'")

    return "postgresql+psycopg://satori:satori_dev@localhost:5432/satoripms"


def _build_test_database_url() -> str:
    """Construye la URL aislada terminada en _test para proteger la base operativa."""
    explicit = os.environ.get("TEST_DATABASE_URL")
    base = explicit or _resolve_env_database_url()
    url = make_url(base)
    db_name = url.database or "satoripms"
    if not db_name.endswith("_test"):
        url = url.set(database=f"{db_name}_test")
    return url.render_as_string(hide_password=False)


def _ensure_test_database_and_schema(test_url_str: str) -> None:
    """Crea la base de datos *_test si no existe y aplica migraciones Alembic hasta head."""
    url = make_url(test_url_str)
    if not url.database or not url.database.endswith("_test"):
        raise RuntimeError(
            f"Seguridad pytest: la base de pruebas debe terminar en '_test', recibido '{url.database}'."
        )

    admin_dsn = (
        url.set(drivername="postgresql", database="postgres")
        .render_as_string(hide_password=False)
    )
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (url.database,),
            )
            if cur.fetchone() is None:
                cur.execute(f'CREATE DATABASE "{url.database}"')

    repo_root = Path(__file__).resolve().parents[1]
    alembic_ini = repo_root / "apps" / "api" / "alembic.ini"
    alembic_cfg = AlembicConfig(str(alembic_ini))
    alembic_cfg.set_main_option(
        "script_location", str(repo_root / "apps" / "api" / "alembic")
    )
    command.upgrade(alembic_cfg, "head")


def pytest_configure(config) -> None:
    """Inyecta DATABASE_URL de pruebas antes de importar módulos de FastAPI."""
    test_url = _build_test_database_url()
    os.environ["DATABASE_URL"] = test_url


def pytest_sessionstart(session) -> None:
    """Prepara la base satoripms_test y sus migraciones antes de ejecutar los casos."""
    test_url = os.environ.get("DATABASE_URL") or _build_test_database_url()
    _ensure_test_database_and_schema(test_url)
