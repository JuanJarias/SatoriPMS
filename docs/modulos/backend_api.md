# Módulo — Backend / API PMS

### 1. Estilo Arquitectónico

**Monolito modular con arquitectura hexagonal:** una única aplicación backend Spring Boot desplegable, estructurada internamente en módulos de dominio desacoplados, con puertos y adaptadores hacia servicios externos (WhatsApp Meta API, Redis, PostgreSQL, Pasarela de Pago, Google Gemini).

Se descarta microservicios para la v1 por el tamaño del hotel, el alcance del equipo, y porque los procesos core (reservar, pagar, check-in, actualizar estado de habitación) se benefician de permanecer en una sola transacción.

---

### 2. Módulos Lógicos Internos

| Módulo | Responsabilidad |
|---|---|
| **Reservas y Disponibilidad** | Consulta de inventario, bloqueos temporales en Redis, persistencia y batch de reservas, consulta de detalles por código y cancelación con cálculo de reembolsos según RN-03. |
| **Habitaciones y Estadías** | Catálogo de habitaciones, calendario operativo, estados (disponible, ocupada, en limpieza, mantenimiento, bloqueo temporal), check-in y check-out. |
| **Clientes, Reseñas y Fidelización** | Registro y consulta de huéspedes por teléfono/documento, historial de estadías, métricas de huésped recurrente y calificaciones. |
| **Tienda e Inventario** | Catálogo de productos, existencias, ventas directas y consumos asociados a reservas de habitación. |
| **Finanzas y Reportes** | Liquidación de ingresos, registro de egresos operativos, cálculo de sueldos y exportación de informes contables. |
| **Identidad y Seguridad** | Autenticación JWT, roles y permisos (Administrador, Recepcionista), auditoría de operaciones. |
| **Conversaciones y Notificaciones** | Gestión del estado conversacional del chatbot y transferencia a recepcionista humano. |
| **Recomendación Asistida** | Interpretación de mensajes en lenguaje libre (via Google Gemini) para apoyar la reserva guiada o autónoma — solo sugiere y normaliza, nunca muta el estado de negocio de forma autónoma. |

---

### 3. Integraciones Externas

| Integración | Uso | Regla de Seguridad y Negocio |
|---|---|---|
| **WhatsApp Business API (Meta)** | Canal principal con huéspedes y envío de confirmaciones. | Validación de firma del webhook y prevención de duplicados (no procesar el mismo mensaje dos veces si Meta lo reenvía). |
| **MercadoPago (Sandbox / Prod)** | Cobro de reservas y pasarela de pago. | Confirmación de reserva sujeta a validación estricta del webhook de pago; nunca por pantalla de éxito del cliente. |
| **Google Gemini 2.0 Flash** | Normalización de texto libre y asistente de recomendación de habitaciones. | Capa de interpretación únicamente; nunca confirma disponibilidad, precios ni bloqueos por sí sola. |
| **Almacenamiento de archivos** | Guardar recibos, facturas, soportes de egresos y otros documentos. | La base de datos solo guarda referencia y metadatos; los archivos se protegen con permisos y enlaces controlados. |

---

### 4. Mecanismo de Integridad y Anti-Doble Reserva

La integridad de disponibilidad opera en dos capas concurrentes:
1. **Bloqueo Temporal (Redis):** Bloqueo en memoria con tiempo de vida (TTL) de 15 minutos (900 segundos) mientras el huésped diligencia sus datos o efectúa el pago.
2. **Restricción Transaccional Excluyente (PostgreSQL):**
   ```sql
   CONSTRAINT no_overlapping_bookings EXCLUDE USING gist (
       room_id WITH =,
       stay_range WITH &&
   ) WHERE (status IN ('pending_payment', 'confirmed'))
   ```
   PostgreSQL rechaza a nivel de motor cualquier intento concurrente de solapamiento de fechas para la misma habitación mientras el estado sea `pending_payment` o `confirmed`.

---

### 5. Contrato de Endpoints API REST

#### 5.1 Habitaciones (`/api/rooms`)

* **`GET /api/rooms/availability`**
  * *Parámetros:* `checkIn` (YYYY-MM-DD), `checkOut` (YYYY-MM-DD), `adults` (int), `children` (int), `pet` (boolean).
  * *Respuesta (200):* Lista de habitaciones libres en PostgreSQL y no bloqueadas en Redis, con tarifa y capacidades.
* **`GET /api/rooms/recommend`**
  * *Propósito:* Recomendación asistida por IA según descripción en lenguaje natural.
  * *Parámetros:* `query` (string libre del huésped).
  * *Respuesta (200):* Habitaciones sugeridas con justificación.

#### 5.2 Reservas (`/api/bookings`)

* **`POST /api/bookings/lock`**
  * *Body:* `{ "roomIds": [long], "checkIn": string, "checkOut": string }`
  * *Respuesta (200):* `{ "lockTokens": [...], "ttlSeconds": 900, "totalPrice": number }`
* **`POST /api/bookings/confirm`**
  * *Body:* `BookingBatchRequestDto` (waId, guestName, guestDocument, companions, checkIn, checkOut, adults, children, hasPet, rooms: `[{ roomId, lockToken }]`).
  * *Respuesta (200):* `BookingBatchResponseDto` con `reservationGroupId`, lista de IDs creados, `totalPrice`, estado `pending_payment`.
* **`POST /api/bookings/test-paid`**
  * *Propósito:* Idéntico a `/confirm` pero establece estado `confirmed`/`paid` de inmediato. Solo disponible cuando `BOOKING_TEST_PAYMENT_ENABLED=true` en entorno de desarrollo.
* **`GET /api/bookings/group/{code}`**
  * *Propósito:* Consulta de reserva por los primeros 8 caracteres del `reservationGroupId` o el UUID completo.
  * *Respuesta (200):* `ReservationDetailsDto` con detalle de habitaciones, huésped, fechas, total, estado y cálculo de política de reembolso (RN-03).
* **`POST /api/bookings/group/{code}/cancellation`**
  * *Propósito:* Cancelación del grupo completo de reservas asociado al código.
  * *Efecto:* El estado cambia a `cancelled` (sin eliminar registros); las habitaciones quedan disponibles de inmediato al salir del `EXCLUDE` de PostgreSQL.
  * *Respuesta (200):* `CancellationResponseDto` con porcentaje y monto de reembolso estimado según RN-03.
* **`POST /api/bookings/{id}/payment-confirmation`**
  * *Body:* Datos de confirmación de pago (referencia de pasarela).
  * *Respuesta (200):* Reserva individual actualizada a `confirmed` / `paid`.
* **`GET /api/bookings/debug`**
  * *Propósito:* Lista detallada de todas las reservas con datos de huésped y habitación. Usada por el panel de administración del frontend.

#### 5.3 Reseñas (`/api/reviews`)

* **`GET /api/reviews`** — Lista calificaciones y comentarios visibles para huéspedes.
* **`POST /api/reviews`** — Crea una reseña asociada a una reserva finalizada (máximo una por reserva, HU-04).

#### 5.4 Conversaciones y Notificaciones (`/api/conversations`)

* **`GET /api/conversations`** — Lista de conversaciones activas con su estado en Redis.
* **`POST /api/conversations/{id}/escalation`** — Notificación de solicitud de agente humano a recepción y activación de `agent_active = true` en Redis.
* **`POST /api/notifications/agent-request`** — Notifica a la app web cuando se escala una conversación (para mostrar en el panel de conversaciones en tiempo real).
