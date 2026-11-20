# 03. Prevención de Sobreventa: Doble Candado en PostgreSQL — SatoriPMS

## 1. Propósito del Diagrama

Uno de los riesgos más críticos para cualquier hotel es la **sobreventa**: que dos clientes distintos intenten reservar la última habitación disponible para las mismas fechas al mismo tiempo.

Este documento explica visualmente cómo **SatoriPMS** elimina ese riesgo con un **doble candado que vive íntegramente en la base de datos PostgreSQL** (el servidor central no usa Redis):
1. **Primer Candado (bloqueo temporal de 15 minutos):** Desde el segundo exacto en que un viajero elige una habitación, se guarda una reserva en estado `BLOQUEADA_TEMPORAL` con una hora de vencimiento (`expires_at`). Si el viajero no avanza, el bloqueo expira solo.
2. **Segundo Candado (reserva firme):** Cuando el viajero entrega sus datos, la misma fila pasa a `PENDIENTE_PAGO` (a la espera del pago aprobado) y luego a `CONFIRMADA`, sin vencimiento.

Ambos candados son la **misma restricción matemática** del motor de base de datos (`EXCLUDE USING gist`), que impide que dos filas activas de una misma habitación tengan fechas cruzadas. Por eso no existe ninguna ventana de tiempo en la que dos solicitudes simultáneas puedan tomar la misma habitación.

---

## 2. Diagrama de Competencia Simultánea entre Dos Usuarios

```mermaid
sequenceDiagram
    autonumber
    actor H1 as Viajero A (WhatsApp)
    actor H2 as Viajero B (WhatsApp o Recepción)
    participant API as Servidor Central (FastAPI)
    participant PG as Base de Datos (PostgreSQL 16)

    Note over H1,H2: Ambos viajeros consultan la Habitación 1 del 20 al 23 de diciembre
    H1->>API: Consulta disponibilidad (GET /api/rooms/availability)
    H2->>API: Consulta disponibilidad (GET /api/rooms/availability)
    API-->>H1: Habitación 1 disponible
    API-->>H2: Habitación 1 disponible

    rect rgb(232, 245, 233)
        Note over H1,PG: Viajero A selecciona la Habitación 1 un instante antes (t = 0s)
        H1->>API: Solicita bloqueo temporal (POST /api/bookings/lock)
        API->>PG: En una sola transacción:<br/>1) Marca como EXPIRADA los bloqueos vencidos de la habitación<br/>2) Inserta la reserva BLOQUEADA_TEMPORAL con expires_at = ahora + 15 min
        PG-->>API: Fila guardada (la restricción GiST no_overlapping_bookings no detecta cruce)
        API-->>H1: Habitación asegurada por 15 minutos (entrega lockToken)
    end

    rect rgb(255, 235, 238)
        Note over H2,PG: Viajero B intenta seleccionar la misma Habitación 1 (t = 1s)
        H2->>API: Solicita bloqueo temporal (POST /api/bookings/lock)
        API->>PG: Intenta insertar otra reserva BLOQUEADA_TEMPORAL en esas fechas
        PG-->>API: La restricción GiST rechaza la fila (rangos de fechas cruzados)
        API-->>H2: Respuesta HTTP 409 (Conflicto):<br/>la habitación ya tiene un bloqueo o reserva vigente
    end

    alt Escenario A: Viajero A completa sus datos y elige cómo pagar
        H1->>API: Confirma reserva con su lockToken (POST /api/bookings/confirm)
        API->>PG: La misma fila pasa a PENDIENTE_PAGO y se le quita el vencimiento
        PG-->>API: Reserva guardada con código TS-XXXX
        API-->>H1: Entrega el código y el enlace de pago de Wompi
        Note over H1,PG: Al llegar el pago aprobado (POST .../confirm-external-payment)<br/>la reserva pasa a CONFIRMADA con el 50% o el 100% abonado
    else Escenario B: Viajero A cancela, escribe "menú" o su sesión queda inactiva
        H1->>API: Cancela o reinicia sesión (POST /api/bookings/unlock)
        API->>PG: Marca el bloqueo como EXPIRADA
        API-->>H1: Confirma liberación inmediata de la habitación
        Note over H2,PG: La Habitación 1 vuelve a estar libre al instante para el Viajero B
    else Escenario C: Viajero A no hace nada durante 15 minutos
        Note over API,PG: Un proceso programado (cada 60 s) marca el bloqueo como EXPIRADA<br/>y la disponibilidad ya ignora los bloqueos vencidos
    end
```

---

## 3. Diagrama de los Dos Candados Sobre la Misma Restricción

```mermaid
flowchart LR
    classDef step fill:#FAF7F2,stroke:#5D4037,stroke-width:2px,color:#3E2723
    classDef lock1 fill:#FFF8E7,stroke:#F59E0B,stroke-width:2px,color:#3E2723
    classDef lock2 fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20
    classDef reject fill:#FFEBEE,stroke:#C62828,stroke-width:2px,color:#B71C1C

    Solicitud["Solicitud de Reserva<br/>Habitación + Fechas<br/>(checkIn a checkOut)"]:::step

    subgraph Candado1["PRIMER CANDADO: Bloqueo temporal (15 min)"]
        direction TB
        Insert1{"Restricción GiST<br/>no_overlapping_bookings<br/>¿hay una fila activa que se cruce?"}:::lock1
        Fila1["Fila BLOQUEADA_TEMPORAL<br/>con expires_at = ahora + 15 min"]:::lock1
    end

    subgraph Candado2["SEGUNDO CANDADO: Reserva firme"]
        direction TB
        Fila2["La misma fila pasa a PENDIENTE_PAGO<br/>(sin vencimiento)"]:::lock2
        Fila3["Pago aprobado:<br/>CONFIRMADA (50% o 100%)"]:::lock2
    end

    Rechazo1["Rechazo inmediato (HTTP 409)<br/>Otro cliente tiene esas fechas<br/>bloqueadas o reservadas"]:::reject

    Solicitud --> Insert1
    Insert1 -->|"Sí hay cruce"| Rechazo1
    Insert1 -->|"No hay cruce"| Fila1
    Fila1 -->|"Huésped entrega sus datos"| Fila2
    Fila2 -->|"Wompi aprueba el pago"| Fila3
    Fila1 -.->|"15 min sin avanzar, cancelar o menú"| Expira["Estado EXPIRADA<br/>la habitación se libera"]:::step
```

---

## 4. Ventajas de Este Diseño para Torre Satori

1. **Bloqueo por fechas y no por habitación completa:** Si el Viajero A está reservando la Habitación 1 para Navidad (24 al 26 de diciembre), solo esas fechas quedan retenidas; otro viajero puede reservar la misma habitación para la semana siguiente.
2. **Cero habitaciones retenidas cuando el usuario se arrepiente:** Además de la expiración automática de 15 minutos, cuando un usuario presiona *"Cancelar"* o vuelve al *"Menú"* en WhatsApp, el bloqueo se libera de inmediato.
3. **Una sola fuente de verdad:** Como el bloqueo y la reserva son filas de la misma tabla, no existe el riesgo de que un almacén de bloqueos y la base de datos queden desincronizados. Aunque una reserva ingrese por WhatsApp y otra desde recepción en el mismo milisegundo, PostgreSQL garantiza que jamás puedan guardarse dos reservas activas cruzadas.
4. **Reserva firme solo con pago aprobado:** Una reserva del chatbot no se confirma por una pantalla de éxito, sino únicamente cuando la pasarela aprueba la transacción; mientras tanto retiene la habitación como `PENDIENTE_PAGO`.
