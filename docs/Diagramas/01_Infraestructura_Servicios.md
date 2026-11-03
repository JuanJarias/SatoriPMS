# Diagrama 01 — Arquitectura de Infraestructura y Servicios

Este diagrama detalla la topología de contenedores de **Docker Compose**, asignación de puertos, redes aisladas, volúmenes de persistencia y la interacción con los servicios en la nube (Meta WhatsApp Cloud API, Google Gemini AI Studio, Cloudflare y MercadoPago).

---

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#E8EEF5', 'primaryTextColor': '#1B365D', 'primaryBorderColor': '#2C4D75', 'lineColor': '#2C4D75', 'secondaryColor': '#F0FDF4', 'tertiaryColor': '#FFFBEB' }}}%%
flowchart TD
    subgraph Internet["🌐 Capa Externa e Internet"]
        UserWA["📱 Huéspedes<br/>(WhatsApp Móvil)"]
        UserWeb["💻 Recepción / Admin<br/>(Navegador Web)"]
        MetaAPI["☁️ Meta Cloud API<br/>(WhatsApp Business)"]
        GeminiAPI["🤖 Google Gemini API<br/>(Flash Lite LLM)"]
        MPPasarela["💳 MercadoPago<br/>(Pasarela Sandbox)"]
    end

    subgraph Host["🖥️ Servidor Host (Linux / Docker Environment)"]
        subgraph Proxy["Perímetro y Seguridad"]
            CFTunnel["🛡️ Cloudflare Tunnel / SSL<br/>(Terminación HTTPS :443)"]
        end

        subgraph DockerNet["Red Privada Docker (satori-network)"]
            subgraph FrontService["Frontend SPA"]
                WebReact["⚛️ App Web Satori<br/>React 18 + Vite<br/>Puerto Host: :5173"]
            end

            subgraph CoreService["Backend Core"]
                API["☕ Spring Boot 3.3 API<br/>Java 21 · Arquitectura Hexagonal<br/>Puerto Host: :8080"]
            end

            subgraph AutomationService["Orquestación Conversacional"]
                N8N["⚡ n8n Workflow Engine<br/>Flujo V8_ChatbotReservas<br/>Puerto Host: :5678"]
            end

            subgraph DataService["Capa de Datos y Almacenamiento"]
                Postgres[("🐘 PostgreSQL 16<br/>Extensión btree_gist<br/>Puerto Host: :5432")]
                Redis[("🔴 Redis 7 Alpine<br/>Scripts Lua + TTL<br/>Puerto Host: :6379")]
            end
        end

        subgraph StorageVolumes["💾 Volúmenes de Persistencia en Disco"]
            VolPG[("postgres_data<br/>(Datos relacionales)")]
            VolRedis[("redis_data<br/>(Caché y dump.rdb)")]
            VolN8N[("n8n_data<br/>(Workflows y credenciales)")]
        end
    end

    %% Relaciones externas
    UserWA <-->|"Mensajería cifrada"| MetaAPI
    MetaAPI <-->|"Webhook HTTP / POST"| CFTunnel
    CFTunnel -->|"Proxy inverso local"| N8N
    UserWeb <-->|"HTTPS :443"| CFTunnel
    CFTunnel -->|"Servicio estático"| WebReact

    %% Relaciones frontend - backend
    WebReact <-->|"REST API (JSON) + JWT"| API
    WebReact <-->|"WebSockets STOMP<br/>(Sincronización en vivo)"| API

    %% Relaciones n8n
    N8N <-->|"Prompts / JSON Extraction"| GeminiAPI
    N8N -->|"Consultas y reservas REST"| API
    N8N <-->|"Sesiones y locks temporales"| Redis

    %% Relaciones backend
    API <-->|"Bloqueos atómicos (Lua scripts)"| Redis
    API <-->|"Persistencia transaccional ACID"| Postgres
    API <-->|"Webhooks de pago / Notificaciones"| MPPasarela

    %% Volúmenes
    Postgres --- VolPG
    Redis --- VolRedis
    N8N --- VolN8N

    classDef external fill:#EFF6FF,stroke:#2563EB,stroke-width:1.5px,color:#1E3A8A;
    classDef proxy fill:#F5F3FF,stroke:#7C3AED,stroke-width:1.5px,color:#4C1D95;
    classDef front fill:#ECFDF5,stroke:#059669,stroke-width:1.5px,color:#064E3B;
    classDef core fill:#FEF2F2,stroke:#DC2626,stroke-width:1.5px,color:#7F1D1D;
    classDef auto fill:#FFFBEB,stroke:#D97706,stroke-width:1.5px,color:#78350F;
    classDef data fill:#F0FDF4,stroke:#16A34A,stroke-width:1.5px,color:#14532D;
    classDef storage fill:#F1F5F9,stroke:#64748B,stroke-width:1px,stroke-dasharray: 4 4,color:#334155;

    class UserWA,UserWeb,MetaAPI,GeminiAPI,MPPasarela external;
    class CFTunnel proxy;
    class WebReact front;
    class API core;
    class N8N auto;
    class Postgres,Redis data;
    class VolPG,VolRedis,VolN8N storage;
```

---

### Componentes y Matriz de Puertos

| Servicio | Imagen Docker | Puerto Contenedor | Puerto Host | Red Docker | Propósito Técnico |
|---|---|:---:|:---:|---|---|
| **Spring Boot API** | `eclipse-temurin:21-jre-alpine` | `8080` | `8080` | `satori-network` | Servidor de aplicaciones backend, endpoints REST, seguridad Spring Security y sockets. |
| **App Web (React)** | `node:20-alpine` (Vite dev) | `5173` | `5173` | `satori-network` | Panel administrativo de recepción para check-in, check-out y visualización de ocupación. |
| **n8n Workflow** | `n8nio/n8n:latest` | `5678` | `5678` | `satori-network` | Orquestador de flujos conversacionales, integración con Meta API y Gemini. |
| **PostgreSQL** | `postgres:16-alpine` | `5432` | `5432` | `satori-network` | Base de datos relacional principal con extensión `btree_gist` para exclusión física. |
| **Redis** | `redis:7-alpine` | `6379` | `6379` | `satori-network` | Almacenamiento en memoria para candados distribuidos (TTL 15 min) y estados de sesión. |
