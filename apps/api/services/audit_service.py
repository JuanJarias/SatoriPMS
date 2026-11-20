"""Servicio de auditoría inmutable (E6 Roles y Auditoría)."""

import json
import sys
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

try:
    from models.audit_log import AuditLog
except ImportError:
    from apps.api.models.audit_log import AuditLog


async def record_audit(
    db: AsyncSession,
    actor: str,
    action: str,
    entity: str,
    entity_id: str | int | None = None,
    details: dict[str, Any] | str | None = None,
) -> AuditLog:
    """Inserta un registro inmutable en la tabla audit_log sin exponer datos sensibles."""
    if isinstance(details, dict):
        serialized_details: str | None = json.dumps(details, ensure_ascii=False)
    else:
        serialized_details = details

    entry = AuditLog(
        actor_username=actor,
        action=action,
        entity=entity,
        entity_id=str(entity_id) if entity_id is not None else None,
        details_json=serialized_details,
    )
    db.add(entry)
    await db.flush()
    return entry


sys.modules.setdefault("services.audit_service", sys.modules[__name__])
sys.modules.setdefault("apps.api.services.audit_service", sys.modules[__name__])
