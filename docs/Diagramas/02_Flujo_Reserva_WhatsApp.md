# 02. Flujo de Reserva Automatizada por WhatsApp — SatoriPMS

## 1. Propósito del Diagrama

Este diagrama detalla paso a paso cómo un huésped realiza una reserva a través del asistente de WhatsApp de **Torre Satori** (tanto por la ruta guiada como mediante el asistente con inteligencia artificial), incluyendo la consulta de disponibilidad real, el bloqueo temporal de 15 minutos, la presentación del aviso de privacidad de datos personales, el desglose transparente de tarifa base y recargo por persona adicional, y las tres opciones de cierre: pago del 100%, anticipo del 50% o cancelación con liberación inmediata del bloqueo.

---

## 2. Diagrama de Secuencia del Proceso de Reserva

```mermaid
sequenceDiagram
    autonumber
    actor H as Huésped (WhatsApp)
    participant N as Orquestador Chatbot (n8n V8)
    participant IA as Inteligencia Artificial (Gemini)
    participant A as Servidor Central (Spring Boot API)
    participant R as Memoria Rápida (Redis 7)
    participant DB as Base de Datos (PostgreSQL 16)

    H->>N: Escribe "Hola" o "Menú"
    N->>R: Consulta o inicia sesión (session:{waId})
    N-->>H: Presenta Menú Principal (Opciones 1 a 6)

    alt Opción 1: Reserva Guiada Paso a Paso
        H->>N: Selecciona "1. Hacer una reserva"
        N-->>H: Solicita fecha de entrada y luego fecha de salida
        H->>N: Envía fechas de estadía (checkIn y checkOut)
        N->>A: Consulta habitaciones libres<br/>(GET /api/rooms/availability)
        A->>DB: Busca habitaciones activas sin cruce de fechas
        A->>R: Descarta habitaciones con bloqueo temporal activo
        A-->>N: Devuelve lista de habitaciones disponibles
        N-->>H: Muestra habitaciones con tarifa base y capacidad
        H->>N: Elige número de habitación(es)
    else Opción 2: Asistente con Inteligencia Artificial
        H->>N: Selecciona "2. Asistente IA"
        N-->>H: Da bienvenida e informa Aviso de Privacidad (Ley 1581)
        H->>N: Describe en un solo mensaje fechas, personas, mascota y datos
        N->>IA: Solicita extraer datos estructurados del texto
        IA-->>N: Devuelve fechas, adultos, niños, mascota, nombre y cédula
        N->>A: Consulta disponibilidad filtrada por capacidad y mascota<br/>(GET /api/rooms/availability)
        A->>DB: Verifica reservas activas y capacidad
        A->>R: Verifica ausencia de bloqueos temporales
        A-->>N: Devuelve habitaciones compatibles
        N-->>H: Muestra opciones disponibles para elegir
        H->>N: Responde con el número de la habitación deseada
    end

    rect rgb(255, 248, 231)
        Note over N,R: Bloqueo Temporal Garantizado por 15 Minutos (900 segundos)
        N->>A: Solicita bloquear la habitación elegida<br/>(POST /api/bookings/lock)
        A->>R: Ejecuta script atómico por intervalo de fechas<br/>(lock:room:{roomId}:intervals + metadata TTL 900s)
        R-->>A: Confirma bloqueo y entrega código (lockToken)
        A-->>N: Devuelve lockToken y vigencia (900s)
    end

    opt Solo en Reserva Guiada: Captura de Huéspedes y Datos Personales
        N-->>H: Confirma bloqueo por 15 min y pregunta adultos y niños
        H->>N: Indica cantidad de adultos y niños
        N-->>H: Presenta Aviso de Privacidad (Ley 1581 de 2012)<br/>y solicita nombre completo del titular
        H->>N: Envía nombre completo, luego documento, mascota y acompañantes
    end

    N-->>H: Muestra Resumen Completo de Reserva:<br/>• Tarifa base por noches<br/>• Recargo por persona adicional (si supera capacidad base)<br/>• Total estadía<br/>Opciones: 1) Pagar 100%  2) Anticipo 50%  3) Cancelar

    alt Elige Opción 1 (Pago 100%) u Opción 2 (Anticipo 50%)
        H->>N: Selecciona modalidad de pago (1 = 100% / 2 = 50%)
        N->>A: Solicita confirmar reserva en firme<br/>(POST /api/bookings/confirm)
        A->>R: Verifica que el lockToken siga vigente
        A->>DB: Guarda huésped y reserva agrupada (reservationGroupId)<br/>status = 'confirmed', payment_status = 'paid' o 'partial'
        A->>R: Elimina de inmediato el bloqueo temporal
        A-->>N: Devuelve código de reserva (8 caracteres), total, abonado y saldo
        N->>R: Reinicia sesión de usuario a estado de menú
        N-->>H: Envía confirmación exitosa con código único y desglose de pago
    else Elige Opción 3 (Cancelar) o Reinicia con "Menú"
        H->>N: Selecciona "3. Cancelar" o escribe "menú"
        N->>R: Limpia borrador de sesión del usuario
        N->>A: Solicita liberar el bloqueo de inmediato<br/>(POST /api/bookings/unlock)
        A->>R: Elimina intervalo y metadatos del bloqueo
        N-->>H: Confirma cancelación y liberación inmediata de la habitación
    end
```

---

## 3. Aspectos Clave del Flujo

1. **Dos caminos complementarios hacia la misma reserva:** Tanto el viajero que prefiere ser guiado pregunta por pregunta como el que prefiere redactar un solo mensaje en lenguaje natural convergen en las mismas reglas de validación del servidor central.
2. **Transparencia en el cobro de personas adicionales:** Antes de que el huésped elija cómo pagar, el resumen discrimina siempre la tarifa base de las noches y el valor adicional cuando el grupo supera la capacidad base de la habitación.
3. **Liberación inmediata ante desistimiento:** Si el viajero decide cancelar en el paso de pago o escribe *"menú"* para empezar de nuevo, el flujo invoca de inmediato la liberación del candado en memoria (`Liberar bloqueo : "POST /api/bookings/unlock"`), evitando que la habitación quede retenida innecesariamente.
