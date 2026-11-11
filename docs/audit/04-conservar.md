# Evaluación de Componentes a Conservar y Adaptar (Fase 1 - Etapa A)

**Fecha:** 2026-11-10  
**Rama:** `migracion-fastapi`  
**Referencia:** Complementa y refina a [01-estatica.md](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/docs/audit/01-estatica.md#L1-L55) y [03-limpieza.md](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/docs/audit/03-limpieza.md#L1-L100).

---

## 1. Mapa de la Rama (`migracion-fastapi`)

La rama `migracion-fastapi` conservará la solución desacoplada de la tecnología prohibida, preservando:
1. **Frontend (`apps/web/`):** SPA en React 18 + Vite + TypeScript que proporciona la interfaz administrativa del hotel. Aloja la supervisión de conversaciones (`Conversations.tsx`) y el panel de verificación de reservas con formulario operativo (`ReservasDebug.tsx`), consumiendo la API mediante Axios.
2. **Orquestador del Chatbot (`flows/n8n/`):** Flujos de automatización (especialmente `V8_ChatbotReservas.json`, 83 nodos) que reciben mensajes de WhatsApp Cloud API, interactúan con Gemini para interpretación de lenguaje natural y consultan la disponibilidad y reservas mediante peticiones HTTP a la API.
3. **Especificaciones y Base DDL (`docs/legacy-ref/`):** Migraciones SQL de Flyway extraídas de la API Java que contienen la definición de tablas (`room`, `guest`, `booking`, `conversation`, `system_users`, `review`), la extensión `btree_gist` y la restricción de exclusión GiST (`no_overlapping_bookings`), insumo directo para las migraciones Alembic.
4. **Infraestructura y Configuración Base (`docker-compose.yml`, `db/seed/dev_seed.sql`, `.gitignore`):** Orquestación de PostgreSQL 16 y n8n, sembrado de usuarios administrativos y exclusión de artefactos volátiles.
5. **Documentación del Negocio (`docs/`):** Manuales, reglas hoteleras (RN-02 a RN-13), flujos operativos y políticas de cancelación que rigen el comportamiento del sistema.

---

## 2. Tabla de Evaluación y Pruebas

| ruta | rol en el sistema | ¿funciona? (evidencia) | decisión | cómo se integra con el backend FastAPI | ajuste necesario |
|---|---|---|---|---|---|
| `apps/web/` | Panel administrativo y monitor de reservas web | **Funcional** (`npm ci` exitoso en 6s; `npm run build` completó `tsc && vite build` en 924ms sin errores) | CONSERVAR | Consume la API REST mediante [apps/web/src/api/client.ts](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/apps/web/src/api/client.ts#L1-L16) apuntando a `/api`. | Ninguno inmediato; a futuro implementar pantallas faltantes (Login RN-10, Calendario, Finanzas RN-11). |
| `apps/web/src/pages/Conversations.tsx` | Vista de supervisión de soporte y WhatsApp | **Funcional** (compila en bundle; sin mock data) | CONSERVAR | Llama a `GET /api/conversations` por polling cada 5s. | FastAPI debe implementar el router `/api/conversations` devolviendo el schema esperado. |
| `apps/web/src/pages/ReservasDebug.tsx` | Monitor y formulario de creación de reservas | **Funcional** (compila en bundle; sin mock data) | CONSERVAR | Llama a `GET /api/rooms/availability`, `GET /api/bookings/debug`, `POST /api/bookings/lock` y `POST /api/bookings/confirm`. | FastAPI debe exponer estos 4 endpoints con paridad de contratos JSON. |
| `flows/n8n/V8_ChatbotReservas.json` | Flujo activo del chatbot de WhatsApp | **Parcial** (JSON 100% válido, 83 nodos íntegros vía [verify_n8n_flow_integrity.py](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/tests/chatbot/verify_n8n_flow_integrity.py#L1-L50); acoplado a Redis) | ADAPTAR | Orquesta el webhook de Meta y llama a FastAPI (`/api/rooms/availability`, `/api/bookings/*`, `/api/reviews`). | 5 nodos (`n8n-nodes-base.redis`) gestionan sesiones de chat; deben sustituirse por endpoints de sesión en FastAPI respaldados en PostgreSQL. |
| `flows/n8n/pastVersions/*.json` | Versiones históricas V1 a V7 del chatbot | **Funcional** (7 de 7 archivos con JSON válido) | CONSERVAR | Referencia histórica de evolución del chatbot. | Ninguno. |
| `tests/chatbot/verify_n8n_flow_integrity.py` | Script de validación de grafos y enlaces n8n | **Funcional** (ejecutado con éxito: `100% INTEGRITY, ZERO BROKEN LINKS`) | CONSERVAR | Script utilitario Python para CI y desarrollo local. | Ninguno. |
| `tests/chatbot/build_v8_chatbot_flow.py` | Generador programático del flujo V8 | **Parcial** (código ejecutable pero genera URL `gemini-flash-lite-latest` y nodos Redis) | ADAPTAR | Construye o regenera el flujo exportado de n8n. | Ajustar modelo a `gemini-2.0-flash` y reemplazar emisión de nodos Redis por llamadas a API de sesión. |
| `tests/chatbot/test_*.js` (7 scripts) | Suites de prueba funcional E2E para chatbot | **No verificable** (requieren n8n activo en puerto 5678 y backend en puerto 8080) | CONSERVAR | Validan los flujos de reserva, cancelación, pago y reseñas simulando webhooks de WhatsApp. | Ajustar puertos y rutas base una vez que FastAPI y n8n estén desplegados. |
| `apps/api/src/main/resources/db/migration/*.sql*` (6 archivos) | DDL inicial, constraints GiST y semillas | **No verificable en vivo** (Postgres/Docker no accesible en host por permisos de socket); **Funcional estático** (incluye `btree_gist` y constraint `EXCLUDE USING gist`) | MOVER a `docs/legacy-ref/db-migrations/` | Insumo directo para diseñar los modelos SQLAlchemy 2.0 y la primera migración de Alembic. | Migrar a scripts de Alembic (`env.py` y versión inicial). |
| `db/seed/dev_seed.sql` | Script SQL de sembrado para usuario administrador | **Funcional** (sintaxis SQL válida para PostgreSQL) | CONSERVAR | Poblará la tabla `system_users` en bases de datos PostgreSQL de desarrollo. | Asegurar que el modelo `SystemUser` de SQLAlchemy mapee los campos `username`, `password_hash`, `role`, `name`. |
| `docker-compose.yml` | Orquestación de infraestructura en contenedores | **Parcial** (PostgreSQL y n8n válidos; contiene contenedor `redis:7-alpine`) | ADAPTAR | Desplegará PostgreSQL 16, n8n y el nuevo servicio `api` (FastAPI). | Eliminar servicio `redis` (líneas 21-35), volumen `redis_data` (línea 87) y dependencias de Redis en `api` y `n8n`. |
| `.github/workflows/ci.yml` | Pipeline de CI en GitHub Actions | **Parcial** (job frontend válido; job backend atado a Java 21, Maven y Redis) | ADAPTAR | Ejecuta linters, tipado y tests automatizados en PRs. | Eliminar job Java ([ci.yml:34-85](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/.github/workflows/ci.yml#L34-L85)); crear job Python con `pytest` y `alembic check`. |
| `start-dev.sh` | Script de inicialización rápida de entorno local | **Parcial** (lógica de frontend y Docker válida; atado a `mvn` y `java`) | ADAPTAR | Inicializa la base de datos, ejecuta migraciones y levanta servidores de desarrollo. | Eliminar verificaciones y compilación de Maven/Java ([start-dev.sh:120,163-165](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/start-dev.sh#L120)); incorporar arranque ASGI Uvicorn o Docker. |
| `.env.example` | Plantilla de configuración de entorno | **Parcial** (estructura completa pero incluye `REDIS_URL`) | ADAPTAR | Define las variables requeridas por FastAPI, n8n y Postgres. | Eliminar bloque Redis (líneas 13-14) y agregar variables de FastAPI (`SECRET_KEY`, `ALGORITHM`). |
| `docs/Diagramas/` (01, 02, 03) | Diagramas de arquitectura y secuencia | **Roto / Obsoleto** (describen arquitectura con Redis 7, Java 21 y Spring Boot) | ADAPTAR | Documentación técnica de diseño. | Actualizar diagramas Mermaid para reflejar FastAPI y PostgreSQL 16 como único mecanismo de persistencia y candado. |
| `docs/modulos/BackendAPI.md` e `Infraestructura.md` | Especificaciones de backend e infraestructura | **Parcial / Obsoleto** (describen servidor en Java y memoria rápida Redis) | ADAPTAR | Guía de referencia técnica y funcional. | Actualizar especificación indicando arquitectura Python 3.12, FastAPI y exclusión de Redis. |

---

## 3. Decisiones que Difieren de `03-limpieza.md`

1. **`flows/n8n/V8_ChatbotReservas.json`:** Pasa de `CONSERVAR` a **`ADAPTAR`**. Se detectaron 5 nodos (`Redis Obtener Sesión`, `Redis Guardar Sesión`, `Redis Revisar Inactividad`, `Redis Confirmar Limpieza`, `Redis Borrar Sesión Inactiva`) que requieren reemplazar Redis por endpoints de sesión en FastAPI o persistencia en PostgreSQL.
2. **`tests/chatbot/build_v8_chatbot_flow.py`:** Pasa de `CONSERVAR` a **`ADAPTAR`**. Actualmente genera llamadas a `gemini-flash-lite-latest` y construye los nodos Redis; debe actualizarse para emitir `gemini-2.0-flash` y omitir dependencias de Redis.
3. **`apps/web/tsconfig.json` y TypeScript:** Se retira la etiqueta de "dudoso". Se confirma **`CONSERVAR`** plenamente tras verificar que compila en 924ms con cero errores y provee tipado fuerte para los contratos de reserva.

---

## 4. Revisión de Seguridad (Detección de Secretos)

Se realizó un escaneo exhaustivo en el árbol de archivos y el historial de git (`git log -p`):
- **Secretos reales filtrados:** **NO**. No se encontraron tokens privados reales, API keys activas de Gemini ni credenciales de WhatsApp en el repositorio.
- **Valores por defecto / Placeholders detectados (no son secretos de producción):**
  - [.env.example:10](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/.env.example#L10): `POSTGRES_PASSWORD=satori_dev` (contraseña de desarrollo por defecto).
  - [.env.example:18](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/.env.example#L18): `JWT_SECRET=cambia_esto_por_un_secreto_seguro...` (placeholder).
  - [.env.example:45](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/.env.example#L45): `N8N_PUBLIC_URL=https://n8n-chatbot.share.zrok.io/` (URL de túnel de prueba).
  - [docker-compose.yml:9,49](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/docker-compose.yml#L9): Contraseñas por defecto para desarrollo local (`satori_dev`, `admin123`).
  - [db/seed/dev_seed.sql:15](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/db/seed/dev_seed.sql#L15): Hash bcrypt de demostración para el usuario local `Admin`.
- **Conclusión de seguridad:** Es seguro realizar commits y push en ramas de trabajo siempre que el archivo `.env` real permanezca fuera de git (cumplido vía `.gitignore`).

---

## 5. Evaluación de TypeScript en Frontend

- **Compilación:** `npm run build` ejecutó `tsc && vite build` finalizando con código de salida 0 en 924 ms, emitiendo el paquete de producción en `apps/web/dist/`.
- **Integridad:** Las interfaces (`BookingRow`, `Room`) tipan de manera estricta los datos consumidos de la API. Convertir a JS puro implicaría eliminar garantías de tipos sin beneficio funcional.
- **Propuesta de corrección en `AGENTS.md` (línea 3):**
  ```markdown
  Stack único: Python 3.12 + FastAPI · PostgreSQL 16 (btree_gist) · SQLAlchemy + Alembic · React 18 (Vite, TS) · n8n + Gemini 2.0 Flash · Cloudflare R2.
  ```
