# SatoriPMS 🏨

**Sistema de gestión hotelera (PMS) para Torre Satori — Sevilla, Valle del Cauca**  
Proyecto Integrador II · 8vo Semestre · Equipo de 3

---

## 📊 Progreso del proyecto

### Sprint actual: Sprint 1 (14 Sep – 25 Sep 2026)

| Sprint | Épica | Progreso |
|:-------|:------|:---------|
| Sprint 1 — Arquitectura y BD | Transversal | [![Sprint 1](https://img.shields.io/github/milestones/issues-open/JuanJarias/SatoriPMS/6?label=open&color=orange)](https://github.com/JuanJarias/SatoriPMS/milestone/6) |
| Sprint 2 — WhatsApp y Reservas | Épica 1 | [![Epic 1](https://img.shields.io/github/milestones/progress-percent/JuanJarias/SatoriPMS/6?label=Épica%201)](https://github.com/JuanJarias/SatoriPMS/milestone/6) |
| Sprint 3 — Panel Web y Finanzas | Épicas 2 y 3 | [![Epic 2](https://img.shields.io/github/milestones/progress-percent/JuanJarias/SatoriPMS/1?label=Épica%202)](https://github.com/JuanJarias/SatoriPMS/milestone/1) |
| Sprint 4 — Tienda y Roles | Épicas 4, 5 y 6 | [![Epic 4](https://img.shields.io/github/milestones/progress-percent/JuanJarias/SatoriPMS/3?label=Épica%204)](https://github.com/JuanJarias/SatoriPMS/milestone/3) |
| Sprint 5 — QA y Despliegue | Transversal | [![Issues](https://img.shields.io/github/issues/JuanJarias/SatoriPMS?label=issues%20abiertos)](https://github.com/JuanJarias/SatoriPMS/issues) |

### Estado general

![Open Issues](https://img.shields.io/github/issues/JuanJarias/SatoriPMS?label=issues%20abiertos&color=blue)
![Closed Issues](https://img.shields.io/github/issues-closed/JuanJarias/SatoriPMS?label=completados&color=green)
![CI](https://img.shields.io/github/actions/workflow/status/JuanJarias/SatoriPMS/ci.yml?label=CI&branch=main)

---

## 🏗 Arquitectura

```
WhatsApp (Huésped)
    ↓
n8n (Orquestación de conversación)
    ↓
Backend API (Spring Boot / NestJS)   ←──── App Web React (Recepcionista / Admin)
    ↓                                            ↑
PostgreSQL 16 + Redis 7             WebSocket Gateway (tiempo real)
```

**Stack:**
- **App web**: React + Vite + TypeScript + Tailwind + TanStack Query
- **Canal huésped**: WhatsApp Cloud API (Meta)
- **Orquestación chatbot**: n8n autoalojado en Docker
- **Backend**: Spring Boot o NestJS (ver [ADR-001](docs/adr/ADR-001-stack.md))
- **Base de datos**: PostgreSQL 16 (restricción de exclusión anti doble-reserva)
- **Caché / bloqueos**: Redis 7 (TTL de 15 min para RN-02)
- **Pagos**: MercadoPago
- **Despliegue**: Docker Compose; frontend en Vercel, API en Railway/Render

---

## 📁 Estructura del repositorio

```
SatoriPMS/
├── apps/
│   ├── web/            # React + Vite (frontend)
│   └── api/            # Backend (Spring Boot o NestJS)
├── flows/
│   └── n8n/            # Workflows de n8n exportados en JSON
├── db/
│   └── migrations/     # Migraciones SQL versionadas
├── docs/
│   ├── adr/            # Architecture Decision Records
│   └── manuales/       # Entregables finales
└── .github/
    ├── ISSUE_TEMPLATE/ # Plantillas de issue
    ├── workflows/      # GitHub Actions (CI, progress tracker)
    └── CODEOWNERS
```

---

## 👥 Equipo

| Miembro | GitHub |
|:--------|:-------|
| Juan Arias | [@JuanJarias](https://github.com/JuanJarias) |
| Gafo | [@Gafoxx](https://github.com/Gafoxx) |
| Esteban | [@Esteban-GV](https://github.com/Esteban-GV) |

---

## 🚀 Levantar el proyecto localmente

```bash
# Requisitos: Docker, Docker Compose, Node.js ≥ 20, Java 21 (si Spring Boot)

# 1. Clonar el repo
git clone https://github.com/JuanJarias/SatoriPMS.git
cd SatoriPMS

# 2. Copiar variables de entorno
cp .env.example .env
# Completar las variables en .env

# 3. Levantar servicios
docker compose up -d

# 4. Correr migraciones
docker compose exec api npm run migrate   # NestJS
# o
docker compose exec api ./gradlew flywayMigrate  # Spring Boot

# 5. Frontend
cd apps/web && npm install && npm run dev
```

---

## 📋 Convenciones

### Ramas
- `feature/<ID>-<slug>` — ej: `feature/CU-01-reservar-habitacion`
- `fix/<ID>-<slug>` — ej: `fix/BUG-07-bloqueo-no-expira`

### Commits (Conventional Commits)
```
feat(reservas): bloqueo temporal de 15 min (#23)
fix(chatbot): manejo de timeout en pago (#33)
docs(adr): registrar decisión NestJS (#15)
```

### Pull Requests
- Título del issue + `Closes #N`
- Requiere: PR aprobado por 1 miembro + CI en verde
- **Nadie hace push directo a `main`**, ni el dueño del repo

---

## 📚 Documentación

- [ADR-001: Stack tecnológico](docs/adr/ADR-001-stack.md)
- [ADR-002: Estructura de módulos](docs/adr/ADR-002-estructura-modulos.md)
- [Plan de sprints y backlog](https://github.com/JuanJarias/SatoriPMS/issues)
- [GitHub Project — Tablero del equipo](https://github.com/users/JuanJarias/projects/2)
