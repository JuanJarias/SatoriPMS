# Análisis del Trabajo en `origin/main` (Flujos n8n V9/V10 y Frontend) y Plan de Integración con FastAPI

**Fecha:** 2026-11-19  
**Rama actual:** `migracion-fastapi`  
**Rama inspeccionada:** `origin/main` (hasta commit `3b83df5`)

---

## 1. ¿Qué es n8n y cómo funciona en SatoriPMS?

**n8n** es un **orquestador visual de flujos de trabajo (workflow automation)** basado en nodos. En términos telemáticos, funciona como un **router/adaptador de mensajería en la frontera**:
1. **No tienes que programar servidores de sockets para Meta:** cada cajita ("nodo") en n8n hace una tarea puntual: recibir un Webhook HTTP, ejecutar un condicional (`IF`/`Switch`), transformar un JSON en JavaScript (`Code`), o hacer una petición HTTP (`HTTP Request`) a nuestra API FastAPI, a Gemini o a Wompi.
2. **Flujo de un mensaje:**
   `Celular del Huésped (WhatsApp)` ──► `Meta Cloud API` ──(Webhook HTTPS)──► `n8n (Puerto 5678)` ──(HTTP interno)──► `FastAPI (Puerto 8080)` ──► `PostgreSQL 16 (GiST)`.

---

## 2. ¿Qué hizo exactamente tu compañero en `origin/main`?

Al hacer `git fetch origin` e inspeccionar `origin/main` (`d0b17ad..3b83df5`), encontramos tres bloques de trabajo muy valiosos:

### A. Flujos de Chatbot en `flows/n8n/V9_ChatbotReservas.json` y `V10_ChatbotReservas.json` (91 nodos)
Tu compañero construyó un flujo completo de **91 nodos** con:
1. **3 Puertas de Entrada (Webhooks en n8n):**
   - `GET /webhook/whatsapp-webhook`: Responde automáticamente el reto `hub.challenge` cuando conectas Meta for Developers.
   - `POST /webhook/whatsapp-webhook`: Recibe cada mensaje del huésped desde WhatsApp.
   - `POST /webhook/wompi-events`: Recibe la confirmación de pago desde **Wompi** y valida criptográficamente el checksum SHA-256 (`WOMPI_EVENTS_SECRET`).
2. **Recorridos del Huésped en WhatsApp:**
   - **Opción 1 (Reserva Guiada):** Pide fechas (`checkIn`, `checkOut`) ──► consulta disponibilidad en el backend ──► bloquea la habitación 15 min ──► pide cantidad de adultos/niños, consentimiento **Ley 1581**, nombre y cédula ──► calcula tarifa base + recargo (**RN-01**) ──► genera link de pago en **Wompi** (100% o abono del 50%).
   - **Opción 2 (Asistente IA con Gemini):** El huésped escribe todo en lenguaje natural, n8n invoca a Gemini Flash para extraer JSON estructurado, confirma con el usuario y bloquea una o varias habitaciones.
   - **Opciones 3, 4 y 5:** Consulta de reserva por código `TS-XXXX`, pago del 50% restante, cancelación con reembolso proporcional (**RN-03**) y escalamiento a agente humano en recepción.
3. **Suite de Pruebas del Chatbot (`tests/chatbot/`):**
   - Scripts automatizados (`test_e2e_v9_completo.js`, `test_pago_wompi_v9.js`, `suite_pruebas_chatbot_v8.js`) que simulan conversaciones completas y webhooks de Wompi contra n8n.

### B. Pantallas Completas del Frontend Web (`apps/web/src/screens/`)
Además de n8n, en `origin/main` se agregaron las pantallas React que mencionabas hace un momento:
- `Dashboard.tsx` (Dashboard financiero y KPIs), `Reservas.tsx`, `CalendarView.tsx`, `Operacion.tsx` (Check-in/out), `Rooms.tsx` (CRUD Habitaciones), `Tienda.tsx`, `Restaurante.tsx` (Salgados Café), `Eventos.tsx`, `Resenas.tsx`, `Chatbot.tsx` y `Admin.tsx` (Auditoría y usuarios).

---

## 3. Hallazgo Crítico: ¿Qué debemos alinear para que el flujo n8n funcione con nuestro FastAPI?

El flujo `V9/V10` de tu compañero fue diseñado contra los contratos del backend anterior. Para que funcione de inmediato con nuestro **FastAPI + PostgreSQL 16 GiST (sin Redis)** hay dos puntos clave:

| Punto de Integración | Qué espera el flujo n8n de tu compañero (`V9/V10`) | Cómo lo resolvemos en `migracion-fastapi` |
| :--- | :--- | :--- |
| **1. Rutas y formato JSON (`camelCase` vs `snake_case`)** | n8n llama a:<br>• `GET /api/rooms/availability?checkIn=...&checkOut=...&adults=...&children=...&pet=...`<br>• `POST /api/bookings/lock` enviando `{waId, roomId, checkIn, checkOut}` y esperando `{lockToken, ttlSeconds, totalPrice}`<br>• `POST /api/bookings/unlock` con `{locks: [...]}`<br>• `POST /api/bookings/confirm`<br>• `GET /api/bookings/group/{code}`<br>• `POST /api/bookings/group/{code}/cancellation`<br>• `POST /api/bookings/group/{code}/pay-remaining`<br>• `POST /api/notifications/agent-request` | En **Lote M3** exponemos en FastAPI tanto las rutas canónicas `/api/v1/...` como los alias compatibles `/api/...` aceptando y devolviendo `camelCase` (`lockToken = str(booking_id)`, `pricePerNight`, etc.), respaldados por nuestro candado GiST en PostgreSQL 16. |
| **2. Estado de sesión en n8n (7 nodos Redis en `V9/V10`)** | El JSON `V9/V10` tiene 7 nodos `n8n-nodes-base.redis` para guardar el paso de la conversación (`session:{wa_id}`). | En **Lote M3** creamos en FastAPI la tabla `conversation` (`GET/PUT/DELETE /api/v1/conversations/session/{wa_id}`) como exige `AGENTS.md` (cero Redis) y adaptamos el flujo `flows/n8n/V10_ChatbotReservas.json` para que consulte la sesión vía HTTP a FastAPI en lugar de Redis. |

---

## 4. ¿Cuál es el siguiente paso a partir de este preciso instante?

1. **Respecto a Meta for Developers:** Deja esa pestaña en pausa durante 1 hora (o agrega a tu compañero como Admin en *Roles de la app* para que él cree el portfolio comercial desde su cuenta con antigüedad). **No nos detiene en absoluto.**
2. **Paso inmediato (Ejecutar Lote M3 en FastAPI + Integrar Flujo n8n V10):**
   - Traer el flujo `flows/n8n/V10_ChatbotReservas.json` de tu compañero a nuestra rama `migracion-fastapi` y reemplazar sus 7 nodos de Redis por llamadas HTTP a nuestra tabla `conversation` en FastAPI/PostgreSQL.
   - Implementar en FastAPI (**Lote M3**):
     1. Tabla y endpoints de sesión conversacional (`/api/v1/conversations/session/{wa_id}`) y escalamiento (`/api/notifications/agent-request`).
     2. Confirmación de reserva (`POST /api/bookings/confirm` y webhook `POST /api/v1/payments/webhook` con validación criptográfica HMAC-SHA256 + idempotencia, generando código `TS-XXXX` y registrando en `audit_log`).
     3. Compatibilidad dual (`camelCase` / `snake_case`) en `/api/rooms/availability`, `/api/bookings/lock` y `/api/bookings/unlock` para que el flujo n8n de tu compañero funcione al 100% con nuestro candado GiST de PostgreSQL 16.
     4. Tests en `pytest` (`tests/test_payments_webhook.py` y `tests/test_conversations.py`).
