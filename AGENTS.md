# Torre Satori PMS
Hotel Torre Satori (Sevilla, Valle del Cauca), 9 habitaciones (`1`–`9`), ~40 reservas/mes. Proyecto Integrador II, Icesi.
Monolito modular hexagonal en **FastAPI + PostgreSQL 16 + React 18**: reservas y disponibilidad · habitaciones y estadías · clientes, reseñas y fidelización · tienda e inventario · finanzas y reportes · identidad y auditoría · conversaciones WhatsApp y notificaciones. WhatsApp (huésped) y web (admin, recepcionista) usan la misma API.

## Stack Actual Integrado (`integracion-fastapi`)
- **Backend:** Python 3.12 + FastAPI + Pydantic + SQLAlchemy async + Alembic (`apps/api/`) + APScheduler en proceso. Sin Redis en backend ni en `docker-compose.yml` (`legacy-java-backup` conserva el código Java histórico).
- **Base de datos:** PostgreSQL 16 (`btree_gist`), `EXCLUDE USING gist` sobre `room_id + daterange(check_in, check_out, '[)')` para estados activos (`BLOQUEADA_TEMPORAL`, `PENDIENTE_PAGO`, `CONFIRMADA`, `EN_CURSO`).
- **Expiración:** `BLOQUEADA_TEMPORAL` vence a los 15 min; `PENDIENTE_PAGO` (reservas chatbot Wompi) vence a las 24 h. Job cada 60 s marca `EXPIRADA` y publica eventos SSE/n8n.
- **Frontend:** React 18 + Vite + TypeScript + Tailwind + TanStack Query (`apps/web/`).
- **Chatbot y pagos:** n8n (`flows/n8n/V10_ChatbotReservas.json`, 0 nodos Redis, sesiones y `wompi:link:*` en PostgreSQL) + WhatsApp Cloud API + Wompi (puerto de pago + sandbox).

## Reglas de Seguridad y Operación
- JWT (`Administrador` y `Recepcionista`), Argon2/bcrypt, auditoría inmutable, `X-Service-Key` para n8n, webhooks HMAC `X-Hub-Signature-256` / Wompi `X-Event-Checksum` + idempotencia, Ley 1581 (sin PII en logs ni endpoints de debug en producción).
- Pruebas automatizadas en `tests/backend/` (`pytest` contra `satoripms_test` aislada) y `tests/chatbot/` (`verify_n8n_flow_integrity.py`, `suite_pruebas_chatbot.js`, `test_pago_wompi_v9.js`).
- Antes de cada cambio: explicar **POR QUÉ · QUÉ · ARCHIVOS · cómo verificaré**. Commits en español en la rama de trabajo activa (`integracion-fastapi`), nunca push directo a `main` sin revisión y verificación completa.
- Comunicación concisa en chat (`<= 10` líneas), detalle técnico en `docs/`.
