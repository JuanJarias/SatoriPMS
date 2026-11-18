"""Configuración de entorno mediante Pydantic Settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


_ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    """Variables de configuración del backend Torre Satori PMS."""

    PROJECT_NAME: str = "Torre Satori PMS API"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    PORT: int = 8080

    DATABASE_URL: str = (
        "postgresql+psycopg://satori:satori_dev@localhost:5432/satoripms"
    )
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=str(_ROOT_ENV) if _ROOT_ENV.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def async_database_url(self) -> str:
        """Garantiza que el esquema de URL use el driver psycopg (asíncrono en SQLAlchemy 2.0)."""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace(
                "postgresql://", "postgresql+psycopg://", 1
            )
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace(
                "postgres://", "postgresql+psycopg://", 1
            )
        return self.DATABASE_URL


settings = Settings()
