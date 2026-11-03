# Diagrama 05 — Máquina de Estados y Ciclo de Vida de la Reserva

Este diagrama documenta la **máquina de estados finita** de una reserva en SatoriPMS, detallando las transiciones de pago, la vigencia de los bloqueos temporales en Redis y las políticas de cancelación y reembolso proporcional (**Regla de Negocio RN-03**).

---

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8EEF5', 'primaryTextColor': '#1B365D', 'primaryBorderColor': '#2C4D75', 'lineColor': '#2C4D75' }}}%%
stateDiagram-v2
    [*] --> DRAFT_LOCK : Huésped selecciona habitación en WhatsApp / Web

    state DRAFT_LOCK {
        [*] --> CandadoEnMemoria
        CandadoEnMemoria : Llave Redis con TTL = 900s (15 min)
        CandadoEnMemoria : Habitación invisible para otros clientes
    }

    DRAFT_LOCK --> LIBERADA_TIMEOUT : Expiran 15 minutos sin completar pago
    LIBERADA_TIMEOUT --> [*] : Habitación reaparece disponible

    DRAFT_LOCK --> CONFIRMED_PARTIAL : Huésped abona 50% anticipo (payment_status='partial')
    DRAFT_LOCK --> CONFIRMED_PAID : Huésped abona 100% total (payment_status='paid')

    state CONFIRMED_PARTIAL {
        ConfirmadaConSaldo : Reserva garantizada en PostgreSQL (EXCLUDE GIST)
        ConfirmadaConSaldo : Saldo pendiente = 50% restante
    }

    state CONFIRMED_PAID {
        ConfirmadaTotal : Reserva garantizada en PostgreSQL (EXCLUDE GIST)
        ConfirmadaTotal : Saldo pendiente = $0.00 COP
    }

    CONFIRMED_PARTIAL --> CONFIRMED_PAID : Pago de saldo restante (/pay-remaining) en recepción

    CONFIRMED_PARTIAL --> EVALUACION_CANCELACION : Solicitud de Cancelación (CU-02)
    CONFIRMED_PAID --> EVALUACION_CANCELACION : Solicitud de Cancelación (CU-02)

    state EVALUACION_CANCELACION {
        [*] --> ValidarAnticipacion
        ValidarAnticipacion : Cálculo de días calendario hasta Check-in (RN-03)
    }

    EVALUACION_CANCELACION --> CANCELLED_REEMBOLSO_100 : > 15 días antes del Check-in
    EVALUACION_CANCELACION --> CANCELLED_REEMBOLSO_50 : Entre 7 y 14 días antes del Check-in
    EVALUACION_CANCELACION --> CANCELLED_SIN_REEMBOLSO : < 7 días antes del Check-in

    state CANCELLED_REEMBOLSO_100 {
        R100 : Reembolso del 100% sobre paid_amount
        R100 : Habitación liberada para reventa
    }

    state CANCELLED_REEMBOLSO_50 {
        R50 : Reembolso del 50% sobre paid_amount (retención 50%)
        R50 : Habitación liberada para reventa
    }

    state CANCELLED_SIN_REEMBOLSO {
        R0 : Reembolso del 0% (Penalidad total por cancelación tardía)
        R0 : Habitación liberada para reventa
    }

    CANCELLED_REEMBOLSO_100 --> [*]
    CANCELLED_REEMBOLSO_50 --> [*]
    CANCELLED_SIN_REEMBOLSO --> [*]

    CONFIRMED_PAID --> CHECKED_IN : Huésped llega al hotel (CU-03)
    CONFIRMED_PARTIAL --> CHECKED_IN : Huésped liquida saldo restante y hace Check-in

    state CHECKED_IN {
        EstadiaActiva : Huésped alojado físicamente
        EstadiaActiva : Habitación en estado 'OCCUPIED'
        EstadiaActiva : Registro de consumos de tienda (RN-04)
    }

    CHECKED_IN --> CHECKED_OUT : Huésped entrega habitación y liquida tienda (CU-04)

    state CHECKED_OUT {
        SalidaExitosa : Factura final generada
        SalidaExitosa : Habitación pasa a estado 'CLEANING' (Aseo)
        SalidaExitosa : Envío automático de solicitud de reseña
    }

    CHECKED_OUT --> [*]
```

---

### Tabla de Reglas de Transición y Devoluciones (RN-03)

| Estado Origen | Evento Desencadenante | Estado Destino | Regla de Negocio Aplicada |
|---|---|---|---|
| `DRAFT_LOCK` | Transcurren 15 min sin abono | `LIBERADA_TIMEOUT` | La llave expira en Redis (`DEL room:{id}:lock`); inventario vuelve a la matriz pública. |
| `DRAFT_LOCK` | Pago del 50% confirmado | `CONFIRMED_PARTIAL` | Se asienta en PostgreSQL con `paid_amount = total * 0.5` y `payment_status = 'partial'`. |
| `DRAFT_LOCK` | Pago del 100% confirmado | `CONFIRMED_PAID` | Se asienta en PostgreSQL con `paid_amount = total` y `payment_status = 'paid'`. |
| `CONFIRMED_*` | Cancelación > 15 días antes | `CANCELLED` | **Reembolso 100%:** Se devuelve el 100% del monto efectivamente pagado (`paid_amount`). |
| `CONFIRMED_*` | Cancelación 7–14 días antes | `CANCELLED` | **Reembolso 50%:** Se devuelve el 50% de `paid_amount`; el hotel retiene el otro 50%. |
| `CONFIRMED_*` | Cancelación < 7 días antes | `CANCELLED` | **Penalidad Total:** 0% de reembolso; el hotel retiene el 100% de lo pagado. |
| `CHECKED_IN` | Check-out completado | `CHECKED_OUT` | Exige validar que todos los consumos de tienda (`RN-04`) estén pagados en `$0 COP`. |
