# SatoriPMS

**Sistema de gestión hotelera (PMS) para Torre Satori — Sevilla, Valle del Cauca**
Proyecto Integrador II · 8vo Semestre · Equipo de 3

## Inicio rápido

Antes de arrancar necesitas:
- Docker + Docker Compose
- Node.js 20+
- Java 21
- Copiar [.env.example](.env.example) a `.env` y completar los valores reales

Comandos básicos en orden:

```bash
git clone https://github.com/JuanJarias/SatoriPMS.git
cd SatoriPMS
cp .env.example .env
# editar .env con tus datos

docker compose -f docker-compose.yml -f docker-compose.tunnel.yml up -d
# o, si no necesitas ngrok:
# docker compose up -d

cd apps/web
npm install
npm run dev
```

Esto levanta la infraestructura del proyecto (Postgres, Redis, n8n y API) y luego arranca el frontend en `http://localhost:5173`.

### Opción simplificada con script

Desde la raíz del proyecto:

```bash
chmod +x start-dev.sh
./start-dev.sh
```

El script crea `.env` si todavía no existe, pregunta si necesitas ngrok, levanta Docker, instala las dependencias y arranca el frontend.

---

## Progreso del proyecto

### Sprint actual: Sprint 1 (14 Sep – 25 Sep 2026)

| Sprint | Épica | Progreso |
|:-------|:------|:---------|
| Sprint 1 — Arquitectura y BD | Transversal | [![Sprint 1](https://img.shields.io/github/milestones/issues-open/JuanJarias/SatoriPMS/6?label=open&color=orange)](https://github.com/JuanJarias/SatoriPMS/milestone/6) |
| Sprint 2 — WhatsApp y Reservas | Épica 1 | [![Epic 1](https://img.shields.io/github/milestones/progress-percent/JuanJarias/SatoriPMS/6?label=Épica%201)](https://github.com/JuanJarias/SatoriPMS/milestone/6) |
| Sprint 3 — Panel Web y Finanzas | Épicas 2 y 3 | [![Epic 2](https://img.shields.io/github/milestones/progress-percent/JuanJarias/SatoriPMS/1?label=Épica%202)](https://github.com/JuanJarias/SatoriPMS/milestone/1) |
| Sprint 4 — Tienda y Roles | Épicas 4, 5 y 6 | [![Epic 4](https://img.shields.io/github/milestones/progress-percent/JuanJarias/SatoriPMS/3?label=Épica%204)](https://github.com/JuanJarias/SatoriPMS/milestone/3) |
| Sprint 5 — QA y Despliegue | Transversal | [![Issues](https://img.shields.io/github/issues/JuanJarias/SatoriPMS?label=issues%20abiertos)](https://github.com/JuanJarias/SatoriPMS/issues) |


## Arquitectura

```
WhatsApp (Huésped)
    ↓
n8n (Orquestación de conversación)
    ↓
Backend API (Spring Boot)            ←──── App Web React (Recepcionista / Admin)
    ↓                                            ↑
PostgreSQL 16 + Redis 7             WebSocket Gateway (tiempo real)
```

> **Nota:** el framework de backend se define formalmente en [ADR-001](docs/adr/ADR-001-stack.md) (TASK-03). Este README asume Spring Boot según el trabajo ya avanzado; si el equipo confirma otra decisión, actualizar esta sección y la tabla de infraestructura.

---

## Infraestructura

Todos los servicios corren en contenedores Docker, definidos en `docker-compose.yml`. Ningún puerto de base de datos ni de caché queda expuesto públicamente — solo accesibles desde `localhost`/la propia red de Docker.

| Servicio | Contenedor | Puerto interno | Expuesto en host | Rol |
|:---------|:-----------|:---------------:|:------------------|:----|
| PostgreSQL 16 | `satori_postgres` | 5432 | `127.0.0.1:5432` (solo local) | Fuente de verdad. Restricción `EXCLUDE USING gist` contra doble reserva. |
| Redis 7 | `satori_redis` | 6379 | `127.0.0.1:6379` (solo local) | Bloqueo temporal de habitación (TTL 15 min, RN-02) y estado de conversación (`chat:<wa_id>`). |
| n8n | `satori_n8n` | 5678 | `5678` | Orquestación del chatbot de WhatsApp. Nunca calcula precios ni aplica reglas de negocio. |
| Backend API | `satori_api` *(pendiente, TASK-07)* | 8080 | 8080 | Dueño único de RN-01, RN-02, RN-03 y del cálculo de tarifas. Emite eventos WebSocket. |
| App Web | — *(fuera de Docker en dev)* | 5173 (Vite) | 5173 | Panel de recepcionista/administrador. Se conecta al backend vía REST + WebSocket. |
| ngrok *(solo desarrollo)* | `satori_ngrok` | — | — | Expone `n8n:5678` a internet con dominio fijo, para que Meta pueda llegar al webhook. |

**Variables de host/dominio** :

| Variable | Dónde se usa | Ejemplo en desarrollo |
|:---------|:--------------|:------------------------|
| `N8N_HOST` | n8n, para construir sus URLs | `tu-dominio.ngrok-free.app` |
| `N8N_WEBHOOK_URL` | n8n, base de los webhooks | `https://tu-dominio.ngrok-free.app/` |
| `NGROK_DOMAIN` | servicio `ngrok` | `tu-dominio.ngrok-free.app` |



---

## Por qué hay `docker-compose.yml` y `docker-compose.tunnel.yml`

- **`docker-compose.yml`** contiene únicamente la infraestructura real del proyecto (Postgres, Redis, n8n, y luego el backend). Es el archivo que algún día correrá tal cual en el servidor de producción.
- **`docker-compose.tunnel.yml`** añade solo el servicio de `ngrok`, necesario mientras el proyecto se desarrolla en máquinas locales sin IP pública, para que WhatsApp/Meta pueda alcanzar el webhook de n8n.

Se mantienen separados a propósito: cuando el proyecto pase a un servidor con dominio propio, `docker-compose.tunnel.yml` deja de usarse sin tocar ni un solo servicio de producción.

```bash
# Desarrollo local (con túnel de ngrok)
docker compose -f docker-compose.yml -f docker-compose.tunnel.yml up -d

# Producción (sin túnel, solo infraestructura real)
docker compose up -d
```

---

## Estructura del repositorio

```
SatoriPMS/
├── apps/
│   ├── web/            # React + Vite (frontend)
│   └── api/            # Backend (Spring Boot)
├── flows/
│   └── n8n/            # Workflows de n8n exportados en JSON
├── db/
│   └── migrations/     # Migraciones SQL versionadas
├── docs/
│   ├── adr/            # Architecture Decision Records
│   └── manuales/       # Entregables finales
├── docker-compose.yml         # Infraestructura real (Postgres, Redis, n8n, API)
├── docker-compose.tunnel.yml  # Túnel ngrok, solo desarrollo local
├── .env.example                # Plantilla de variables de entorno
└── .github/
    ├── ISSUE_TEMPLATE/ # Plantillas de issue
    ├── workflows/      # GitHub Actions (CI, progress tracker)
    └── CODEOWNERS
```

---

## Equipo

| Miembro | GitHub |
|:--------|:-------|
| Juan Arias | [@JuanJarias](https://github.com/JuanJarias) |
| Gafo | [@Gafoxx](https://github.com/Gafoxx) |
| Esteban | [@Esteban-GV](https://github.com/Esteban-GV) |

---

## Levantar el proyecto localmente

```bash
# Requisitos: Docker, Docker Compose, Node.js ≥ 20, Java 21

# 1. Clonar el repo
git clone https://github.com/JuanJarias/SatoriPMS.git
cd SatoriPMS

# 2. Copiar variables de entorno y completarlas con valores reales
cp .env.example .env

# 3. Levantar infraestructura (con túnel de ngrok, para pruebas de WhatsApp)
docker compose -f docker-compose.yml -f docker-compose.tunnel.yml up -d

# 4. Flyway valida y aplica las migraciones automáticamente al arrancar el API

# 5. Frontend
cd apps/web && npm install && npm run dev
```
