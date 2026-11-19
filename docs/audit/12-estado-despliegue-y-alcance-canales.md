# Estado Actual, Prueba de WhatsApp, Topología de Despliegue y Alcance Exacto por Canal (Chatbot vs. Web)

**Fecha:** 2026-11-19  
**Rama:** `migracion-fastapi`

---

## 1. ¿Qué llevamos actualmente del proyecto y qué requerimientos están satisfechos?

Ya tenemos **3 de los 4 lotes del backend (M0, M1 y M3 + M2) terminados, probados con 18 tests automatizados en verde y subidos a GitHub**:

| Lote | Estado | Requerimientos y Reglas de Negocio Satisfechas |
| :--- | :---: | :--- |
| **M0 — Infraestructura & Candado GiST** | **100% Completado** | • Backend FastAPI (Python 3.12 ASGI) + SQLAlchemy 2.0 async + Alembic.<br>• PostgreSQL 16 con extensión `btree_gist` y seed de las **9 habitaciones reales**.<br>• **RN-02 (Anti-sobreventa nativo):** Restricción `EXCLUDE USING gist` sobre `(room_id, daterange(check_in, check_out, '[)'))` para estados activos (`BLOQUEADA_TEMPORAL`, `CONFIRMADA`, `EN_CURSO`).<br>• Endpoint de monitoreo ITIL 4 `GET /api/v1/health`. |
| **M1 — Identidad, JWT, RBAC y Auditoría** | **100% Completado** | • **RN-10 (Roles RBAC):** Autenticación JWT (`HS256`) y hashing `bcrypt` con roles `Administrador` y `Recepcionista`.<br>• **E6 (Auditoría Inmutable):** Tabla *append-only* `audit_log` + servicio `record_audit()` + consulta exclusiva de admin `GET /api/v1/auth/audit-logs`. |
| **M2 — Disponibilidad y Bloqueo 15 min** | **100% Completado** | • **RN-01 (Capacidad y recargo):** Cálculo automático de tarifa por noche + recargo por adulto adicional y filtro de capacidad/mascotas.<br>• **RN-12 (Ley 1581):** Validación obligatoria de consentimiento Habeas Data (`habeas_data_accepted`).<br>• **RN-02 (Candado 15 min):** Expiración inline (`expires_at <= NOW()`) en `GET /api/v1/rooms/availability` y transacción atómica en `POST /api/v1/bookings/lock` (`HTTP 409` ante colisión simultánea). |
| **M3 — Flujo n8n V10, Sesiones en DB, Pagos HMAC y RN-03** | **100% Completado** | • **Cero Redis:** Flujo `flows/n8n/V10_ChatbotReservas.json` (91 nodos) migrado para guardar sesiones y links Wompi en la tabla `conversation` de PostgreSQL 16.<br>• **Seguridad de Pagos:** Webhook `POST /api/v1/payments/webhook` con firma `HMAC-SHA256` (`X-Hub-Signature-256`) e idempotencia por `payment_id`.<br>• **Ciclo Grupal (`TS-XXXX`) y RN-03:** Confirmación batch (100% o abono 50%), consulta por código `TS-XXXX`, pago del 50% restante, cancelación con reembolso proporcional **RN-03** (>72h: 100%, 24–72h: 50%, <24h: 0%) y escalamiento a agente humano. |
| **M4 — Integración de las 12 Pantallas Web** | **Siguiente paso inmediato** | • Conectar las 12 pantallas React de `origin/main` (`apps/web/src/screens/`) con FastAPI (Check-in/Check-out, Calendario, CRUD Habitaciones, Salgados Café, Eventos, Reseñas, Dashboard y Admin). |

---

## 2. ¿Cómo y cuándo probaremos la API de WhatsApp?

La prueba de WhatsApp tiene **dos niveles** para que nunca dependas de un único punto de fallo:

1. **Nivel 1 — Prueba E2E del motor del Chatbot sin Meta (¡Disponible hoy mismo al levantar n8n!):**
   - Los scripts que trajimos en `tests/chatbot/` (`test_e2e_v9_completo.js`, `test_pago_wompi_v9.js`, `suite_pruebas_chatbot_v8.js`) envían exactamente el mismo JSON que envía Meta Cloud API directo al webhook de n8n (`POST http://localhost:5678/webhook/whatsapp-webhook`).
   - Esto prueba el 100% de los 91 nodos de n8n + Gemini + FastAPI + PostgreSQL GiST sin necesitar todavía el token de Meta.
2. **Nivel 2 — Prueba con tu celular físico en WhatsApp Real (Apenas Meta te deje crear el portfolio en ~1 hora o al cierre de M4):**
   - En cuanto Meta te habilite el botón *Continuar*, copias 3 datos en `.env`: `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID` y `WHATSAPP_VERIFY_TOKEN`.
   - Expones el puerto `5678` de n8n con la URL pública HTTPS (Cloudflare Tunnel / zrok / ngrok o Railway), pegas `https://<tu-tunel>/webhook/whatsapp-webhook` en Meta for Developers → *Webhooks*, y escribes *"Hola"* desde tu WhatsApp personal al número de prueba de Meta.

---

## 3. Ruta de Despliegue: ¿Dónde se aloja cada componente?

Tienes dos modalidades listas (Nube Gratuita 24/7 o Híbrida Local con Túnel para la sustentación):

| Componente | ¿Qué hace? | Opción A: Despliegue en Nube (Producción / Demo) | Opción B: Híbrido en tu PC (Demo Local Segura) |
| :--- | :--- | :--- | :--- |
| **Base de Datos (`PostgreSQL 16 + btree_gist`)** | Tablas, candado GiST RN-02, sesiones de chat y auditoría. | **Supabase** (PostgreSQL 16 administrado gratis). | Contenedor Docker `satori_postgres` (`localhost:5432`). |
| **Backend API (`FastAPI + Uvicorn`)** | Lógica de negocio, JWT, disponibilidad, candado 15m, webhooks. | **Railway** o **Render** (contenedor Docker desde `apps/api/Dockerfile`). | `uvicorn apps.api.main:app --port 8080` (o contenedor `satori_api`). |
| **Orquestador (`n8n` + Webhooks Meta/Wompi)** | Recibe `/webhook/whatsapp-webhook` y `/webhook/wompi-events`. | **Railway** (imagen `n8nio/n8n`) con URL HTTPS fija. | Contenedor Docker `satori_n8n` (`localhost:5678`) expuesto a internet con **zrok / ngrok / Cloudflare Tunnel**. |
| **Frontend Web (`React 18 + Vite`)** | Panel de Recepción y Administración (12 pantallas). | **Vercel** (conectado a `VITE_API_URL` de Railway). | `npm run dev` en `http://localhost:5173`. |

---

## 4. Alcance Exacto por Canal: ¿Qué queda implementado y qué queda fuera?

### A. Canal 1: Chatbot de WhatsApp (Huésped — `V10_ChatbotReservas.json` + FastAPI)
* **SÍ queda 100% implementado y operativo:**
  1. **Reserva Guiada paso a paso:** Fechas ──► disponibilidad real ──► bloqueo temporal de 15 min en PostgreSQL GiST ──► captura de adultos/niños, aviso **Ley 1581**, nombre y cédula ──► desglose tarifa base + recargo (**RN-01**) ──► confirmación con código `TS-XXXX` y generación de link de pago **Wompi** (100% o anticipo 50%).
  2. **Asistente IA con Gemini Flash:** Interpretación de reservas en lenguaje natural en un solo mensaje, soporte multi-habitación y confirmación interactiva.
  3. **Consulta de reserva activa (`TS-XXXX`):** Verificación con cédula del titular, estado del pago y política de reembolso.
  4. **Pago del 50% de saldo restante y Cancelación con Reembolso (RN-03):** Cálculo automático del 100% (>72h), 50% (24–72h) o 0% (<24h) sobre lo abonado y liberación inmediata de la habitación.
  5. **Conciliación de Webhook Wompi / HMAC:** Confirmación automática al aprobarse el pago y notificación por WhatsApp al huésped.
  6. **Escalamiento a Recepcionista Humano:** Pausa el bot (`agent_active = true`) y alerta a la bandeja web de recepción.
  7. **Persistencia de sesión e inactividad (10/11 min):** Todo en PostgreSQL 16 (cero Redis), liberando candados si el usuario abandona el chat.
* **Queda FUERA en el Chatbot:**
  - Pedidos de cafetería (Salgados Café) por WhatsApp (se registran desde el panel web de recepción/mostrador).
  - Notificación proactiva automática 24h antes del check-in (**RN-06**, requiere plantilla aprobada de pago en cuenta comercial verificada de Meta).

### B. Canal 2: Aplicación Web (Administrador y Recepcionista — `apps/web` + FastAPI en Lote M4)
Al integrar en **Lote M4** las 12 pantallas que tu compañero dejó en `origin/main` (`apps/web/src/screens/`):
* **SÍ queda implementado y conectado a FastAPI:**
  1. **Login y Roles RBAC (`Login.tsx`, `Admin.tsx`):** Ingreso real con JWT para `Administrador` y `Recepcionista`, gestión de usuarios y **bitácora de auditoría inmutable (`audit_log`)**.
  2. **Dashboard Ejecutivo y Financiero (`Dashboard.tsx`):** KPIs en tiempo real de ocupación, ingresos cobrados, saldos pendientes y estado de las 9 habitaciones.
  3. **Calendario y Gestión de Reservas (`CalendarView.tsx`, `Reservas.tsx`):** Grilla visual de las 9 habitaciones, creación manual de reservas en recepción, confirmación de pagos, cancelación **RN-03** y liberación de bloqueos.
  4. **Operación de Mostrador Check-in / Check-out (`Operacion.tsx`):** Paso a estado `EN_CURSO` (check-in), registro de consumos al folio de la habitación y liquidación en check-out con auditoría.
  5. **CRUD de Habitaciones (`Rooms.tsx`):** Creación/edición de tarifas, capacidades y estado físico (`available`, `occupied`, `cleaning`, `maintenance`).
  6. **Salgados Café y Tienda (`Restaurante.tsx`, `Tienda.tsx`):** Menú de cafetería/tienda y órdenes cargadas al folio de la habitación o venta directa.
  7. **Eventos Especiales y Reseñas (`Eventos.tsx`, `Resenas.tsx`):** Configuración de temporadas/descuentos para ferias y visualización de reseñas.
  8. **Bandeja de Chatbot (`Chatbot.tsx`):** Monitoreo de conversaciones de WhatsApp y atención de chats escalados a humano.
* **Queda FUERA de alcance en la Web (Backlog v1.1 según `AGENTS.md`):**
  - **No-Show automático a las 12:00 p. m. (RN-13):** Excluido explícitamente por decisión de arquitectura en `AGENTS.md`.
  - **Facturación electrónica DIAN y exportación contable compleja a `.xlsx` / Nómina de sueldos de empleados (HU-07 / RN-11):** Fuera de alcance porque la fórmula de comisiones quedó pendiente de definir por el cliente en `AGENTS.md`.
  - **Backups cifrados nocturnos a Cloudflare R2:** Los respaldos se ejecutan localmente con `pg_dump` / `scripts/backup.sh`.
