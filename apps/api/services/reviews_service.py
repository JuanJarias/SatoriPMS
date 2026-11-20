"""Servicio de consulta en vivo y caché de reseñas reales de Google (Travel público + Places API)."""

from datetime import datetime, timedelta, timezone
import json
import re
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
_DS1_PATTERN = re.compile(
    r"AF_initDataCallback\(\{key:\s*'ds:1'.*?data:(.*?),\s*sideChannel:",
    re.DOTALL,
)


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


def _empty_summary(
    *,
    place_id: str,
    reviews_url: str,
    now: datetime,
    source: str,
    places_configured: bool,
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "placeName": "Hotel Torre Satori · Sevilla, Valle del Cauca",
        "placeId": place_id,
        "googleReviewsUrl": reviews_url,
        "average": None,
        "total": 0,
        "distribution": {5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
        "reviews": [],
        "source": source,
        "placesApiConfigured": places_configured,
        "fetchedAt": now.isoformat(),
        "error": error,
    }


async def _fetch_google_travel_summary(
    reviews_url: str,
    place_id: str,
    now: datetime,
) -> dict[str, Any] | None:
    """Extrae calificación promedio, total y distribución real desde Google Travel sin API Key."""
    target_url = reviews_url.strip()
    if not target_url:
        return None
    if "hl=" not in target_url:
        sep = "&" if "?" in target_url else "?"
        target_url = f"{target_url}{sep}hl=es-CO&gl=co"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "es-CO,es;q=0.9",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(target_url, headers=headers)
            resp.raise_for_status()
            html = resp.text
    except Exception:
        return None

    match = _DS1_PATTERN.search(html)
    if not match:
        return None

    try:
        root = json.loads(match.group(1))
        node = root[0] if isinstance(root, list) and root else []
        place_name = (
            str(node[1]).strip()
            if isinstance(node, list) and len(node) > 1 and node[1]
            else "Hotel Torre Satori · Sevilla, Valle del Cauca"
        )
        rating_block = node[7] if isinstance(node, list) and len(node) > 7 else []
        pair = rating_block[0] if isinstance(rating_block, list) and rating_block else []
        if not (isinstance(pair, list) and len(pair) >= 2):
            return None

        average = float(pair[0])
        total = int(pair[1])
        distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        dist_container = rating_block[1][0] if len(rating_block) > 1 and rating_block[1] else []
        if isinstance(dist_container, list):
            for entry in dist_container:
                if isinstance(entry, list) and len(entry) >= 3:
                    star = int(entry[0])
                    count = int(entry[2])
                    if star in distribution:
                        distribution[star] = count

        return {
            "placeName": place_name,
            "placeId": place_id,
            "googleReviewsUrl": reviews_url,
            "average": average,
            "total": total,
            "distribution": distribution,
            "reviews": [],
            "source": "google_travel_live",
            "placesApiConfigured": False,
            "fetchedAt": now.isoformat(),
            "error": None,
        }
    except Exception:
        return None


async def fetch_google_reviews_summary(refresh: bool = False) -> dict[str, Any]:
    """Consulta reseñas de Google: Places API (con llave) o resumen público Google Travel (sin tarjeta/llave)."""
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
    reviews_url = (
        settings.GOOGLE_REVIEWS_URL.strip()
        or "https://www.google.com/travel/hotels/entity/CgsIvsf-mZ_-h-fGARAB/reviews"
    )

    if not api_key:
        travel_summary = await _fetch_google_travel_summary(reviews_url, place_id, now)
        if travel_summary is not None:
            _cache_entry = travel_summary
            _cache_expires_at = now + _CACHE_TTL
            return travel_summary
        if _cache_entry is not None:
            return {
                **_cache_entry,
                "error": "Usando caché tras fallo al consultar el perfil público de Google Travel.",
            }
        return _empty_summary(
            place_id=place_id,
            reviews_url=reviews_url,
            now=now,
            source="google_places_unconfigured",
            places_configured=False,
        )

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
            return {
                **_cache_entry,
                "error": f"Usando caché tras fallo al consultar Google Places: {exc}",
            }
        return _empty_summary(
            place_id=place_id,
            reviews_url=reviews_url,
            now=now,
            source="google_places_error",
            places_configured=True,
            error=f"No fue posible consultar Google Places API: {exc}",
        )

    display_name = (
        (data.get("displayName") or {}).get("text")
        or "Hotel Torre Satori · Sevilla, Valle del Cauca"
    )
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
        "googleReviewsUrl": reviews_url,
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
