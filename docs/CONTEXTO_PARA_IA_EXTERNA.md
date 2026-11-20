# Contexto Maestro del Proyecto Torre Satori PMS (Listo para Copiar y Pegar en Cualquier IA)

> **Instrucción:** Copia todo el bloque de abajo y pégalo al inicio de tu conversación con cualquier IA externa para que entienda al 100% qué es el proyecto, qué stack usamos, qué reglas están prohibidas, qué llevamos construido y en qué paso exacto estamos.

---

```markdown
# CONTEXTO DEL PROYECTO: TORRE SATORI PMS

## 1. Propósito y Dominio del Negocio
Somos estudiantes de Ingeniería Telemática (Proyecto Integrador II, Universidad Icesi) desarrollando **Torre Satori PMS**, un sistema de gestión hotelera (Property Management System) hecho a la medida para el **Hotel Torre Satori** (hotel boutique familiar ubicado en Sevilla, Valle del Cauca, Colombia, con **9 habitaciones** y ~40 reservas/mes).
- **Problema que resuelve:** Eliminar el riesgo de sobreventa (overbooking por cruce entre WhatsApp y cuaderno físico), automatizar la atención 24/7 por WhatsApp sin pagar comisiones en dólares de PMS comerciales, controlar consumos de cafetería (Salgados Café) y tienda cargados al folio de la habitación, y centralizar el calendario, finanzas y auditoría del hotel.
- **Principio de arquitectura:** **Un solo backend central (API REST unificada)** sirve simultáneamente a **dos canales**:
  1. **Canal Huésped (Chatbot de WhatsApp):** Consulta disponibilidad, bloquea habitación por 15 minutos, cotiza con o sin IA (Gemini), recibe link de pago (Wompi), consulta/cancela su reserva (`TS-XXXX`) o pide hablar con un recepcionista humano.
  2. **Canal Interno (Aplicación Web React):** Usado por el **Administrador** (dueño) y el **Recepcionista** para gestionar calendario, reservas manuales, check-in/check-out, Salgados Café, tienda, eventos, reseñas y bitácora de auditoría.

## 2. Stack Tecnológico Oficial y Restricciones Estrictas
- **Backend:** Python 3.12+ con **FastAPI** (ASGI asíncrono + Uvicorn), **Pydantic v2**, **SQLAlchemy 2.0 async** (`psycopg` v3) y migraciones con **Alembic**.
- **Base de Datos:** **PostgreSQL 16** con la extensión **`btree_gist`** activa.
- **Frontend Web:** **React 18 + Vite + TypeScript + Tailwind CSS + TanStack Query** (12 pantallas operativas en `apps/web/src/screens/`).
- **Orquestador de Chatbot:** **n8n self-hosted** (flujo `flows/n8n/V10_ChatbotReservas.json` de 91 nodos) + **Google Gemini Flash** (únicamente como intérprete de lenguaje natural y recomendador; Gemini NUNCA confirma disponibilidad ni precios por su cuenta) + **WhatsApp Cloud API (Meta)** + **Wompi** (links de pago y webhook de eventos).
- **TECNOLOGÍAS PROHIBIDAS (Regla de arquitectura):** Está estrictamente prohibido usar **Java, Spring Boot, JPA, Maven, Flyway o Redis**. Toda la persistencia de bloqueos temporales y sesiones conversacionales de WhatsApp vive en **PostgreSQL 16** (cero Redis).

## 3. Reglas de Negocio Críticas (RN) Implementadas
- **RN-01 (Capacidad y recargo por persona adicional):** Cada una de las 9 habitaciones tiene capacidad base y máxima. Si los adultos superan la capacidad base sin exceder la máxima, se cobra recargo por persona adicional por noche: `total = (noches * precio_noche) + (noches * recargo_extra * adultos_extra)`.
- **RN-02 (Anti-sobreventa nativo GiST y bloqueo temporal de 15 min):**
  - La tabla `booking` en PostgreSQL 16 tiene la restricción:
    `EXCLUDE USING gist (room_id WITH =, daterange(check_in, check_out, '[)') WITH &&) WHERE (status IN ('BLOQUEADA_TEMPORAL', 'CONFIRMADA', 'EN_CURSO'))`
  - El intervalo semiabierto `[)` permite que un huésped salga el día X a las 11:00 a. m. y otro entre el mismo día X a las 3:00 p. m. sin colisión.
  - Cuando alguien selecciona una habitación, se inserta una fila `BLOQUEADA_TEMPORAL` con `expires_at = NOW() + 15 min`. Antes de insertar, en la misma transacción se expiran (`EXPIRADA`) los bloqueos vencidos de esa habitación, y la consulta de disponibilidad filtra inline `expires_at > NOW()`. Si dos usuarios intentan bloquear al mismo milisegundo, PostgreSQL GiST rechaza al segundo y FastAPI devuelve `HTTP 409 Conflict`.
- **RN-03 (Política de reembolsos por cancelación):** Calculada sobre lo efectivamente pagado (`paid_amount`) respecto a las 15:00 del día de check-in: **> 72h antes = 100%**, **entre 24h y 72h = 50%**, **< 24h = 0%**. Al pasar a `CANCELADA`, la fila sale del índice GiST y libera la habitación de inmediato.
- **RN-05 (Check-in / Check-out):** Al hacer check-in en mostrador, la reserva pasa a `EN_CURSO` y la habitación a `occupied` dejando registro en auditoría.
- **RN-10 y E6 (Seguridad JWT, Roles RBAC y Auditoría Inmutable):** Roles `Administrador` y `Recepcionista`, contraseñas con `bcrypt`, tokens JWT `HS256` y tabla `audit_log` *append-only* (fecha, actor, acción, entidad, detalle JSON sin datos sensibles).
- **RN-12 (Ley 1581 de 2012 - Habeas Data):** Consentimiento obligatorio (`habeas_data_accepted = true`) antes de registrar datos del huésped.
- **Estados en Español en Base de Datos:** `BLOQUEADA_TEMPORAL`, `CONFIRMADA`, `EN_CURSO`, `EXPIRADA`, `CANCELADA`.

## 4. ¿Qué Llevamos Construido y Probado Actualmente? (Estado al 100% en Código)
En la rama `migracion-fastapi` ya completamos los lotes **M0, M1, M2, M3 y M4** con **21/21 pruebas automatizadas en `pytest` pasando en verde** y el frontend compilando con **0 errores de TypeScript (`npm run build`)**:
1. **Lote M0 (`apps/api/models/`, `alembic/versions/001_initial_schema.py`):** Motor FastAPI + SQLAlchemy 2.0 async, extensión `btree_gist`, tablas `room` (con las 9 habitaciones sembradas: 101–103 Estándar, 201–203 Doble, 301–303 Suite), `guest`, `booking` (con `ExcludeConstraint` GiST) y `audit_log`, más endpoint `GET /api/v1/health`.
2. **Lote M1 (`core/security.py`, `dependencies/auth.py`, `routers/auth.py`, `002_system_users.py`):** Login JWT (`POST /api/v1/auth/login`), perfil (`GET /api/v1/auth/me`), dependencia `require_role(['Administrador', 'Recepcionista'])`, servicio `record_audit()` y consulta de bitácora para admin (`GET /api/v1/auth/audit-logs`).
3. **Lote M2 (`routers/rooms.py`, `routers/bookings.py`, `services/room_service.py`, `services/booking_service.py`):** Disponibilidad real `GET /api/v1/rooms/availability` (ignorando `expires_at <= NOW()`) y bloqueo atómico `POST /api/v1/bookings/lock` (`HTTP 200` al ganador, `HTTP 409` a colisiones concurrentes).
4. **Lote M3 (`models/conversation.py`, `routers/conversations.py`, `routers/payments.py`, `routers/n8n_compat.py`, `flows/n8n/V10_ChatbotReservas.json`):**
   - Flujo n8n `V10` (91 nodos) adaptado con **0 nodos Redis** (las sesiones y links Wompi se guardan en PostgreSQL vía `GET/PUT/DELETE /api/v1/conversations/session/{key}`).
   - Webhook de pagos `POST /api/v1/payments/webhook` con validación `HMAC-SHA256` (`X-Hub-Signature-256` + `hmac.compare_digest`) e idempotencia por `payment_id`.
   - Endpoints de ciclo grupal (`TS-XXXX`): `/api/bookings/confirm`, `/api/bookings/group/{code}`, `/pay-remaining`, `/cancellation` (**RN-03**) y `/api/notifications/agent-request`.
5. **Lote M4 (`routers/web_operations.py`, `apps/web/src/screens/`, `start-dev.sh`):**
   - 12 pantallas React integradas (`Login`, `Dashboard`, `Reservas`, `CalendarView`, `Operacion`, `Rooms`, `Tienda`, `Restaurante` Salgados Café, `Eventos`, `Resenas`, `Chatbot`, `Admin`).
   - Endpoints de Check-in (`EN_CURSO`), Check-out, CRUD de habitaciones con bloqueo de borrado si hay reserva activa (**TC-02**), comandas de Salgados Café al folio (**TC-03**), eventos con descuento (**TC-04**) y reseñas.
   - Script `./start-dev.sh` que levanta PostgreSQL 16, Alembic, FastAPI (`:8080`) y React (`:5173`) en un solo comando.

## 5. ¿En Qué Paso Exacto Estamos Ahora Mismo? (Paso 5: Meta Cloud API + n8n + Despliegue)
Acabamos de desbloquear y crear el **Portfolio Comercial "Torre Satori"** en **Meta Business Suite** y ya tenemos creada la App **Torre Satori PMS** (`App ID: 1013079941261698`) en Meta for Developers.
Lo único que vamos a hacer a continuación es:
1. Vincular la app `Torre Satori PMS` al portfolio comercial `Torre Satori` en Meta for Developers → **WhatsApp → Inicio rápido / Configuración de la API** para obtener `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID` y registrar el número de celular de prueba.
2. Generar el token permanente con un **Usuario del Sistema** en Meta Business Suite (`Configuración -> Usuarios -> Usuarios del sistema`).
3. Conectar el webhook público HTTPS de **n8n** (`/webhook/whatsapp-webhook` con `WHATSAPP_VERIFY_TOKEN`) y desplegar en la nube (**Supabase** para PostgreSQL 16 + **Railway** para FastAPI/n8n + **Vercel** para React).
```
