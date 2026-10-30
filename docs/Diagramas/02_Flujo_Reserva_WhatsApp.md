# Diagrama 02 — Flujo Integral de Reserva por WhatsApp

Este diagrama describe el ciclo conversacional completo de reserva a través de **WhatsApp Business**, desde la recepción del mensaje inicial hasta la confirmación de la reserva y persistencia transaccional en la base de datos con abono parcial o total.

---

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8EEF5', 'primaryTextColor': '#1B365D', 'primaryBorderColor': '#2C4D75', 'lineColor': '#2C4D75' }}}%%
sequenceDiagram
    autonumber
    actor Guest as 📱 Huésped (WhatsApp)
    participant Meta as ☁️ Meta Cloud API
    participant N8N as ⚡ n8n (Flujo V8)
    participant Gemini as 🤖 Gemini Flash Lite
    participant Redis as 🔴 Redis 7
    participant API as ☕ Spring Boot API
    participant DB as 🐘 PostgreSQL 16

    Note over Guest,Meta: 1. Inicio y saludo del huésped
    Guest->>Meta: "Hola, quisiera reservar para 2 personas del 15 al 18 de nov"
    Meta->>N8N: Webhook Event (Mensaje entrante JSON)

    Note over N8N,Redis: 2. Control de sesión y silenciamiento
    N8N->>Redis: GET session:{waId}:agent_active
    Redis-->>N8N: null / false (Bot activo)

    Note over N8N,Gemini: 3. Interpretación y extracción con IA (HU-09)
    N8N->>Gemini: Prompt con mensaje natural + schema JSON
    Gemini-->>N8N: JSON: {checkIn: "2026-11-15", checkOut: "2026-11-18", guests: 2}

    Note over N8N,API: 4. Consulta de inventario real (CU-01.1)
    N8N->>API: GET /api/bookings/availability?checkIn=2026-11-15&checkOut=2026-11-18
    API->>DB: SELECT habitaciones libres sin reserva CONFIRMED/CHECKED_IN
    DB-->>API: Lista de habitaciones disponibles
    API->>Redis: Filtrar habitaciones con lock activo (room:*:lock)
    API-->>N8N: 200 OK: [Hab 101 - Suite Bambú ($180k), Hab 102 - Estándar ($140k)]

    N8N->>Meta: Mensaje con catálogo de habitaciones disponibles
    Meta->>Guest: Presenta opciones interactivas y tarifas por noche

    Note over Guest,API: 5. Selección y Bloqueo Temporal de 15 Minutos (CU-01.2 / RN-02)
    Guest->>Meta: Selecciona "Habitación 101 - Suite Bambú"
    Meta->>N8N: Evento de selección
    N8N->>API: POST /api/bookings/lock {roomId: 1, checkIn: "2026-11-15", checkOut: "2026-11-18"}
    API->>Redis: EVAL script Lua: SET room:1:lock token NX EX 900
    Redis-->>API: 1 (Candado adquirido con TTL de 15 minutos)
    API-->>N8N: 200 OK: {lockToken: "uuid-lock-101", expiresAt: "15:45:00"}

    Note over N8N,Guest: 6. Captura de datos personales y elección de abono
    N8N->>Meta: Solicita nombre completo y documento del titular
    Guest->>Meta: "Carlos Mendoza, CC 1118234567"
    Meta->>N8N: Datos del huésped normalizados
    N8N->>Meta: Modalidad de abono: 50% anticipo ($270k) o 100% total ($540k)
    Guest->>Meta: Selecciona "50% Anticipo"

    Note over N8N,DB: 7. Confirmación y Registro Transaccional (CU-01.4 / Flyway V5)
    Meta->>N8N: Opción de pago confirmada
    N8N->>API: POST /api/bookings/batch {rooms: [1], titular: "Carlos Mendoza", doc: "1118234567", paidAmount: 270000, totalAmount: 540000}
    API->>DB: INSERT INTO booking (status='CONFIRMED', payment_status='partial', paid_amount=270000)
    Note over DB: Validación excluyente EXCLUDE USING gist (Cero solapamiento)
    DB-->>API: 201 Created: {groupCode: "ST-7842A", bookingId: 42}
    API->>Redis: DEL room:1:lock (Libera candado temporal en memoria)
    API-->>N8N: 201 Created con código de reserva de 8 caracteres

    Note over N8N,Guest: 8. Voucher digital de confirmación inmediata
    N8N->>Meta: Envía voucher con código ST-7842A, fechas, abono y saldo pendiente
    Meta->>Guest: 📄 ¡Reserva Confirmada! Código: ST-7842A. Saldo pendiente: $270.000 COP al check-in.
```

---

### Puntos Clave de la Arquitectura Conversacional

1. **Idempotencia de Sesión:** Redis almacena el estado de la conversación bajo la clave `session:{waId}`, permitiendo que el usuario retome el flujo si se interrumpe momentáneamente.
2. **Candado de 15 Minutos:** Durante el paso 5, la habitación queda completamente invisible para otros usuarios. Si el cliente no completa los datos antes de que expire el TTL, Redis purga la llave automáticamente y la habitación vuelve al inventario público.
3. **Persistencia de Abono:** En el paso 7, la base de datos almacena el valor efectivamente pagado en la columna `paid_amount` (`V5__add_paid_amount_and_review_entity.sql`), estableciendo el estado de pago como `partial` para liquidar el saldo pendiente al momento del check-in.
