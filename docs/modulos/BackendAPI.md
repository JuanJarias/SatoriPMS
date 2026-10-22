# Módulo — Backend / API PMS

## 1. Estilo Arquitectónico

El backend es un **monolito modular con arquitectura hexagonal**: una única aplicación Spring Boot desplegable, estructurada internamente en módulos de dominio desacoplados, con puertos y adaptadores hacia los servicios externos (WhatsApp Meta API, Redis, PostgreSQL, pasarela de pago y Google Gemini). Los adaptadores permiten reemplazar un servicio externo sin reescribir la lógica central de reservas, habitaciones o finanzas.

Se descartan los microservicios para la v1 por el tamaño del hotel, el alcance del equipo y porque los procesos centrales (reservar, pagar, hacer check-in, actualizar el estado de una habitación) se benefician de ejecutarse dentro de una sola transacción, sin los costos de múltiples despliegues, comunicación por red y consistencia distribuida.

El backend es el dueño único de las reglas de negocio. Ningún canal calcula precios, determina disponibilidad ni aplica políticas por su cuenta: el chatbot y la aplicación web consultan y mutan el estado exclusivamente a través de esta API.

## 2. Módulos Lógicos Internos

Los ocho módulos comparten el mismo despliegue y la misma fuente de datos transaccional. Cada uno conserva una responsabilidad clara, pero no son aplicaciones independientes.

| Módulo | Responsabilidad |
|---|---|
| **Reservas y Disponibilidad** | Consulta de inventario, bloqueos temporales en Redis, persistencia batch de reservas con pagos parciales o totales, pago de saldo pendiente (`pay-remaining`), consulta de detalles por código y cancelación con cálculo de reembolsos según RN-03. |
| **Habitaciones y Estadías** | Catálogo de habitaciones, calendario operativo, estados (disponible, ocupada, en limpieza, mantenimiento, bloqueo temporal), check-in y check-out. |
| **Clientes, Reseñas y Fidelización** | Registro y consulta de huéspedes por teléfono o documento, historial de estadías, métricas de huésped recurrente y calificaciones persistidas en PostgreSQL (`ReviewRepository`). |
| **Tienda e Inventario** | Catálogo de productos, existencias, ventas directas y consumos asociados a reservas de habitación. |
| **Finanzas y Reportes** | Liquidación de ingresos, registro de egresos operativos, reembolsos, cálculo de sueldos y exportación de informes contables. |
| **Identidad y Seguridad** | Autenticación JWT, roles y permisos (Administrador y Recepcionista), recuperación de acceso y auditoría de operaciones. |
| **Conversaciones y Notificaciones** | Estado conversacional del chatbot, transferencia a recepcionista humano y mensajes de confirmación y seguimiento. |
| **Recomendación Asistida** | Interpretación de mensajes en lenguaje libre mediante Google Gemini para apoyar la reserva guiada o la reserva por IA. Solo sugiere y normaliza; nunca muta el estado de negocio de forma autónoma. |

## 3. Integraciones Externas

| Integración | Uso | Regla de seguridad y negocio |
|---|---|---|
| **WhatsApp Business Cloud API (Meta)** | Canal principal con los huéspedes y envío de confirmaciones. | Validación de la firma del webhook y prevención de procesamiento duplicado de mensajes. |
| **MercadoPago (Sandbox y producción)** | Cobro de reservas y reembolsos. | La confirmación de una reserva queda sujeta a la validación estricta del webhook de pago; nunca se confirma por una pantalla de éxito del cliente. |
| **Google Gemini Flash Lite** | Extracción estructurada de mensajes libres de reserva, normalización de textos y recomendación de habitaciones. Modelo `gemini-flash-lite-latest` o `gemini-3.5-flash-lite`. | Solo interpreta y extrae JSON; no confirma reservas ni bloqueos sin validación del backend. |
| **Google Reviews y Maps** | Recolección de opiniones públicas en Google Business. | Redirección oficial mediante Place ID: `https://search.google.com/local/writereview?placeid=${GOOGLE_PLACE_ID}`. Google no permite crear reseñas de forma programática sin la autenticación del usuario final. |
| **Almacenamiento de archivos** | Recibos, facturas, soportes de egresos y otros documentos. | La base de datos solo guarda la referencia y los metadatos; los archivos se protegen con permisos y enlaces controlados. |

## 4. Mecanismo de Integridad y Anti-Doble Reserva

La disponibilidad de una habitación no puede garantizarse solo mostrando un calendario actualizado, porque dos personas pueden intentar reservarla casi al mismo tiempo desde canales distintos. Por eso la integridad opera en dos capas concurrentes.

1. **Bloqueo temporal en Redis.** Un bloqueo en memoria, con tiempo de vida de 15 minutos (900 segundos), protege la habitación mientras el huésped diligencia sus datos o efectúa el pago. Se implementa con scripts Lua en `RedisLockService` para que la adquisición y la liberación sean atómicas. El bloqueo se libera al confirmar la reserva, al vencer el TTL o cuando el flujo termina sin reserva.
2. **Restricción transaccional excluyente en PostgreSQL.**

   ```sql
   CONSTRAINT no_overlapping_bookings EXCLUDE USING gist (
       room_id WITH =,
       stay_range WITH &&
   ) WHERE (status IN ('pending_payment', 'confirmed'))
   ```

   PostgreSQL rechaza a nivel de motor cualquier intento concurrente de solapar fechas para la misma habitación mientras el estado sea `pending_payment` o `confirmed`. Al cancelar una reserva (estado `cancelled`), las fechas se liberan automáticamente al salir del `WHERE` de la restricción.

El backend vuelve a validar la disponibilidad dentro de la transacción antes de confirmar una reserva. Si el pago no se completa antes de que venza el bloqueo, este deja de afectar la disponibilidad.

## 5. Reglas de Cálculo

**Valor de la estadía.** Es la suma, para cada habitación seleccionada, del precio por noche multiplicado por el número de noches, más los recargos por huéspedes adicionales calculados según RN-01.

**Modalidades de pago.** Con `paymentOption: "full"` la reserva queda con `payment_status = 'paid'` y `paid_amount = total_price`. Con `paymentOption: "deposit"` queda con `payment_status = 'partial'` y `paid_amount = total_price / 2`. El saldo pendiente es siempre `total_price - paid_amount`.

**Reembolso por cancelación.** Se calcula sobre `paid_amount`, no sobre el valor total de la reserva, aplicando el porcentaje de RN-03 según las horas restantes hasta el check-in de las 15:00 del día de llegada.

## 6. Contrato de Endpoints API REST

Todos los endpoints usan JSON. Los endpoints del canal operativo (administración y recepción) requieren un token JWT en el encabezado de autorización; los endpoints consumidos por el chatbot se llaman desde n8n dentro de la red interna de Docker.

### 6.1 Habitaciones (`/api/rooms`)

**`GET /api/rooms/availability`**
Parámetros: `checkIn` (YYYY-MM-DD), `checkOut` (YYYY-MM-DD), `adults` (int), `children` (int), `pet` (boolean).
Respuesta (200): lista de habitaciones libres en PostgreSQL y no bloqueadas en Redis, con tarifa, capacidades (base, máxima y niños), recargo por huésped extra y si admiten mascotas.

**`GET /api/rooms/recommend`**
Propósito: recomendación asistida por IA según una descripción en lenguaje natural.
Parámetros: `query` (texto libre del huésped).
Respuesta (200): habitaciones sugeridas con justificación. La recomendación solo considera habitaciones disponibles y nunca reemplaza la validación de disponibilidad.

### 6.2 Reservas (`/api/bookings`)

**`POST /api/bookings/lock`**
Body: `{ "waId": string, "roomId": long, "checkIn": string, "checkOut": string }`, o una lista de habitaciones para bloquear varias a la vez.
Respuesta (200): `{ "lockToken": string, "ttlSeconds": 900, "totalPrice": number }`.
Si alguna habitación ya no está disponible, el bloqueo no se otorga y la respuesta indica que la habitación no está disponible.

**`POST /api/bookings/confirm`**
Body: `BookingBatchRequestDto` con `waId`, `guestName`, `guestDocument`, `companions`, `checkIn`, `checkOut`, `adults`, `children`, `hasPet`, `paymentOption` (`"deposit"` o `"full"`) y `rooms: [{ roomId, lockToken }]`.
Comportamiento: valida cada `lockToken`, vuelve a validar disponibilidad y capacidad (RN-01), crea un registro `booking` por habitación con un `reservation_group_id` común, registra el pago según `paymentOption` y libera los bloqueos de Redis. El campo `source` queda como `chatbot` o `web` según el canal de origen.
Respuesta (200): `BookingBatchResponseDto` con `reservationGroupId`, lista de IDs creados, `totalPrice`, `status`, `paymentStatus`, `paidAmount` y `pendingBalance`.

**`GET /api/bookings/group/{code}`**
Propósito: consulta de una reserva por los primeros 8 caracteres del `reservationGroupId` o por el UUID completo.
Respuesta (200): `ReservationDetailsDto` con el detalle de habitaciones, huésped, fechas, `totalPrice`, `paidAmount`, `pendingBalance`, `canPayRemaining` (boolean), `canCancel` (boolean), estado de la reserva y estado de pago, y el cálculo de la política de reembolso (RN-03). No incluye información sobre el estado operativo de la habitación.

**`POST /api/bookings/group/{code}/pay-remaining`**
Propósito: liquidar el saldo restante de una reserva con abono parcial previo.
Efecto: `payment_status = 'paid'` y `paid_amount = total_price`.
Respuesta (200): `BookingBatchResponseDto` con saldo restante en 0 y estado pagado.

**`POST /api/bookings/group/{code}/cancellation`**
Propósito: cancelar el grupo completo de reservas asociado al código.
Efecto: el estado cambia a `cancelled`; `payment_status` cambia a `refunded` cuando aplica devolución y se conserva cuando el porcentaje de reembolso es 0 %. Las habitaciones quedan disponibles de inmediato y la reserva se conserva en la base de datos como historial.
Respuesta (200): `CancellationResponseDto` con el porcentaje y el monto de reembolso estimado según RN-03.

**`GET /api/bookings/debug`**
Propósito: lista detallada de todas las reservas con datos de huésped y habitación, usada por el panel de administración del frontend.

### 6.3 Reseñas (`/api/reviews`)

**`GET /api/reviews?limit=10`**
Propósito: consultar las últimas reseñas desde PostgreSQL ordenadas por `created_at DESC`.
Respuesta (200): lista de objetos `Review` con `id`, `authorName`, `rating`, `comment`, `source` y `createdAt`.

**`POST /api/reviews`**
Body: `ReviewRequestDto` con `waId`, `authorName`, `rating`, `comment`, `bookingId` y `source`.
Comportamiento: si viene `waId`, busca al huésped y asocia `guest_id`. Valida que `rating` esté entre 1 y 5. Si viene `bookingId`, valida que no exista ya otra reseña para esa reserva.
Respuesta (200): `{ "status": "ok", "message": "Reseña guardada exitosamente", "id": long, "rating": int, "comment": string }`.

### 6.4 Conversaciones y Notificaciones (`/api/conversations`)

**`GET /api/conversations`**
Lista de conversaciones activas con su estado en Redis, incluyendo las escaladas pendientes de atención humana.

**`POST /api/conversations/{id}/escalation`**
Notificación de solicitud de agente humano a recepción. Se invoca cuando el huésped solicita hablar con un agente dentro del horario de atención.

## 7. Eventos en Tiempo Real

El backend emite eventos por WebSocket con protocolo STOMP hacia la aplicación web cuando cambia el estado de una habitación, se crea o cambia una reserva, o se escala una conversación. La aplicación web se suscribe a estos eventos para actualizar el calendario y el centro de conversaciones sin recargar la página.

## 8. Interpretación Asistida con Gemini

El módulo de Recomendación Asistida recibe texto libre y devuelve JSON estricto con los campos de la reserva (`checkIn`, `checkOut`, `adults`, `children`, `hasPet`, `guestName`, `guestDocument`, `companions`) y un resumen de lo entendido. También puede clasificar la intención del mensaje dentro de un flujo (responder el paso actual, modificar un dato anterior, reiniciar, cancelar o escalar). Toda salida de la IA se trata como una sugerencia: el backend valida formato, rangos de fechas, disponibilidad, capacidad y reglas de negocio antes de aceptar cualquier dato.
