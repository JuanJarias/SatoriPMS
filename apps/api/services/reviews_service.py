"""Servicio de consulta en vivo y caché de reseñas desde Google Places API (Lote P5)."""

from datetime import datetime, timedelta, timezone
import sys
from typing import Any

import httpx

try:
    from core.config import settings
except ImportError:
    from apps.api.core.config import settings

_CACHE_TTL = timedelta(minutes=15)
_cache_entry: dict[str, Any] | None = None
_cache_expires_at: datetime | None = None


def clear_reviews_cache() -> None:
    """Limpia la caché en memoria de reseñas (útil en pruebas o recargas forzadas)."""
    global _cache_entry, _cache_expires_at
    _cache_entry = None
    _cache_expires_at = None


def _build_distribution(reviews: list[dict[str, Any]]) -> dict[int, int]:
    dist = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for item in reviews:
        rating = int(item.get("rating") or 0)
        if rating in dist:
            dist[rating] += 1
    return dist


async def fetch_google_reviews_summary(refresh: bool = False) -> dict[str, Any]:
    """Consulta Google Places API (New) con caché TTL; nunca inventa reseñas falsas si falta la llave."""
    global _cache_entry, _cache_expires_at

    now = datetime.now(timezone.utc)
    if (
        not refresh
        and _cache_entry is not None
        and _cache_expires_at is not None
        and now < _cache_expires_at
    ):
        return _cache_entry

    api_key = settings.GOOGLE_PLACES_API_KEY.strip()
    place_id = settings.GOOGLE_PLACE_ID.strip() or "ChIJQRr4FV2zOY4RvqM_8_EfzsY"

    if not api_key:
        return {
            "placeName": "Hotel Torre Satori · Sevilla, Valle del Cauca",
            "placeId": place_id,
            "average": None,
            "total": 0,
            "distribution": {5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
            "reviews": [],
            "source": "google_places_unconfigured",
            "placesApiConfigured": False,
            "fetchedAt": now.isoformat(),
            "error": None,
        }

    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "displayName,rating,userRatingCount,reviews",
        "Accept-Language": "es",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        if _cache_entry is not None:
            return {**_cache_entry, "error": f"Usando caché tras fallo al consultar Google Places: {exc}"}
        return {
            "placeName": "Hotel Torre Satori · Sevilla, Valle del Cauca",
            "placeId": place_id,
            "average": None,
            "total": 0,
            "distribution": {5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
            "reviews": [],
            "source": "google_places_error",
            "placesApiConfigured": True,
            "fetchedAt": now.isoformat(),
            "error": f"No fue posible consultar Google Places API: {exc}",
        }

    display_name = (data.get("displayName") or {}).get("text") or "Hotel Torre Satori · Sevilla, Valle del Cauca"
    raw_reviews = data.get("reviews") or []
    normalized_reviews: list[dict[str, Any]] = []
    for idx, rev in enumerate(raw_reviews, start=1):
        author = rev.get("authorAttribution") or {}
        text_obj = rev.get("text") or rev.get("originalText") or {}
        normalized_reviews.append(
            {
                "id": idx,
                "authorName": author.get("displayName") or "Huésped de Google",
                "authorPhotoUrl": author.get("photoUri"),
                "rating": int(rev.get("rating") or 5),
                "comment": text_obj.get("text") or "",
                "relativeTime": rev.get("relativePublishTimeDescription") or "",
                "source": "google",
                "createdAt": rev.get("publishTime") or now.isoformat(),
            }
        )

    avg = data.get("rating")
    total = int(data.get("userRatingCount") or len(normalized_reviews))
    result = {
        "placeName": display_name,
        "placeId": place_id,
        "average": float(avg) if avg is not None else None,
        "total": total,
        "distribution": _build_distribution(normalized_reviews),
        "reviews": normalized_reviews,
        "source": "google_places_live",
        "placesApiConfigured": True,
        "fetchedAt": now.isoformat(),
        "error": None,
    }
    _cache_entry = result
    _cache_expires_at = now + _CACHE_TTL
    return result


sys.modules.setdefault("services.reviews_service", sys.modules[__name__])
sys.modules.setdefault("apps.api.services.reviews_service", sys.modules[__name__])
