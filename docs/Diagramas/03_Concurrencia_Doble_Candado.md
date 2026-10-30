# Diagrama 03 — Concurrencia y Mecanismo de Doble Candado Anti-Overbooking

Este diagrama ilustra la arquitectura de **Doble Candado** implementada en Torre Satori PMS para garantizar la prevención absoluta de sobreventa (*overbooking*), protegiendo la consistencia tanto en memoria de baja latencia como a nivel de bloque en disco.

---

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8EEF5', 'primaryTextColor': '#1B365D', 'primaryBorderColor': '#2C4D75', 'lineColor': '#2C4D75' }}}%%
flowchart TD
    subgraph CanalesEntrada["Canales Concurrentes de Venta"]
        WA["📱 Huésped A<br/>WhatsApp Bot"]
        WebRec["💻 Recepcionista B<br/>App Web / Reserva Manual"]
    end

    subgraph CapaAPI["Backend API — Spring Boot 3.3"]
        BookingCtrl["BookingController<br/>POST /api/bookings/lock"]
        LockService["RedisLockService<br/>(Adquisición de Candado Atómico)"]
    end

    subgraph Nivel1["NIVEL 1: Candado en Memoria (Baja Latencia)"]
        RedisMem[("🔴 Redis 7 Alpine<br/>EVAL script Lua atómico<br/>SET room:ID:lock token NX EX 900")]
        DecisionLock{"¿Candado<br/>adquirido?<br/>(Retorna 1)"}
    end

    subgraph Nivel2["NIVEL 2: Candado Físico Relacional (Garantía ACID)"]
        DBEngine[("🐘 PostgreSQL 16 Motor<br/>Extensión btree_gist<br/>EXCLUDE USING gist")]
        ConstraintRule["Restricción Excluyente:<br/>room_id WITH = AND<br/>daterange(check_in, check_out, '[)') WITH &&<br/>WHERE status IN ('CONFIRMED', 'CHECKED_IN')"]
        DecisionDB{"¿Conflicto<br/>en disco?"}
    end

    subgraph Respuestas["Respuestas al Cliente"]
        Success["✅ HTTP 200 / 201<br/>Bloqueo temporal 15 min /<br/>Reserva Confirmada"]
        Conflict["🚫 HTTP 409 Conflict<br/>Habitación no disponible /<br/>En proceso de pago por otro huésped"]
    end

    %% Flujo concurrente
    WA -->|"1. Intento bloqueo t = 0 ms"| BookingCtrl
    WebRec -->|"1. Intento bloqueo t = 1 ms"| BookingCtrl
    BookingCtrl --> LockService
    LockService --> RedisMem
    RedisMem --> DecisionLock

    %% Decisiones Nivel 1
    DecisionLock -->|"SÍ (Primer solicitante)"| Success
    DecisionLock -->|"NO (Habitación ya bloqueada)"| Conflict

    %% Transición a Nivel 2
    Success -->|"2. Pago completado<br/>POST /api/bookings/batch"| DBEngine
    DBEngine --- ConstraintRule
    ConstraintRule --> DecisionDB

    %% Decisiones Nivel 2
    DecisionDB -->|"NO (Sin solapamiento)"| CommitDB["💾 Transacción COMMIT<br/>Status: CONFIRMED<br/>Liberación de llave en Redis"]
    DecisionDB -->|"SÍ (Violación de exclusión)"| RollbackDB["💥 Error 23P01 exclusion_violation<br/>Transacción ROLLBACK<br/>Cero datos corruptos"]

    classDef channels fill:#EFF6FF,stroke:#2563EB,stroke-width:1.5px,color:#1E3A8A;
    classDef api fill:#FEF2F2,stroke:#DC2626,stroke-width:1.5px,color:#7F1D1D;
    classDef n1 fill:#FFFBEB,stroke:#D97706,stroke-width:1.5px,color:#78350F;
    classDef n2 fill:#F0FDF4,stroke:#16A34A,stroke-width:1.5px,color:#14532D;
    classDef respOk fill:#ECFDF5,stroke:#059669,stroke-width:1.5px,color:#064E3B;
    classDef respErr fill:#FFF1F2,stroke:#E11D48,stroke-width:1.5px,color:#881337;

    class WA,WebRec channels;
    class BookingCtrl,LockService api;
    class RedisMem,DecisionLock n1;
    class DBEngine,ConstraintRule,DecisionDB,CommitDB,RollbackDB n2;
    class Success respOk;
    class Conflict respErr;
```

---

### Explicación de los Dos Niveles de Blindaje

1. **Nivel 1 (Redis 7 — Preventivo):** Opera en memoria volátil en $< 5\text{ ms}$. Si dos clientes solicitan la misma habitación para las mismas fechas, el comando atómico `SET ... NX EX 900` entrega el candado al primero y rechaza al segundo de inmediato con un código de conflicto `409 Conflict`, evitando saturar la base de datos con peticiones redundantes.
2. **Nivel 2 (PostgreSQL 16 — Estructural):** La restricción `EXCLUDE USING gist` opera en el motor relacional. Incluso si la capa de Redis se cayera, se reiniciara o la red sufriera particiones extremas, el motor físico de base de datos aborta con excepción `23P01 exclusion_violation` cualquier intento de insertar dos reservas activas con fechas solapadas para la misma habitación.
