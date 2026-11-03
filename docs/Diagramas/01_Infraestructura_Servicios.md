# 01. Arquitectura de Infraestructura y Servicios — SatoriPMS

## 1. Propósito del Diagrama

Este diagrama representa cómo están organizados y conectados los servicios tecnológicos de **SatoriPMS**. Permite observar qué elementos interactúan con los huéspedes y el personal del hotel en el exterior, y cómo los cuatro contenedores principales del sistema colaboran dentro de una red interna protegida para garantizar rapidez, seguridad y respaldo permanente de los datos de **Torre Satori**.

---

## 2. Diagrama General de Infraestructura

```mermaid
flowchart TB
    classDef external fill:#FAF7F2,stroke:#5D4037,stroke-width:2px,color:#3E2723
    classDef frontend fill:#FFF8E7,stroke:#D4A373,stroke-width:2px,color:#3E2723
    classDef core fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20
    classDef data fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#0D47A1
    classDef storage fill:#F3E5F5,stroke:#6A1B9A,stroke-width:1.5px,color:#4A148C

    subgraph Usuarios["Canales de Atención y Usuarios"]
        direction LR
        Huesped["Huésped / Viajero<br/>(Aplicación WhatsApp)"]:::external
        Personal["Recepcionista y Administrador<br/>(Navegador Web en Recepción)"]:::frontend
    end

    subgraph Externos["Plataformas Externas Conectadas"]
        direction LR
        MetaAPI["Plataforma Oficial de WhatsApp<br/>(Meta Cloud API)"]:::external
        GeminiAPI["Motor de Inteligencia Artificial<br/>(Google Gemini Flash Lite)"]:::external
        GoogleMaps["Ficha Pública del Hotel<br/>(Google Maps Reviews)"]:::external
    end

    subgraph FrontendApp["Interfaz Visual del Hotel"]
        WebApp["Aplicación Web SatoriPMS<br/>(React 18 + TypeScript + Vite)<br/>Puerto local: 5173"]:::frontend
    end

    subgraph DockerHost["Infraestructura en Contenedores Docker (docker-compose.yml)"]
        direction TB

        subgraph Orquestacion["Capa de Atención y Lógica Central"]
            direction LR
            N8N["Orquestador del Chatbot (satori-n8n)<br/>Flujo V8 (83 nodos)<br/>Puerto: 5678"]:::core
            API["Servidor Central (satori-api)<br/>Java 21 + Spring Boot 3.3<br/>Puerto: 8080"]:::core
        end

        subgraph Persistencia["Capa de Datos y Control de Concurrencia"]
            direction LR
            Redis["Memoria Rápida (satori-redis)<br/>Redis 7 · Sesiones y Bloqueos 15 min<br/>Puerto: 6379"]:::data
            Postgres["Base de Datos Principal (satori-postgres)<br/>PostgreSQL 16 + Migraciones Flyway<br/>Puerto local: 5433 -> 5432"]:::data
        end

        subgraph Volumenes["Almacenamiento Permanente en Disco"]
            direction LR
            VolN8N[("Volumen n8n<br/>n8n_data")]:::storage
            VolRedis[("Volumen Redis<br/>redis_data")]:::storage
            VolPG[("Volumen PostgreSQL<br/>postgres_data")]:::storage
        end
    end

    %% Relaciones de usuarios y servicios externos
    Huesped <-->|"Mensajes y menús interactivos"| MetaAPI
    Huesped -.->|"Publicación de reseña pública"| GoogleMaps
    MetaAPI <-->|"Recepción y envío de mensajes<br/>(/webhook/whatsapp-webhook)"| N8N
    N8N <-->|"Extracción de fechas y datos<br/>en lenguaje natural"| GeminiAPI

    %% Relaciones de la aplicación web
    Personal <-->|"Operación diaria y administración"| WebApp
    WebApp <-->|"Operaciones del hotel (REST)<br/>y alertas en vivo (/ws)"| API

    %% Relaciones internas entre contenedores
    N8N <-->|"Lectura y guardado de sesión<br/>(session:{waId})"| Redis
    N8N <-->|"Disponibilidad, bloqueos, reservas,<br/>pagos, cancelaciones y reseñas"| API
    API <-->|"Bloqueo atómico por intervalos (15 min)<br/>y liberación inmediata"| Redis
    API <-->|"Transacciones y restricción<br/>contra sobreventa"| Postgres

    %% Persistencia en volúmenes
    N8N --- VolN8N
    Redis --- VolRedis
    Postgres --- VolPG
```

---

## 3. Explicación de Componentes y Flujo de Comunicación

1. **Canal de Huéspedes (WhatsApp e Inteligencia Artificial):**
   - El viajero se comunica desde su teléfono con el número oficial de **Torre Satori**.
   - La plataforma de WhatsApp entrega el mensaje al **Orquestador del Chatbot** (`Contenedor de n8n : "satori-n8n"`), el cual recupera en milisegundos el paso actual de la conversación desde la **Memoria Rápida** (`Contenedor de Redis : "satori-redis"`).
   - Cuando el huésped escribe una solicitud en lenguaje libre, el orquestador se apoya en el motor **Google Gemini Flash Lite** para interpretar las fechas, la cantidad de personas y las preferencias.
2. **Canal de Recepción y Administración (Aplicación Web):**
   - El recepcionista y el administrador operan desde el navegador web conectándose directamente con el **Servidor Central** (`Contenedor del servidor : "satori-api"`).
   - A través de este canal se gestionan las 9 habitaciones de referencia (creación, edición y eliminación segura), los eventos especiales con descuentos, las llegadas y salidas de huéspedes, la tienda interna y los reportes contables.
3. **Aislamiento y Respaldo de Datos:**
   - Ni la base de datos (`Contenedor de PostgreSQL : "satori-postgres"`) ni la memoria rápida reciben conexiones directas desde internet; solo el servidor central y el orquestador interno pueden consultarlas.
   - Los tres volúmenes de almacenamiento (`"postgres_data"`, `"redis_data"` y `"n8n_data"`) garantizan que toda la información permanezca intacta aunque el servidor se reinicie.
