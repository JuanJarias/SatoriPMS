"""Punto de entrada ASGI de FastAPI con APScheduler RN-02 y canal SSE (Lotes M0 y P4)."""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sys

_API_DIR = str(Path(__file__).resolve().parent)
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db

logger = logging.getLogger(__name__)
if settings.SENTRY_DSN.strip():
    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN.strip(),
            environment=settings.ENVIRONMENT,
            release=f"satoripms@{settings.VERSION}",
            send_default_pii=False,
            traces_sample_rate=0.1,
        )
    except ImportError:
        logger.warning("SENTRY_DSN definido pero sentry-sdk no está instalado.")
from routers.auth import router as auth_router
from routers.bookings import router as bookings_router
from routers.conversations import router as conversations_router
from routers.events_stream import router as events_stream_router
from routers.finance_reports import router as finance_reports_router
from routers.n8n_compat import router as n8n_compat_router
from routers.payments import router as payments_router
from routers.rooms import router as rooms_router
from routers.web_operations import router as web_operations_router
from services.expiration_service import expire_stale_booking_locks


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Inicia el job periódico de expiración de candados cada 60 s y lo detiene al apagar."""
    scheduler = AsyncIOScheduler(timezone="America/Bogota")
    scheduler.add_job(
        expire_stale_booking_locks,
        "interval",
        seconds=60,
        id="expire_booking_locks",
        replace_existing=True,
    )
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API unificada para Hotel Torre Satori (Sevilla, Valle del Cauca)",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(payments_router)
app.include_router(conversations_router)
app.include_router(events_stream_router)
app.include_router(finance_reports_router)
app.include_router(n8n_compat_router)
app.include_router(web_operations_router)


@app.get("/api/v1/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Verifica el estado del servicio ASGI y la conectividad activa con PostgreSQL 16."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible",
        ) from exc
    return {"status": "ok", "db": "connected"}
