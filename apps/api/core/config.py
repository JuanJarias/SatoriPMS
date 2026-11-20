"""Configuración de entorno mediante Pydantic Settings."""

from pathlib import Path
import sys
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> str:
    """Busca el archivo .env en directorios padre de forma segura (local y Docker /app)."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / ".env"
        if candidate.is_file():
            return str(candidate)
    return ".env"


class Settings(BaseSettings):
    """Variables de configuración del backend Torre Satori PMS."""

    PROJECT_NAME: str = "Torre Satori PMS API"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    PORT: int = 8080

    JWT_SECRET: str = "satori_dev_jwt_secret_key_minimo_32_caracteres_2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 480

    PAYMENT_WEBHOOK_SECRET: str = "satori_dev_payment_webhook_secret_hmac_2026"
    PAYMENT_PROVIDER: str = "sandbox"
    WOMPI_PUBLIC_KEY: str = ""
    WOMPI_PRIVATE_KEY: str = ""
    WOMPI_EVENTS_SECRET: str = ""
    WOMPI_INTEGRITY_SECRET: str = ""
    WOMPI_ENVIRONMENT: str = "sandbox"

    # Llave que n8n envía en X-Service-Key. Se acepta con el nombre SATORI_SERVICE_KEY
    # (el que usa el flujo y el .env del repositorio) o con el nombre original.
    N8N_INTERNAL_API_KEY: str = Field(
        default="satori_dev_n8n_internal_key_2026",
        validation_alias=AliasChoices("SATORI_SERVICE_KEY", "N8N_INTERNAL_API_KEY"),
    )
    N8N_EXPIRED_WEBHOOK_URL: str = ""

    GOOGLE_PLACES_API_KEY: str = ""
    GOOGLE_PLACE_ID: str = "ChIJQRr4FV2zOY4RvqM_8_EfzsY"
    GOOGLE_REVIEWS_URL: str = (
        "https://www.google.com/travel/hotels/entity/CgsIvsf-mZ_-h-fGARAB/reviews"
    )

    SENTRY_DSN: str = ""

    DATABASE_URL: str = (
        "postgresql+psycopg://satori:satori_dev@localhost:5432/satoripms"
    )
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
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

sys.modules.setdefault("core.config", sys.modules[__name__])
sys.modules.setdefault("apps.api.core.config", sys.modules[__name__])
