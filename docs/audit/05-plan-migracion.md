# Plan Maestro de Migración a FastAPI (Fase 1 - Etapa B/C)

**Fecha:** 2026-11-10  
**Rama:** `migracion-fastapi`  
**Referencia de especificación legada:** Tag `legacy-java-backup` (`d0b17ad`) y directorio [docs/legacy-ref/](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/docs/legacy-ref/README.md).

---

## 1. Inventario por Épica del Backend Legado (Java/Spring)

Especificación extraída del tag `legacy-java-backup`. El código legado sirve como referencia de contratos y reglas; no se ejecuta ni se modifica.

| épica | ítem (endpoint, entidad/tabla o regla) | ruta@tag:línea | acción | estado RN asociada |
|---|---|---|---|---|
| **Autenticación** | Tabla `system_users` | `V1__initial_schema.sql:124-132` | PORTAR | RN-10 (Parcial en SQL: `CHECK (role IN ('admin', 'receptionist'))`) |
| **Autenticación** | `SecurityConfig` (Spring Security abierto `.permitAll()`) | `SecurityConfig.java:37-40` | DESCARTAR | RN-10 (Ausente en código: sin login, JWT ni RBAC) |
| **Autenticación** | Endpoints de autenticación (`/login`, `/me`) | N/A (nunca existieron en Java) | REESCRIBIR | RN-10 (Ausente en Java; requerida por frontend y seguridad) |
| **Reservas** | Tabla `room` (catálogo y capacidades) | `V1__initial_schema.sql:12-28` | PORTAR | Regla de capacidad base y máxima |
| **Reservas** | Tabla `guest` (huéspedes) | `V1__initial_schema.sql:3-10`, `V4:1` | PORTAR | RN-12 (Ausente en DB: no persiste consentimiento Ley 1581) |
| **Reservas** | Tabla `booking` y constraint `no_overlapping_bookings` | `V1__initial_schema.sql:57-90`, `V3:91` | PORTAR | RN-02 (Parcial: GiST en SQL con WHERE; duplicada en Redis) |
| **Reservas** | Tabla `conversation` (estado conversacional) | `V1__initial_schema.sql:31-55` | PORTAR | Base de sesiones chatbot |
| **Reservas** | Entidad JPA `Booking.java` | `Booking.java:1-105` | PORTAR | RN-02 (Falta mapear `conversation_id` y `stay_range`) |
| **Reservas** | `RedisLockService.java` y `RedisConfig.java` | `RedisLockService.java:1-125` | DESCARTAR | RN-02 (Redis tecnología prohibida) |
| **Reservas** | `GET /api/rooms/availability` | `BookingController.java:66-75` | PORTAR | RN-02 (Filtros fechas, adultos, niños, mascotas) |
| **Reservas** | `POST /api/bookings/lock` (bloqueo 15 min) | `BookingController.java:85-103` | REESCRIBIR | RN-02 (Migrar candado temporal de Redis a PostgreSQL) |
| **Reservas** | `POST /api/bookings/unlock` (liberación inmediata) | `BookingController.java:113-141` | REESCRIBIR | RN-02 (Liberación de candados en PostgreSQL) |
| **Reservas** | `POST /api/bookings/confirm` (lote y abono) | `BookingController.java:153-162` | PORTAR | Soporte abono 50% (`deposit`) y 100% (`full`) |
| **Reservas** | `POST /api/bookings/test-paid` (pago test) | `BookingController.java:171-183` | PORTAR | Utilidad de pruebas |
| **Reservas** | `GET /api/bookings/group/{code}` | `BookingController.java:193-202` | PORTAR | RN-03 (Desglose financiero y política de reembolso) |
| **Reservas** | `POST /api/bookings/group/{code}/cancellation` | `BookingController.java:216-227` | PORTAR | RN-03 (100% >72h, 50% 24-72h, 0% <24h sobre pagado) |
| **Reservas** | `POST /api/bookings/group/{code}/pay-remaining` | `BookingController.java:237-248` | PORTAR | Liquidación del 50% restante |
| **Reservas** | `GET /api/bookings/debug` | `BookingController.java:257-292` | PORTAR | Monitor administrativo consumido por `ReservasDebug.tsx` |
| **Reservas** | `GET /api/conversations` | `ConversationController.java:35-43` | PORTAR | Bandeja de chats consumida por `Conversations.tsx` |
| **Reservas** | `POST /api/conversations/{id}/escalation` | `ConversationController.java:51-55` | PORTAR | Solicitud de atención por recepcionista humano |
| **Reservas** | Liberación automática No-Show a las 12:00 | N/A (nunca existió en Java) | REESCRIBIR | RN-13 (Ausente en Java; debe liberarse al mediodía) |
| **Calendario** | Cuadrícula de ocupación y temporadas | N/A (solo mencionado en docs) | REESCRIBIR | Ausente en código Java y DB |
| **Finanzas** | Liquidación de sueldos (fijo/comisión/mixto) | N/A (nunca existió en Java) | REESCRIBIR | RN-11 (Ausente en código Java y DB) |
| **Finanzas** | Control de egresos y balance contable | N/A (solo mencionado en docs) | REESCRIBIR | Ausente en código Java |
| **Tienda** | Tabla `product` e inserts semilla | `V1:105-112`, `V6.example:1-8` | PORTAR | Tablas en SQL sin controladores Java |
| **Tienda** | Tabla `consumption` (cargos a habitación) | `V1:114-122`, `V3:74-76` | PORTAR | Relación booking-producto en SQL |
| **Tienda** | Endpoints de venta y catálogo tienda | N/A (nunca existieron en Java) | REESCRIBIR | Ausente en controladores Java |
| **Reseñas** | Tabla `review` (Google y chatbot) | `V1:95-103`, `V5:11-20` | PORTAR | Soporte de reseñas con o sin reserva asociada |
| **Reseñas** | Entidad JPA `Review.java` | `Review.java:1-51` | PORTAR | Mapeo de reseñas públicas |
| **Reseñas** | `GET /api/reviews` | `ReviewController.java:50-54` | PORTAR | Listado público de calificaciones |
| **Reseñas** | `POST /api/reviews` | `ReviewController.java:64-105` | PORTAR | Creación de reseña desde chatbot o web |

### Resumen de Estado de Reglas de Negocio en Legado:
- **RN-02 (Sin solapamiento):** **Parcial** (en SQL con GiST; en Java acoplado a Redis).
- **RN-10 (RBAC Recepcionista/Admin):** **Ausente** en código; solo constraint CHECK en tabla `system_users`.
- **RN-11 (Sueldo mensual fijo/comisión/mixto):** **Ausente** en su totalidad.
- **RN-12 (Autorización datos Ley 1581):** **Parcial** (solo texto informativo en chatbot; ausente en DB y API).
- **RN-13 (No-Show libera a las 12:00):** **Ausente** en su totalidad.

---

## 2. Contrato del Frontend React

Endpoints que el código fuente de [apps/web/src/](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/apps/web/src/) consume activamente contra la API:

| Endpoint (Método + Ruta) | Invocado en Frontend | ¿Existía en Java legado? | Cumplimiento requerido en FastAPI |
|---|---|---|---|
| `GET /api/conversations` | [Conversations.tsx:7](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/apps/web/src/pages/Conversations.tsx#L7) | **Sí** (`ConversationController:35`) | Contrato idéntico: lista de conversaciones con datos del huésped y estado. |
| `GET /api/rooms/availability` | [ReservasDebug.tsx:71](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/apps/web/src/pages/ReservasDebug.tsx#L71) | **Sí** (`BookingController:66`) | Params: `checkIn`, `checkOut`, `adults`, `children`, `pet`. Retorna `Room[]`. |
| `GET /api/bookings/debug` | [ReservasDebug.tsx:85](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/apps/web/src/pages/ReservasDebug.tsx#L85) | **Sí** (`BookingController:257`) | Retorna todas las reservas con datos planos del huésped y habitación. |
| `POST /api/bookings/lock` | [ReservasDebug.tsx:96](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/apps/web/src/pages/ReservasDebug.tsx#L96) | **Sí** (`BookingController:85`) | Body: `{ roomId, checkIn, checkOut }`. Retorna `{ lockToken, ttlSeconds, totalPrice }`. |
| `POST /api/bookings/confirm` | [ReservasDebug.tsx:103](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/apps/web/src/pages/ReservasDebug.tsx#L103) | **Sí** (`BookingController:153`) | Body completo con titular, acompañantes, habitaciones con `lockToken`. |

### Endpoints esperados por el frontend que NUNCA existieron en Java:
1. `POST /api/auth/login`: [client.ts:13-17](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/apps/web/src/api/client.ts#L13-L17) intercepta y envía `Authorization: Bearer <token>`, pero no existía endpoint emisor de JWT.
2. `GET /api/auth/me`: Verificación de identidad y rol del usuario logueado en sesión web.
3. Rutas proyectadas en [App.tsx:11](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/apps/web/src/App.tsx#L11) (`/login`, `/bookings`, `/shop`, `/finance`, `/settings`): Nunca tuvieron backend asociado.

---

## 3. Propuesta de Esquema Alembic Inicial

A partir de los archivos en [docs/legacy-ref/db-migrations/](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/docs/legacy-ref/db-migrations/), el esquema inicial de Alembic se estructurará mediante modelos declarativos de SQLAlchemy 2.0:

### A. Extensiones de PostgreSQL
- Habilitación obligatoria de `btree_gist`: `CREATE EXTENSION IF NOT EXISTS btree_gist;`

### B. Tablas por Épica
1. **Autenticación:**
   - `system_users`: `id` (BigSerial, PK), `username` (VarChar 50, UNIQUE), `password_hash` (VarChar 255), `role` (VarChar 20, check: admin/receptionist), `name` (VarChar 100), `active` (Boolean), `created_at` (Timestamp).
2. **Habitaciones y Reservas:**
   - `room`: `id` (BigSerial, PK), `number` (VarChar 10, UNIQUE), `name` (VarChar 50), `description` (Text), `type` (VarChar 50), `base_adults_capacity` (Int), `max_adults_capacity` (Int), `children_capacity` (Int), `extra_guest_price` (Numeric 10,2), `allows_pets` (Boolean), `price_per_night` (Numeric 10,2), `status` (VarChar 20: available/occupied/cleaning/maintenance), `active` (Boolean).
   - `guest`: `id` (BigSerial, PK), `whatsapp_phone` (VarChar 20, UNIQUE), `name` (VarChar 100), `email` (VarChar 100), `document_number` (VarChar 50), `data_consent` (Boolean, default False, **RN-12**), `data_consent_at` (Timestamp, **RN-12**), `created_at` (Timestamp), `updated_at` (Timestamp).
   - `temporary_locks`: `id` (BigSerial, PK), `room_id` (BigInt, FK room.id), `check_in` (Date), `check_out` (Date), `lock_token` (VarChar 100, UNIQUE), `expires_at` (Timestamp), `created_at` (Timestamp). *(Sustituye Redis directamente en PostgreSQL)*.
   - `conversation`: `id` (BigSerial, PK), `guest_id` (BigInt, FK guest.id), `status` (VarChar 20), `step` (VarChar 30), `check_in` (Date), `check_out` (Date), `selected_room_id` (BigInt, FK room.id), `adults` (Int), `children` (Int), `with_pet` (Boolean), `total_price` (Numeric 10,2), `lock_token` (VarChar 100), `lock_expires_at` (Timestamp), `session_data` (JSONB, almacena el draft del chatbot), `created_at`, `updated_at`.
   - `booking`: `id` (BigSerial, PK), `reservation_group_id` (UUID), `guest_id` (BigInt, FK guest.id), `room_id` (BigInt, FK room.id), `conversation_id` (BigInt, FK conversation.id, UNIQUE), `check_in` (Date), `check_out` (Date), `stay_range` (`DATERANGE GENERATED ALWAYS AS (daterange(check_in, check_out, '[)')) STORED`), `status` (VarChar 20: pending_payment/confirmed/checked_in/checked_out/finished/cancelled/no_show), `payment_status` (VarChar 20: pending/paid/refunded/partial), `paid_amount` (Numeric 10,2), `adults` (Int), `children` (Int), `with_pet` (Boolean), `companions` (Text), `total_price` (Numeric 10,2), `source` (VarChar 20: chatbot/web), `lock_id` (VarChar 100), `created_at`, `updated_at`.
3. **Tienda e Inventario:**
   - `product`: `id` (BigSerial, PK), `name` (VarChar 100), `description` (Text), `price` (Numeric 10,2), `stock` (Int), `active` (Boolean).
   - `consumption`: `id` (BigSerial, PK), `booking_id` (BigInt, FK booking.id), `product_id` (BigInt, FK product.id), `quantity` (Int), `unit_price` (Numeric 10,2), `paid` (Boolean), `occurred_at` (Timestamp).
4. **Reseñas:**
   - `review`: `id` (BigSerial, PK), `guest_id` (BigInt, FK guest.id, Nullable), `room_id` (BigInt, FK room.id, Nullable), `booking_id` (BigInt, FK booking.id, UNIQUE, Nullable), `rating` (Int, 1-5), `comment` (Text), `author_name` (VarChar 150), `source` (VarChar 50: google/chatbot/web), `created_at` (Timestamp).
5. **Finanzas (RN-11):**
   - `payroll_config`: `id` (BigSerial, PK), `user_id` (BigInt, FK system_users.id), `modality` (VarChar 20: fixed/commission/mixed), `base_salary` (Numeric 12,2), `commission_percentage` (Numeric 5,2), `active` (Boolean).
   - `operating_expenses`: `id` (BigSerial, PK), `category` (VarChar 50), `description` (Text), `amount` (Numeric 12,2), `incurred_at` (Date), `registered_by` (BigInt, FK system_users.id).

### C. Constraint EXCLUDE con GiST (RN-02)
```sql
ALTER TABLE booking ADD CONSTRAINT no_overlapping_bookings EXCLUDE USING gist (
    room_id WITH =,
    stay_range WITH &&
) WHERE (status IN ('pending_payment', 'confirmed', 'checked_in'));
```
- **Comportamiento ante canceladas:** Excluye explícitamente `status = 'cancelled'` y `status = 'no_show'`. Cuando una reserva pasa a cancelada, la base de datos libera automáticamente el rango de fechas sin requerir borrado físico.
- **Índices de soporte:**
  - `CREATE INDEX idx_booking_stay_range ON booking USING gist (stay_range);`
  - `CREATE INDEX idx_booking_room ON booking(room_id);`
  - `CREATE INDEX idx_booking_group ON booking(reservation_group_id);`
  - `CREATE UNIQUE INDEX uq_active_conversation_guest ON conversation(guest_id) WHERE status = 'active';`

---

## 4. Estrategia de Desacople de Redis en n8n

En [V8_ChatbotReservas.json](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/flows/n8n/V8_ChatbotReservas.json#L109), 5 nodos operan sobre Redis para gestionar sesiones volátiles:
1. `Redis Obtener Sesión` (`GET session:${wa_id}`)
2. `Redis Guardar Sesión` (`SET session:${wa_id} (TTL 660s)`)
3. `Redis Revisar Inactividad` (`GET session:${wa_id}`)
4. `Redis Confirmar Limpieza` (`GET session:${wa_id}`)
5. `Redis Borrar Sesión Inactiva` (`DEL session:${wa_id}`)

### A. Endpoints de FastAPI requeridos para sustituir Redis:
1. `GET /api/chatbot/session/{wa_id}`: Recupera la sesión activa y el borrador de reserva (`ia_draft`) desde PostgreSQL (almacenado en `conversation.session_data`). Si expiró por TTL (>10 min inactivo), retorna estado expirado.
2. `POST /api/chatbot/session/{wa_id}`: Guarda o actualiza el estado de la sesión, datos cotizados y timestamp de última interacción atómicamente en PostgreSQL.
3. `DELETE /api/chatbot/session/{wa_id}`: Limpia la sesión activa y libera de forma atómica los bloqueos temporales asociados en `temporary_locks`.
4. `POST /api/notifications/agent-request`: Registra la solicitud de escalamiento a recepción humana en la tabla de conversaciones.

### B. Qué dejarán de necesitar los flujos n8n:
- La credencial `redis: Redis account`.
- Los nodos de tipo `n8n-nodes-base.redis` (se reemplazan por nodos `httpRequest` estándar).
- El contenedor y volumen de Redis en Docker.
- La lógica manual de serialización y control de milisegundos en bloques JavaScript de n8n.

---

## 5. Análisis del Tablero GitHub vs. Código Real

Datos extraídos de `gh project item-list 2 --owner JuanJarias` y `gh issue list --state all`.

### A. Tabla Comparativa por Ítem de Tablero (Muestra Representativa)

| ítem | estado tablero | estado real | ¿coincide? | explicación |
|---|---|---|---|---|
| `#103` [DU-01] Documentar arquitectura | Done | Funcional | **Sí** | Existe documentación en `docs/` (requiere actualización de stack). |
| `#104` a `#108` [DU-02 a DU-06] Diseños de solución | Done | Funcional | **Sí** | Documentos de diseño entregados en `docs/modulos/`. |
| `#101` [HU-00.1] Conectar WhatsApp con n8n | Done | Funcional | **Sí** | Webhook configurado en `V8_ChatbotReservas.json`. |
| `#29` [CU-01] Reservar habitación (Chatbot) | Done | Ausente en FastAPI | **No** | Se implementó en Java; al eliminar Java, en FastAPI no existe. |
| `#35` [CU-02] Cancelar reserva (Chatbot) | Done | Ausente en FastAPI | **No** | Pendiente de portar router y servicio a FastAPI. |
| `#42` [HU-08] Confirmación automática | Done | Ausente en FastAPI | **No** | Depende de endpoint de confirmación de FastAPI. |
| `#74` [CU-01.1] Consultar disponibilidad | Done | Ausente en FastAPI | **No** | Pendiente de portar a FastAPI. |
| `#75` [CU-01.2] Bloquear temporalmente | Done | Ausente en FastAPI | **No** | Se hizo en Redis; debe rehacerse en PostgreSQL. |
| `#77` [CU-01.4] Calcular precio y confirmar | Done | Ausente en FastAPI | **No** | Lógica de recargos pendiente de portar a FastAPI. |
| `#34` [CU-03] Registrar check-in | In Progress | Ausente | **No** | Sin endpoints ni interfaz implementada. |
| `#39` [CU-04] Registrar check-out | In Progress | Ausente | **No** | Sin endpoints ni interfaz implementada. |
| `#41` [HU-03] Calendario de ocupación | In Progress | Ausente | **No** | Sin vista ni backend de matriz de ocupación. |
| `#49` [HU-05] Roles y usuarios | In Progress | Ausente | **No** | Sin endpoints de usuarios ni RBAC en backend. |
| `#21` [HU-01] Exportar informe finanzas | Backlog | Ausente | **Sí** | No iniciado. |
| `#45` [HU-07] Sueldo recepcionista (RN-11) | Backlog | Ausente | **Sí** | No iniciado. |
| `#48` [CU-05] Vender producto tienda | Backlog | Ausente | **Sí** | No iniciado. |
| `#44` [HU-02] Consultar reseñas | Backlog | Ausente en FastAPI | **Sí** | No implementado en FastAPI. |

### B. Porcentaje de Progreso por Épica (Tablero vs. Código Real Actual)

| Épica | % Progreso Tablero | % Progreso Real en Código | Diagnóstico |
|---|---|---|---|
| **Diseño de la solución** | 100% (6/6) | 100% | Documentación funcional completa en `docs/`. |
| **Épica 1: Reservas** | 46% (7/15) | 15% | Flujo n8n existe (83 nodos) y vistas React (`ReservasDebug.tsx`), pero backend FastAPI en 0%. |
| **Épica 2: Gestión Operativa** | 0% (0/6) | 0% | Ningún endpoint operativo desarrollado. |
| **Épica 3: Facturación y Finanzas** | 0% (0/4) | 0% | RN-11 ausente. |
| **Épica 4: Tienda y Ventas** | 0% (0/3) | 0% | Solo DDL en migraciones legacy; sin código backend. |
| **Épica 5: Reseñas y Fidelización** | 0% (0/4) | 0% | Reseñas eliminadas con backend Java; ausentes en FastAPI. |
| **Épica 6: Roles y Autenticación** | 0% (0/3) | 0% | RN-10 ausente. |
| **Transversal / QA / Otros** | 87% (41/47) | 10% | Cierres administrativos en GitHub; suites de tests backend no implementadas en Python. |

### C. Listas de Discrepancia del Tablero:
1. **Ítems en Done que NO existen en el código actual:**
   - `#29`, `#35`, `#42`, `#74`, `#75`, `#77`: Fueron cerrados con la implementación Java + Redis (PRs #109, #110); al expurgar el backend prohibido para migrar a FastAPI, su funcionalidad backend está pendiente de reescritura.
2. **Trabajo real sin ítem en tablero:**
   - Auditorías estáticas y planes de migración ([01-estatica.md](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/docs/audit/01-estatica.md), [03-limpieza.md](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/docs/audit/03-limpieza.md), [04-conservar.md](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/docs/audit/04-conservar.md), [05-plan-migracion.md](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/docs/audit/05-plan-migracion.md)).
   - Extracción de contratos legados en [endpoints-java.md](file:///home/jjarias/Documents/UNIVERSIDAD/8vo%20semestre/Integrador-ii/SatoriPMS/docs/legacy-ref/endpoints-java.md).
   - Tag de respaldo `legacy-java-backup` y rama `migracion-fastapi`.
3. **Ítems obsoletos en tablero:**
   - `#75` [CU-01.2] Bloquear habitación temporalmente (especifica Redis en su descripción).
   - `#81` [HU-03.1] Reconexión del socket (describe Spring STOMP).

---

## 6. Plan de Migración en Lotes Acotados (Máximo 5 IDs por Lote)

Todos los ítems están respaldados por evidencia directa en el código y el esquema legacy. No se incluyen ítems no verificables.

### Lote M0: Andamiaje y Fundación Backend
| ID | épica | por qué | cambio | archivos | verificación | riesgo | depende de |
|---|---|---|---|---|---|---|---|
| **M0-01** | Transversal | Establecer runtime Python 3.12 y dependencias del stack | Crear estructura `apps/api/`, `pyproject.toml` con FastAPI, Uvicorn, SQLAlchemy, Alembic, Psycopg y Pydantic, y nuevo `Dockerfile` con `python:3.12-slim` | `apps/api/pyproject.toml`, `apps/api/Dockerfile` | `python3 -m pip install -e apps/api` o `docker build apps/api` | Bajo | Ninguno |
| **M0-02** | Transversal | Proveer motor de base de datos desacoplado | Implementar configuración de sesión SQLAlchemy 2.0 y Settings Pydantic | `apps/api/src/core/config.py`, `apps/api/src/core/database.py` | Importar engine e inicializar sesión en test | Bajo | M0-01 |
| **M0-03** | Transversal | Configurar herramienta de migraciones según AGENTS.md | Configurar Alembic (`alembic.ini`, `env.py`) conectado a Base declarativa | `apps/api/alembic.ini`, `apps/api/migrations/env.py` | `alembic check` o generación de migración vacía | Medio | M0-02 |
| **M0-04** | Transversal | Validar sintaxis DDL y soporte `btree_gist` en PostgreSQL 16 | Crear migración inicial Alembic con DDL portado de `docs/legacy-ref/db-migrations/` y aplicarla contra PostgreSQL | `apps/api/migrations/versions/001_initial.py` | `alembic upgrade head` contra Postgres | Alto | M0-03 |
| **M0-05** | Transversal | Habilitar arnés de pruebas automatizadas | Configurar `pytest`, fixtures de base de datos transaccional y cliente `httpx.AsyncClient` | `apps/api/tests/conftest.py`, `apps/api/pytest.ini` | `pytest apps/api/tests` retorna PASS | Bajo | M0-04 |

### Lote M1: Autenticación y RBAC (RN-10)
| ID | épica | por qué | cambio | archivos | verificación | riesgo | depende de |
|---|---|---|---|---|---|---|---|
| **M1-01** | Autenticación | Mapear usuarios del sistema en ORM | Modelo SQLAlchemy `SystemUser` con roles `admin` y `receptionist` y migración Alembic | `apps/api/src/models/user.py` | Test unitario de instanciación y persistencia | Bajo | M0-04 |
| **M1-02** | Autenticación | Criptografía y tokens de seguridad para sesiones | Servicio de hashing con bcrypt y generador/validador de JWT | `apps/api/src/core/security.py` | Tests unitarios de hash, verify y decode de tokens | Bajo | M0-01 |
| **M1-03** | Autenticación | Permitir inicio de sesión del personal administrativo | Endpoints `POST /api/auth/login` y `GET /api/auth/me` con schemas Pydantic | `apps/api/src/routers/auth.py`, `apps/api/src/schemas/auth.py` | Test de integración: login exitoso con usuario semilla `dev_seed.sql` | Medio | M1-01, M1-02 |
| **M1-04** | Autenticación | Cumplir RN-10 (Control de acceso por roles) | Dependencias de autorización `require_role('admin')` y `require_role('receptionist')` | `apps/api/src/core/dependencies.py` | Test de endpoints protegidos: 403 Forbidden ante rol indebido | Medio | M1-03 |

### Lote M2: Reservas, Disponibilidad y Concurrencia (RN-02)
| ID | épica | por qué | cambio | archivos | verificación | riesgo | depende de |
|---|---|---|---|---|---|---|---|
| **M2-01** | Reservas | Persistir entidades base con restricción GiST (RN-02) | Modelos SQLAlchemy `Room`, `Guest`, `Booking` con `ExcludeConstraint` sobre `stay_range` ignorando canceladas | `apps/api/src/models/room.py`, `apps/api/src/models/booking.py`, `apps/api/src/models/guest.py` | Test de BD: intentar insertar dos reservas solapadas genera IntegrityError | Alto | M0-04 |
| **M2-02** | Reservas | Atender consulta de catálogo disponible para web y chatbot | Endpoint `GET /api/rooms/availability` con filtros de fechas, adultos, niños y mascotas | `apps/api/src/routers/rooms.py`, `apps/api/src/services/booking.py` | Test de integración con casos de fechas libres vs ocupadas | Medio | M2-01 |
| **M2-03** | Reservas | Sustituir Redis por candados en PostgreSQL | Tabla `temporary_locks` y endpoints `POST /api/bookings/lock` y `POST /api/bookings/unlock` | `apps/api/src/models/lock.py`, `apps/api/src/routers/locks.py` | Test de concurrencia: dos locks simultáneos en mismas fechas uno falla con 409 | Alto | M2-02 |
| **M2-04** | Reservas | Registrar reservas confirmadas con abono parcial o total | Endpoint `POST /api/bookings/confirm` (lote, cálculo 50%/100%, UUID grupal) y `POST /api/bookings/test-paid` | `apps/api/src/routers/bookings.py`, `apps/api/src/schemas/booking.py` | Test: confirmación guarda lote en DB y libera locks temporales | Alto | M2-03 |
| **M2-05** | Reservas | Consultas, liquidación y cancelaciones (RN-03) | Endpoints `GET /api/bookings/group/{code}`, `POST .../pay-remaining`, `POST .../cancellation` y `GET /api/bookings/debug` | `apps/api/src/routers/bookings.py` | Tests de política de reembolso (100% >72h, 50% 24-72h, 0% <24h) y monitoreo debug | Medio | M2-04 |

### Lote M3: Desacople de Redis en Chatbot n8n y Conversaciones
| ID | épica | por qué | cambio | archivos | verificación | riesgo | depende de |
|---|---|---|---|---|---|---|---|
| **M3-01** | Reservas | Gestionar historial de soporte y chats | Modelo SQLAlchemy `Conversation` y endpoints `GET /api/conversations` y `POST /api/conversations/{id}/escalation` | `apps/api/src/models/conversation.py`, `apps/api/src/routers/conversations.py` | Test de consulta consumida por `Conversations.tsx` | Bajo | M2-01 |
| **M3-02** | Reservas | Atender escalamiento humano emitido por n8n | Endpoint `POST /api/notifications/agent-request` | `apps/api/src/routers/notifications.py` | Test HTTP de recepción de alerta de escalamiento | Bajo | M3-01 |
| **M3-03** | Reservas | Proveer persistencia de sesión a n8n para eliminar Redis | Endpoints `GET`, `POST`, `DELETE /api/chatbot/session/{wa_id}` respaldados en PostgreSQL | `apps/api/src/routers/chatbot_sessions.py` | Test de guardado, recuperación y expiración de sesión | Medio | M3-01 |
| **M3-04** | Reservas | Eliminar dependencia de Redis en el flujo activo n8n | Adaptar `flows/n8n/V8_ChatbotReservas.json` reemplazando los 5 nodos Redis por llamadas a los endpoints de sesión | `flows/n8n/V8_ChatbotReservas.json` | `python3 tests/chatbot/verify_n8n_flow_integrity.py` exitoso con 0 errores | Alto | M3-03 |
| **M3-05** | Reservas | Alinear script generador a Gemini 2.0 Flash y sin Redis | Actualizar `tests/chatbot/build_v8_chatbot_flow.py` (modelo `gemini-2.0-flash` y llamadas HTTP de sesión) | `tests/chatbot/build_v8_chatbot_flow.py` | Ejecución del script regenera el flujo V8 idéntico y consistente | Medio | M3-04 |

### Lote M4: Recepción Operativa, Ley 1581 (RN-12) y No-Show (RN-13)
| ID | épica | por qué | cambio | archivos | verificación | riesgo | depende de |
|---|---|---|---|---|---|---|---|
| **M4-01** | Reservas | Cumplir RN-12 (Autorización legal de datos Ley 1581) | Columnas `data_consent` y `data_consent_at` en `guest` y validación en endpoints de alta de reservas | `apps/api/src/models/guest.py`, `apps/api/src/schemas/booking.py` | Test de persistencia de flag de consentimiento y fecha | Bajo | M2-04 |
| **M4-02** | Reservas | Gestión física del huésped en recepción | Endpoints `POST /api/bookings/{id}/check-in` y `POST /api/bookings/{id}/check-out` con validación de saldo en 0 | `apps/api/src/routers/reception.py` | Test: checkout impedido si hay deuda; permitido si saldo es 0 | Medio | M2-05 |
| **M4-03** | Reservas | Cumplir RN-13 (Liberación de No-Show al mediodía) | Tarea de negocio o endpoint `POST /api/bookings/cron/process-no-shows` que a las 12:00 libere habitaciones no presentadas | `apps/api/src/services/reception.py`, `apps/api/src/routers/cron.py` | Test: reserva del día no confirmada a las 12:00 pasa a `no_show` y libera GiST | Medio | M4-02 |
| **M4-04** | Calendario | Vista de cuadrícula de ocupación para recepción | Router `/api/calendar` con endpoint `GET /api/calendar/matrix` por habitación y rango de fechas | `apps/api/src/routers/calendar.py` | Test de generación de matriz de ocupación para UI | Bajo | M2-05 |
| **M4-05** | Reservas | CRUD administrativo de catálogo de habitaciones | Endpoints `POST`, `PUT`, `DELETE /api/rooms/{id}` protegidos con rol Admin | `apps/api/src/routers/rooms.py` | Test: rechazo de eliminación si hay reservas pendientes | Medio | M1-04, M2-02 |

### Lote M5: Tienda, Finanzas y Sueldos (RN-11)
| ID | épica | por qué | cambio | archivos | verificación | riesgo | depende de |
|---|---|---|---|---|---|---|---|
| **M5-01** | Tienda | Modelar inventario y consumos en base de datos | Modelos SQLAlchemy `Product` y `Consumption` portados de migraciones SQL | `apps/api/src/models/store.py` | Test de inserción y consulta de stock | Bajo | M0-04, M2-01 |
| **M5-02** | Tienda | Permitir venta y cargo a la cuenta de la habitación | Endpoints `GET`, `POST /api/products` y `POST /api/consumptions` | `apps/api/src/routers/store.py` | Test: consumo registrado incrementa saldo adeudado de la reserva | Medio | M5-01, M4-02 |
| **M5-03** | Finanzas | Cumplir RN-11 (Modelado de remuneración mensual) | Modelos `PayrollConfig` (modalidad fija, comisión, mixta) y `OperatingExpense` | `apps/api/src/models/finance.py` | Test de asignación salarial a recepcionista | Bajo | M1-01 |
| **M5-04** | Finanzas | Cumplir RN-11 (Cálculo y liquidación de nómina) | Endpoints `GET /api/finance/salaries` y `POST /api/finance/salaries/settle` aplicando porcentajes de venta o fijos | `apps/api/src/routers/finance.py`, `apps/api/src/services/payroll.py` | Tests unitarios de cálculo salarial (fijo puro, 100% comisión, mixto) | Medio | M5-03, M2-05 |
| **M5-05** | Finanzas | Balance de ingresos y egresos hoteleros | Endpoint `GET /api/finance/report` (ingresos por reservas, consumos y egresos operativos) | `apps/api/src/routers/finance.py` | Test de conciliación contable contra reservas pagadas | Bajo | M5-04 |

### Lote M6: Reseñas, Cloudflare R2 y Cierre de Migración
| ID | épica | por qué | cambio | archivos | verificación | riesgo | depende de |
|---|---|---|---|---|---|---|---|
| **M6-01** | Reseñas | Gestión de calificaciones y opiniones de huéspedes | Modelo SQLAlchemy `Review` y endpoints `GET /api/reviews` y `POST /api/reviews` | `apps/api/src/models/review.py`, `apps/api/src/routers/reviews.py` | Test de creación y listado de reseñas (chatbot y Google) | Bajo | M0-04 |
| **M6-02** | Transversal | Almacenar comprobantes y backups sin Redis según AGENTS.md | Cliente S3/R2 (`boto3`) y endpoint para carga segura de comprobantes de pago | `apps/api/src/core/storage.py`, `apps/api/src/routers/storage.py` | Test de subida de archivo a bucket mock/real | Medio | M0-01 |
| **M6-03** | Transversal | Asegurar pipeline de CI automatizado para FastAPI | Actualizar `.github/workflows/ci.yml` para ejecutar `pytest` y validación de migraciones Alembic | `.github/workflows/ci.yml` | Ejecución de GitHub Actions exitosa en PR | Bajo | M0-05 |
| **M6-04** | Transversal | Actualizar documentación de diseño y diagramas | Adaptar `docs/Diagramas/` (01, 02, 03) y `docs/modulos/BackendAPI.md` reflejando FastAPI y Postgres | `docs/Diagramas/*.md`, `docs/modulos/*.md` | Revisión de coherencia documental sin menciones a tecnologías prohibidas | Bajo | M6-03 |
