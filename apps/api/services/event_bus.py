"""Bus de eventos en proceso para transmisión en tiempo real vía SSE (HU-03)."""

import asyncio
from datetime import datetime, timezone
import json
import sys
from typing import Any


class PmsEventBus:
    """Publicador/suscriptor asíncrono basado en colas por cliente conectado."""

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[str]] = set()

    def subscribe(self) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=100)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[str]) -> None:
        self._subscribers.discard(queue)

    def publish(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        envelope = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload or {},
        }
        frame = f"event: {event_type}\ndata: {json.dumps(envelope, ensure_ascii=False)}\n\n"
        stale: list[asyncio.Queue[str]] = []
        for q in list(self._subscribers):
            try:
                q.put_nowait(frame)
            except asyncio.QueueFull:
                stale.append(q)
        for q in stale:
            self._subscribers.discard(q)


event_bus = PmsEventBus()


def publish_pms_event(event_type: str, payload: dict[str, Any] | None = None) -> None:
    """Emite un evento SSE a todos los tableros web suscritos."""
    event_bus.publish(event_type=event_type, payload=payload)


sys.modules.setdefault("services.event_bus", sys.modules[__name__])
sys.modules.setdefault("apps.api.services.event_bus", sys.modules[__name__])
