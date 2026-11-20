"""Router Server-Sent Events (SSE) para sincronización en tiempo real de calendario y tablero (HU-03)."""

import asyncio
from collections.abc import AsyncGenerator
import json
import sys

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from core.database import get_db
    from dependencies.auth import get_current_user, oauth2_scheme
    from services.event_bus import event_bus
except ImportError:
    from apps.api.core.database import get_db
    from apps.api.dependencies.auth import get_current_user, oauth2_scheme
    from apps.api.services.event_bus import event_bus

router = APIRouter(prefix="/api/v1/events", tags=["Realtime SSE (HU-03)"])


@router.get("/stream", status_code=status.HTTP_200_OK)
async def stream_pms_events(
    request: Request,
    token: str | None = Query(default=None, description="JWT opcional para EventSource"),
    once: bool = Query(default=False, description="Emite evento inicial y cierra"),
    bearer_token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Canal SSE autenticado que notifica cambios de reservas, bloqueos y habitaciones en tiempo real."""
    resolved_token = bearer_token or token
    if not resolved_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token JWT requerido para suscripción SSE",
        )
    await get_current_user(token=resolved_token, db=db)

    queue = event_bus.subscribe()

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            hello = json.dumps({"status": "connected"})
            yield f"event: connected\ndata: {hello}\n\n"
            if once:
                return
            while True:
                if await request.is_disconnected():
                    break
                try:
                    frame = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield frame
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            event_bus.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


sys.modules.setdefault("routers.events_stream", sys.modules[__name__])
sys.modules.setdefault("apps.api.routers.events_stream", sys.modules[__name__])
