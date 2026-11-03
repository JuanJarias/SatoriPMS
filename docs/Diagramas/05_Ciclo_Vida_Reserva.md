# 05. Ciclo de Vida de una Reserva y Política de Reembolso — SatoriPMS

## 1. Propósito del Diagrama

Este documento describe todos los estados por los que transita una reserva dentro de **SatoriPMS** desde que el viajero selecciona una habitación hasta que concluye su estadía o solicita una cancelación, mostrando de forma explícita cómo se calcula el reembolso **exclusivamente sobre el dinero que el huésped haya abonado hasta ese momento** (`Monto abonado : "paid_amount"`).

---

## 2. Diagrama de Estados de la Reserva y del Pago

Los estados representados corresponden exactamente a los valores que gestiona el servidor y la base de datos del hotel:
- **Estados de la reserva (`Estado de la reserva : "status"`):** `'pending_payment'`, `'confirmed'`, `'finished'`, `'cancelled'`.
- **Estados financieros (`Estado del pago : "payment_status"`):** `'pending'`, `'partial'`, `'paid'`, `'refunded'`.

```mermaid
stateDiagram-v2
    [*] --> BloqueoTemporal : Selección de habitación en WhatsApp o Web\n(Bloqueo en Redis por 15 minutos)

    state "Bloqueo Temporal en Memoria (15 min)" as BloqueoTemporal
    state "Pendiente de Pago\nstatus = 'pending_payment'\npayment_status = 'pending'" as PendientePago
    state "Confirmada con Anticipo del 50%\nstatus = 'confirmed'\npayment_status = 'partial'\npaid_amount = 50%" as ConfirmadaParcial
    state "Confirmada y Pagada al 100%\nstatus = 'confirmed'\npayment_status = 'paid'\npaid_amount = 100%" as ConfirmadaTotal
    state "Estadía Finalizada\nstatus = 'finished'\npayment_status = 'paid'" as Finalizada
    state "Reserva Cancelada\nstatus = 'cancelled'\npayment_status = 'refunded' o 'paid'" as Cancelada

    BloqueoTemporal --> [*] : Cancela en resumen, escribe "menú"\no inactividad (POST /api/bookings/unlock)
    BloqueoTemporal --> PendientePago : Registro sin pago inmediato
    BloqueoTemporal --> ConfirmadaParcial : Elige Opción 2 (Abono del 50%)\nPOST /api/bookings/confirm
    BloqueoTemporal --> ConfirmadaTotal : Elige Opción 1 (Pago del 100%)\nPOST /api/bookings/confirm

    PendientePago --> ConfirmadaParcial : Registra abono del 50%
    PendientePago --> ConfirmadaTotal : Registra pago del 100%
    PendientePago --> Cancelada : Cancelación antes de abonar\n(Reembolso = $0)

    ConfirmadaParcial --> ConfirmadaTotal : Liquida el 50% restante en WhatsApp o Recepción\nPOST /api/bookings/group/{code}/pay-remaining

    ConfirmadaParcial --> Cancelada : Solicita cancelación\n(Reembolso calculado sobre el 50% abonado)
    ConfirmadaTotal --> Cancelada : Solicita cancelación\n(Reembolso calculado sobre el 100% abonado)

    ConfirmadaTotal --> Finalizada : Salida del huésped (Check-out)\ncon consumos de tienda en $0

    Finalizada --> [*]
    Cancelada --> [*]
```

---

## 3. Árbol de Decisión de Reembolso sobre el Monto Efectivamente Pagado

Cuando un huésped solicita cancelar su reserva confirmada (`POST /api/bookings/group/{code}/cancellation`), el sistema toma dos datos reales de la reserva:
1. Las horas que faltan desde el momento de la cancelación hasta las **15:00 horas (3:00 p. m.) del día de entrada**.
2. El **monto efectivamente pagado por el cliente hasta ese instante (`Monto abonado : "paid_amount"`)**.

```mermaid
flowchart TD
    classDef start fill:#FAF7F2,stroke:#3E2723,stroke-width:2px,color:#3E2723
    classDef cond fill:#FFF8E7,stroke:#F59E0B,stroke-width:2px,color:#3E2723
    classDef r100 fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20
    classDef r50 fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#0D47A1
    classDef r0 fill:#FFEBEE,stroke:#C62828,stroke-width:2px,color:#B71C1C

    Inicio["Solicitud de Cancelación de Reserva<br/>Base de cálculo: Monto Abonado (paid_amount)<br/>Hora de referencia: 15:00 del día de llegada"]:::start

    Horas{"¿Cuántas horas faltan<br/>para el Check-in (15:00)?"}:::cond

    Tramo1["Más de 72 horas antes:<br/>Reembolso del 100% de lo abonado<br/>• Reserva pasa a status = 'cancelled'<br/>• payment_status = 'refunded'<br/>• Habitaciones liberadas de inmediato"]:::r100

    Tramo2["Entre 24 y 72 horas antes:<br/>Reembolso del 50% de lo abonado<br/>• Reserva pasa a status = 'cancelled'<br/>• payment_status = 'refunded'<br/>• Habitaciones liberadas de inmediato"]:::r50

    Tramo3["Menos de 24 horas o no presentación:<br/>Sin reembolso (0% de lo abonado)<br/>• Reserva pasa a status = 'cancelled'<br/>• Habitaciones liberadas de inmediato"]:::r0

    Ej100["Ejemplo sobre estadía de $200.000:<br/>• Si pagó el 100% ($200.000) -> Devuelve $200.000<br/>• Si abonó el 50% ($100.000) -> Devuelve $100.000"]:::r100
    Ej50["Ejemplo sobre estadía de $200.000:<br/>• Si pagó el 100% ($200.000) -> Devuelve $100.000<br/>• Si abonó el 50% ($100.000) -> Devuelve $50.000"]:::r50
    Ej0["Ejemplo sobre estadía de $200.000:<br/>• Si pagó el 100% ($200.000) -> Devuelve $0<br/>• Si abonó el 50% ($100.000) -> Devuelve $0"]:::r0

    Inicio --> Horas
    Horas -->|"> 72 horas"| Tramo1 --> Ej100
    Horas -->|"Entre 24h y 72h"| Tramo2 --> Ej50
    Horas -->|"< 24 horas"| Tramo3 --> Ej0
```

---

## 4. Garantías Financieras y Operativas del Ciclo de Vida

1. **Coherencia entre consulta y cancelación:** Tanto cuando el huésped consulta su reserva antes de decidir (`GET /api/bookings/group/{code}`) como cuando confirma la cancelación definitiva (`POST /api/bookings/group/{code}/cancellation`), el servidor aplica exactamente la misma fórmula sobre el monto abonado (`paid_amount`).
2. **Liberación inmediata de disponibilidad:** En cuanto el estado cambia a `'cancelled'`, la restricción de la base de datos deja de bloquear ese rango de fechas y la habitación vuelve a aparecer disponible en WhatsApp y en la aplicación web sin requerir intervención manual.
