# 03. Prevención de Sobreventa: Arquitectura de Doble Candado — SatoriPMS

## 1. Propósito del Diagrama

Uno de los riesgos más críticos para cualquier hotel es la **sobreventa**: que dos clientes distintos intenten reservar la última habitación disponible para las mismas fechas al mismo tiempo.

Este documento explica visualmente cómo **SatoriPMS** elimina ese riesgo mediante un **sistema de Doble Candado**:
1. **Primer Candado (En memoria rápida Redis por 15 minutos):** Protege la habitación desde el segundo exacto en que el primer viajero la selecciona, evaluando intervalos de fechas de manera atómica.
2. **Segundo Candado (En la base de datos PostgreSQL de forma permanente):** Impide matemáticamente guardar dos reservas activas con fechas cruzadas para una misma habitación.

---

## 2. Diagrama de Competencia Simultánea entre Dos Usuarios

```mermaid
sequenceDiagram
    autonumber
    actor H1 as Viajero A (WhatsApp)
    actor H2 as Viajero B (WhatsApp o Recepción)
    participant API as Servidor Central (Spring Boot)
    participant Redis as Primer Candado: Memoria Rápida (Redis 7)
    participant PG as Segundo Candado: Base de Datos (PostgreSQL 16)

    Note over H1,H2: Ambos viajeros consultan la Habitación 101 del 20 al 23 de diciembre
    H1->>API: Consulta disponibilidad (GET /api/rooms/availability)
    H2->>API: Consulta disponibilidad (GET /api/rooms/availability)
    API-->>H1: Habitación 101 disponible
    API-->>H2: Habitación 101 disponible

    rect rgb(232, 245, 233)
        Note over H1,Redis: Viajero A selecciona la Habitación 101 un instante antes (t = 0s)
        H1->>API: Solicita bloqueo temporal (POST /api/bookings/lock)
        API->>Redis: Ejecuta script atómico Lua:<br/>1) Limpia tokens vencidos en lock:room:1:intervals<br/>2) Verifica que ningún intervalo activo se cruce con [20 dic, 23 dic)<br/>3) Registra token en lock:room:1:intervals y lock:room:1:metadata:{token} (TTL 900s)
        Redis-->>API: Bloqueo concedido (Resultado = 1)
        API-->>H1: Habitación asegurada por 15 minutos (entrega lockToken)
    end

    rect rgb(255, 235, 238)
        Note over H2,Redis: Viajero B intenta seleccionar la misma Habitación 101 (t = 1s)
        H2->>API: Solicita bloqueo temporal (POST /api/bookings/lock)
        API->>Redis: Ejecuta script atómico Lua sobre lock:room:1:intervals
        Redis-->>API: Detecta solapamiento con el intervalo activo del Viajero A (Resultado = 0)
        API-->>H2: Respuesta HTTP 409 (Conflicto):<br/>"La habitación ya tiene un bloqueo temporal activo"
    end

    alt Escenario A: Viajero A completa sus datos y confirma el pago (50% o 100%)
        H1->>API: Confirma reserva con su lockToken (POST /api/bookings/confirm)
        API->>Redis: Verifica que lock:room:1:metadata:{token} siga vigente
        API->>PG: Inserta reserva con status = 'confirmed'<br/>Valida restricción GiST no_overlapping_bookings
        PG-->>API: Reserva guardada con éxito
        API->>Redis: Libera bloqueo temporal (borra metadata y zrem de intervals)
        API-->>H1: Entrega código único de reserva confirmada
    else Escenario B: Viajero A cancela, escribe "menú" o su sesión queda inactiva
        H1->>API: Cancela o reinicia sesión (POST /api/bookings/unlock)
        API->>Redis: Elimina de inmediato lock:room:1:metadata:{token} y el registro en intervals
        API-->>H1: Confirma liberación inmediata de la habitación
        Note over H2,Redis: La Habitación 101 vuelve a estar libre al instante para el Viajero B
    end
```

---

## 3. Diagrama de las Dos Capas de Protección por Intervalos de Fechas

```mermaid
flowchart LR
    classDef step fill:#FAF7F2,stroke:#5D4037,stroke-width:2px,color:#3E2723
    classDef lock1 fill:#FFF8E7,stroke:#F59E0B,stroke-width:2px,color:#3E2723
    classDef lock2 fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20
    classDef reject fill:#FFEBEE,stroke:#C62828,stroke-width:2px,color:#B71C1C

    Solicitud["Solicitud de Reserva<br/>Habitación + Fechas<br/>(checkIn a checkOut)"]:::step

    subgraph Candado1["PRIMER CANDADO: Memoria Rápida (Redis 7)"]
        direction TB
        LuaCheck{"¿Existe intervalo cruzado en<br/>lock:room:{id}:intervals?"}:::lock1
        HashTTL["Guarda rango [checkIn, checkOut)<br/>en lock:room:{id}:metadata:{token}<br/>Vigencia máxima: 900s (15 min)"]:::lock1
    end

    subgraph Candado2["SEGUNDO CANDADO: Base de Datos (PostgreSQL 16)"]
        direction TB
        GistCheck{"Restricción GiST:<br/>no_overlapping_bookings<br/>status IN ('pending_payment','confirmed')"}:::lock2
        Persist["Reserva Confirmada en Firme<br/>y Liberación del Candado 1"]:::lock2
    end

    Rechazo1["Rechazo Inmediato (HTTP 409)<br/>Otro cliente está reservando<br/>esas fechas en este momento"]:::reject
    Rechazo2["Rechazo Transaccional<br/>Ya existe una reserva firme<br/>en ese rango de días"]:::reject

    Solicitud --> LuaCheck
    LuaCheck -->|"Sí hay cruce"| Rechazo1
    LuaCheck -->|"No hay cruce"| HashTTL
    HashTTL -->|"Huésped confirma pago"| GistCheck
    GistCheck -->|"Sí hay cruce"| Rechazo2
    GistCheck -->|"No hay cruce"| Persist
```

---

## 4. Ventajas de Este Diseño para Torre Satori

1. **Bloqueo inteligente por fechas y no por habitación completa:** Si el Viajero A está reservando la Habitación 101 para Navidad (24 al 26 de diciembre), el Primer Candado solo bloquea esas fechas específicas. Si al mismo tiempo el Viajero B desea la misma Habitación 101 para Año Nuevo (30 de diciembre al 2 de enero), el sistema le permite reservar sin ningún obstáculo.
2. **Cero habitaciones retenidas cuando el usuario se arrepiente:** Además de la expiración automática de 15 minutos, cuando un usuario presiona *"Cancelar"* o regresa al *"Menú"* en WhatsApp, el sistema libera el Primer Candado de inmediato (`Liberación inmediata : "POST /api/bookings/unlock"`).
3. **Respaldo definitivo en base de datos:** Aunque una reserva ingrese por WhatsApp y otra desde el computador de recepción en el mismo milisegundo, el Segundo Candado en PostgreSQL garantiza que jamás puedan guardarse dos reservas activas superpuestas.
