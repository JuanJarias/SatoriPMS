# Plan y Ejecución de Limpieza (Fase 1 - Etapa B)

**Fecha:** 2026-11-10  
**Rama:** `migracion-fastapi`  
**Tag de respaldo (main):** `legacy-java-backup` (`d0b17ad17db04fe5b6027838ff108bd418c04413`)  
**Estado:** Etapa B ejecutada exitosamente en commits separados.

---

## 1. Tabla de Estado de Archivos tras la Limpieza

| ruta | qué es | acción original | estado final | evidencia / motivo |
|---|---|---|---|---|
| `apps/api/.dockerignore` | Exclusiones Docker Maven | ELIMINAR | **ELIMINADO** | Eliminado en commit 2. |
| `apps/api/Dockerfile` | Dockerfile `eclipse-temurin:21-jre` | ELIMINAR | **ELIMINADO** | Eliminado en commit 2. |
| `apps/api/pom.xml` | Descriptor Maven | ELIMINAR | **ELIMINADO** | Eliminado en commit 2. |
| `apps/api/src/main/resources/application.yml` | Config Spring Boot/Redis/Flyway | ELIMINAR | **ELIMINADO** | Eliminado en commit 3. |
| `apps/api/src/main/java/**` (28 archivos) | Clases Java (Controllers, Services, JPA, Config) | ELIMINAR | **ELIMINADO** | 28 archivos eliminados en commit 2. |
| `apps/api/src/test/java/**` (1 archivo) | Suite de pruebas JUnit/Testcontainers | ELIMINAR | **ELIMINADO** | Eliminado en commit 2. |
| `apps/api/src/main/resources/db/migration/*.sql*` (6 archivos) | DDL inicial Flyway y semillas de habitaciones/productos | MOVER | **MOVIDO a `docs/legacy-ref/db-migrations/`** | Movidos vía `git mv` en commit 1. *Nota:* No verificable en vivo, pendiente de probar en el primer lote de Alembic. |
| `docs/legacy-ref/endpoints-java.md` | Especificación de endpoints REST Java | CREAR | **CREADO** | Creado en commit 1 como contrato de paridad para routers FastAPI. |
| `docs/legacy-ref/README.md` | Guía de referencia legada | CREAR | **CREADO** | Creado en commit 1 documentando el estado de los insumos. |
| `apps/web/**` (10 archivos) | Frontend React 18 + Vite + TypeScript | CONSERVAR | **CONSERVADO** | Compila al 100% (`npm ci` y `npm run build` en 924ms). `tsconfig.json` ratificado. |
| `db/seed/dev_seed.sql` | Script SQL dev para `system_users` | CONSERVAR | **CONSERVADO** | Script agnóstico para PostgreSQL. |
| `docker-compose.yml` | Orquestación Docker | ADAPTAR | **ADAPTADO** | Servicio `redis`, volumen `redis_data` y dependencias eliminados en commit 3. |
| `.env.example` | Variables de entorno base | ADAPTAR | **ADAPTADO** | Bloque Redis eliminado; URL de Postgres normalizada en commit 3. |
| `.github/workflows/ci.yml` | Pipeline de integración continua | ADAPTAR | **ADAPTADO** | Job de backend Java/Maven/Redis eliminado en commit 3; se conserva job de frontend. |
| `start-dev.sh` | Script de inicialización de desarrollo | ADAPTAR | **ADAPTADO** | Validaciones y compilación de `mvn`/`java` eliminadas en commit 3. |
| `AGENTS.md` | Reglas rectoras de agentes y stack | ADAPTAR | **ADAPTADO** | Regla actualizada a `React 18 (Vite, TS)` en commit 4. |
| `README.md` | Documentación principal del repositorio | ADAPTAR | **ADAPTADO** | Nota añadida: *"Backend en migración a FastAPI; legado en el tag legacy-java-backup"* en commit 4. |
| `.gitignore` | Reglas de exclusión Git | ADAPTAR | **ADAPTADO** | Agregadas exclusiones para `.venv`, `.pytest_cache`, coverage en commit 4. |
| `flows/n8n/V8_ChatbotReservas.json` | Flujo activo n8n (83 nodos) | ADAPTAR | **PENDIENTE (lote posterior)** | Preservado intacto temporalmente; referencias a Redis pendientes de migrar tras crear endpoints FastAPI. |
| `tests/chatbot/build_v8_chatbot_flow.py` | Generador del flujo n8n V8 | ADAPTAR | **PENDIENTE (lote posterior)** | Preservado intacto temporalmente; pendiente actualizar modelo a `gemini-2.0-flash` y omitir generación de nodos Redis. |
| `flows/n8n/pastVersions/*.json` (7 archivos) | Versiones anteriores de chatbot | CONSERVAR | **CONSERVADO** | Histórico de versiones. |
| `tests/chatbot/verify_n8n_flow_integrity.py` | Validador estructural n8n | CONSERVAR | **CONSERVADO** | Verificación íntegra (83 nodos, 0 errores). |
| `tests/chatbot/test_*.js` (7 archivos) | Tests funcionales del chatbot | CONSERVAR | **CONSERVADO** | Suites E2E simulando webhooks de WhatsApp. |
| `docs/**` (diagramas, manuales, módulos) | Documentación técnica y funcional | CONSERVAR / ADAPTAR | **CONSERVADO** | Preservados; los diagramas que mencionan Redis/Spring serán actualizados conceptualmente en lote documental posterior. |

---

## 2. Referencias a Redis Pendientes de Adaptación en Chatbot

Conforme a la aprobación, estos dos archivos se mantienen intactos durante esta limpieza y se adaptarán en un lote posterior cuando FastAPI exponga los endpoints de sesión:

1. **[flows/n8n/V8_ChatbotReservas.json](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/flows/n8n/V8_ChatbotReservas.json):**
   - Líneas 109-122: Nodo `Redis Obtener Sesión` (`operation: get`, `key: session:${wa_id}`).
   - Líneas 799-812: Nodo `Redis Guardar Sesión` (`operation: set`, `key: ${redis_key}`, `ttl: 660`).
   - Líneas 868-881: Nodo `Redis Revisar Inactividad` (`operation: get`).
   - Líneas 997-1010: Nodo `Redis Confirmar Limpieza` (`operation: get`).
   - Líneas 1065-1078: Nodo `Redis Borrar Sesión Inactiva` (`operation: delete`).
   - Líneas 2372, 2683, 2721, 2787, 2820: Conexiones del grafo hacia/desde los 5 nodos Redis.

2. **[tests/chatbot/build_v8_chatbot_flow.py](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/tests/chatbot/build_v8_chatbot_flow.py):**
   - Línea 24 y Línea 1288: Referencia al modelo `gemini-flash-lite-latest` (pendiente actualizar a `gemini-2.0-flash`).
   - Línea 1595: Asignación de payload con `redis_key: 'session:' + J.wa_id` y `redis_value: JSON.stringify(session)`.
   - Línea 1618: Asignación de payload con `redis_key: $('Preparar Salida').first().json.redis_key`.

---

## 3. Resumen de Commits Realizados en Etapa B

1. `57b12d1` — `chore(migra): mover especificaciones y migraciones Flyway a docs/legacy-ref` (6 archivos SQL movidos con `git mv`, README y `endpoints-java.md` creados).
2. `5c1cc67` — `chore(migra): eliminar codigo fuente Java, descriptor Maven y suites JUnit` (32 archivos eliminados con `git rm -r`).
3. `c97eceb` — `chore(migra): eliminar Redis, configuracion Flyway y limpiar docker-compose y scripts` (1 archivo eliminado con `git rm`, `docker-compose.yml`, `.env.example`, `.github/workflows/ci.yml` y `start-dev.sh` limpios).
4. Siguiente — `chore(migra): ajustar .gitignore, README, AGENTS.md y documentacion de auditoria`.
