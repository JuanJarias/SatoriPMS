# Especificación de Endpoints REST del Backend Legado (Java/Spring)

Documento de referencia para la construcción de los routers de FastAPI con paridad funcional y compatibilidad con el frontend React y el chatbot n8n.

---

## 1. Reservas y Disponibilidad (`BookingController.java`)

### A. Consulta de Disponibilidad
- **Ruta:** `GET /api/rooms/availability`
- **Parámetros Query:**
  - `checkIn` (date, YYYY-MM-DD, requerido)
  - `checkOut` (date, YYYY-MM-DD, requerido)
  - `adults` (int, requerido)
  - `children` (int, opcional, default 0)
  - `pet` (boolean, opcional, default false)
- **Respuesta (200 OK):** Lista de habitaciones disponibles que cumplen fechas, capacidad y admisión de mascota.
- **Regla:** Excluir habitaciones con reservas confirmadas/pendientes (RN-02) o con candado activo.

### B. Bloqueo Temporal (15 minutos)
- **Ruta:** `POST /api/bookings/lock`
- **Body:** `{ "roomId": number, "checkIn": string, "checkOut": string }`
- **Respuesta (200 OK):** `{ "lockToken": string (UUID), "ttlSeconds": 900, "totalPrice": number }`
- **Errores:** 409 Conflict si la habitación no está libre; 400 Bad Request si fechas son inválidas.
- **Nota migración:** Se sustituye Redis por PostgreSQL con expiración transaccional o tabla de locks.

### C. Liberación Inmediata de Bloqueos
- **Ruta:** `POST /api/bookings/unlock`
- **Body:** `{ "roomId": number, "lockToken": string }` o `{ "locks": [{ "roomId": number, "lockToken": string }] }`
- **Respuesta (200 OK):** `{ "released": number }`

### D. Confirmación de Reserva (Individual o Grupal)
- **Ruta:** `POST /api/bookings/confirm`
- **Body (`BookingBatchRequestDto`):**
  ```json
  {
    "waId": "573001234567",
    "guestName": "Nombre Huésped",
    "guestDocument": "12345678",
    "companions": "Acompañante 1",
    "checkIn": "2026-12-01",
    "checkOut": "2026-12-03",
    "adults": 2,
    "children": 0,
    "hasPet": false,
    "source": "chatbot | web",
    "paymentOption": "deposit | full",
    "rooms": [{ "roomId": 1, "lockToken": "uuid" }]
  }
  ```
- **Respuesta (200 OK):**
  ```json
  {
    "reservationGroupId": "uuid",
    "totalPrice": 350000.00,
    "bookingIds": [101],
    "roomIds": [1],
    "status": "confirmed",
    "paymentStatus": "partial | paid",
    "paidAmount": 175000.00,
    "pendingBalance": 175000.00
  }
  ```
- **Errores:** 409 Conflict si hay colisión; 400 Bad Request si falta algún dato.

### E. Consulta de Reserva por Código
- **Ruta:** `GET /api/bookings/group/{code}`
- **Parámetro Path:** `code` (string, 8 primeros caracteres del UUID de grupo o UUID completo).
- **Respuesta (200 OK):** Detalles completos de la reserva, habitaciones, total, abonado, saldo pendiente y desglose de política de reembolso (RN-03).
- **Errores:** 404 Not Found si no existe.

### F. Cancelación de Reserva Grupal (RN-03)
- **Ruta:** `POST /api/bookings/group/{code}/cancellation`
- **Respuesta (200 OK):** `{ "code": "...", "status": "cancelled", "refundPercentage": 100|50|0, "refundAmount": number, "cancelledBookingIds": [...], "freedRoomNumbers": [...] }`
- **Errores:** 404 Not Found si no existe; 409 Conflict si ya está cancelada.

### G. Pago de Saldo Restante
- **Ruta:** `POST /api/bookings/group/{code}/pay-remaining`
- **Respuesta (200 OK):** Actualiza `payment_status` a `paid`, `paidAmount` al total y `pendingBalance` a 0.
- **Errores:** 409 Conflict si no tiene saldo pendiente o está cancelada.

### H. Monitoreo y Verificación de Reservas (Debug)
- **Ruta:** `GET /api/bookings/debug`
- **Respuesta (200 OK):** Lista de todas las reservas ordenadas por `createdAt` desc, consumida por `ReservasDebug.tsx`.

---

## 2. Conversaciones (`ConversationController.java`)

### A. Listar Conversaciones
- **Ruta:** `GET /api/conversations`
- **Respuesta (200 OK):** Lista de conversaciones con `id`, `whatsappPhone`, `status`, `step`, `checkIn`, `checkOut`, `selectedRoomId`, `adults`, `children`, `withPet`, `quotedTotal`, `updatedAt`. Consumida por `Conversations.tsx`.

### B. Escalamiento a Agente Humano
- **Ruta:** `POST /api/conversations/{id}/escalation`
- **Respuesta (200 OK):** Confirmación de notificación de escalado.

---

## 3. Reseñas y Opiniones (`ReviewController.java`)

### A. Listar Reseñas
- **Ruta:** `GET /api/reviews?limit=10`
- **Respuesta (200 OK):** Lista de reseñas ordenadas cronológicamente (`id`, `authorName`, `rating`, `comment`, `source`, `createdAt`).

### B. Crear Reseña
- **Ruta:** `POST /api/reviews`
- **Body:** `{ "rating": 5, "comment": "...", "waId": "...", "bookingId": 123, "authorName": "...", "source": "chatbot|google|web" }`
- **Respuesta (200 OK):** `{ "status": "ok", "id": number, "rating": number, "comment": string }`
