# Diagrama 04 — Gestión Operativa en Recepción (App Web & WebSockets)

Este diagrama modela la interacción entre el personal de recepción en la **App Web (React 18)**, la sincronización bidireccional mediante **WebSockets STOMP**, y los procesos de negocio en el backend (Check-in, Check-out, consumos de tienda RN-04 y liquidación de saldos).

---

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8EEF5', 'primaryTextColor': '#1B365D', 'primaryBorderColor': '#2C4D75', 'lineColor': '#2C4D75' }}}%%
sequenceDiagram
    autonumber
    actor Rec as 💻 Recepcionista (App Web)
    participant Front as ⚛️ React 18 / Vite (Tailwind)
    participant WS as 🔌 WebSocket STOMP (/ws-satori)
    participant API as ☕ Spring Boot API
    participant DB as 🐘 PostgreSQL 16

    Note over Rec,Front: 1. Inicio de Turno y Carga de Calendario (HU-03)
    Rec->>Front: Autenticación con JWT (Rol Recepcionista)
    Front->>API: GET /api/rooms/occupancy (Matriz 12 habitaciones)
    API->>DB: Consulta reservas del mes (CONFIRMED, CHECKED_IN, CHECKED_OUT)
    DB-->>API: Listado de ocupación
    API-->>Front: JSON con cuadrícula de estados
    Front->>WS: Suscripción a canal /topic/calendar-updates
    Front-->>Rec: Renderiza Calendario Interactivo con códigos de color

    Note over Rec,DB: 2. Proceso de Check-in y Liquidación de Saldo (CU-03)
    Rec->>Front: Huésped llega a recepción con código "ST-7842A"
    Front->>API: GET /api/bookings/group/ST-7842A
    API->>DB: Consulta reserva: Estado 'partial', abonado $270.000, pendiente $270.000
    API-->>Front: Retorna detalle de reserva y saldo por cobrar
    Rec->>Front: Cobra saldo restante en efectivo/datáfono y confirma Check-in
    Front->>API: POST /api/bookings/group/ST-7842A/pay-remaining {paymentMethod: 'CASH'}
    API->>DB: UPDATE booking SET paid_amount = total_amount, payment_status = 'paid'
    Front->>API: POST /api/bookings/42/check-in
    API->>DB: UPDATE booking SET status = 'CHECKED_IN', actual_check_in = NOW()
    API->>WS: Broadcast evento {roomId: 1, newStatus: 'OCCUPIED'}
    WS-->>Front: Actualiza en vivo color de la habitación a Rojo (Ocupada)

    Note over Rec,DB: 3. Proceso de Check-out y Consolidación de Consumos (CU-04 / RN-04)
    Rec->>Front: Selecciona Habitación 101 para Check-out
    Front->>API: GET /api/rooms/1/pending-charges
    API->>DB: Consulta consumos cargados (Minibar, café especial, lavandería)
    DB-->>API: [2 Cafés especiales: $14.000, 1 Agua: $4.000]
    API-->>Front: Total consumos adicionales: $18.000 COP
    Rec->>Front: Factura y cobra consumos finales
    Front->>API: POST /api/bookings/42/check-out {consumptionsPaid: true}
    API->>DB: UPDATE booking SET status = 'CHECKED_OUT', actual_check_out = NOW()
    API->>DB: UPDATE room SET status = 'CLEANING' (Pasa a aseo y desinfección)
    API->>WS: Broadcast evento {roomId: 1, newStatus: 'CLEANING'}
    WS-->>Front: Actualiza en vivo color a Amarillo (En limpieza)
    Front-->>Rec: Check-out completado exitosamente y habitación enviada a limpieza
```

---

### Módulos y Reglas de Negocio en Recepción

1. **Sincronización por WebSockets (`HU-03.1`):** Cualquier cambio realizado por WhatsApp (bloqueo o reserva nueva) emite un evento al canal `/topic/calendar-updates`, actualizando la pantalla del recepcionista sin necesidad de recargar la página (*zero polling*).
2. **Liquidación de Saldos (`/pay-remaining`):** Permite cobrar el 50% restante a huéspedes que reservaron con abono previo, unificando la cuenta antes de emitir la llave.
3. **Consolidación de Consumos (RN-04):** Durante el check-out, la API audita los cargos de tienda cargados a la habitación y no permite cerrar la estadía hasta que el saldo de consumos quede en `$0 COP`.
