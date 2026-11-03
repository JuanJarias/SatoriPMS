# Estado Actual del Proyecto — Torre Satori PMS

Documento maestro de seguimiento técnico, estado general de componentes y documentos, registro cronológico de cambios y registro de decisiones arquitectónicas del proyecto **Torre Satori PMS**, estructurado conforme a las secciones 4, 8 y 12.B de [`GEMINI.md`](file:///home/guarinve/Documentos/SatoriPMS/GEMINI.md).

---

## 1. Resumen Ejecutivo del Estado Actual

**Torre Satori PMS** es un sistema de gestión hotelera (Property Management System) y motor de reservas conversacional diseñado para el **Hotel Torre Satori** en Sevilla, Valle del Cauca, Colombia, operando actualmente sobre una base de **9 habitaciones de referencia** (con datos y tarifas de prueba mientras el cliente suministra el tarifario y descripción comercial definitiva de cada habitación).

El proyecto cuenta con el **núcleo transaccional de reservas, doble candado de concurrencia y flujo conversacional en WhatsApp (`V8`) completamente funcional y verificado**:

- **Infraestructura local y contenedores (`docker-compose.yml`):** Orquestación operativa de 6 servicios (`postgres:16-alpine` con extensión `btree_gist`, `redis:7-alpine`, `n8n:1.81.4`, `apps/api` en Java 21 / Spring Boot 3.3.5, `apps/web` en React 18 / Vite 5 y `cloudflared`).
- **Base de datos y migraciones Flyway (`V1` a `V5` + plantillas `V2` y `V6`):** Cinco migraciones estructurales activas que definen 8 tablas (`rooms`, `customers`, `bookings`, `products`, `inventory_movements`, `system_users`, `audit_logs`, `chat_messages`), la restricción de exclusión `no_overlapping_bookings` (`EXCLUDE USING gist`) y el historial de chat. Se corrigió el script [`db/seed/dev_seed.sql`](file:///home/guarinve/Documentos/SatoriPMS/db/seed/dev_seed.sql) (`system_users`), se actualizó [`V2__seed_rooms.sql.example`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/resources/db/migration/V2__seed_rooms.sql.example) a las **9 habitaciones de referencia** (`101`–`103`, `201`–`203`, `301`–`303`) y se renombró la plantilla de productos a [`V6__seed_products.sql.example`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/resources/db/migration/V6__seed_products.sql.example) para eliminar la colisión de versión con `V3__align_id_types_with_jpa.sql`.
- **Backend API (`apps/api`):** Servicios REST operativos en `BookingController`, `BookingService`, `RedisLockService` y `ConversationController`. Se corrigió el cálculo de reembolso estimado (`estimatedRefund`) en [`BookingService.java`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/java/com/satoripms/api/booking/BookingService.java) para que opere estrictamente sobre el monto realmente pagado (`totalPaidAmount` / `paid_amount`), se habilitó el campo `source` en [`BookingBatchRequestDto.java`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/java/com/satoripms/api/booking/BookingBatchRequestDto.java) para distinguir reservas `"web"` de `"chatbot"`, y se implementó el endpoint `POST /api/bookings/unlock` en [`BookingController.java`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/java/com/satoripms/api/booking/BookingController.java) para liberar inmediatamente los bloqueos temporales en Redis.
- **Chatbot WhatsApp (`flows/n8n/V8_ChatbotReservas.json` — 83 nodos):** Flujo híbrido (menú guiado + agente IA con Google Gemini Flash Lite) generado por [`tests/chatbot/build_v8_chatbot_flow.py`](file:///home/guarinve/Documentos/SatoriPMS/tests/chatbot/build_v8_chatbot_flow.py) y validado con [`tests/chatbot/verify_n8n_flow_integrity.py`](file:///home/guarinve/Documentos/SatoriPMS/tests/chatbot/verify_n8n_flow_integrity.py) (0 enlaces rotos, 0 nodos huérfanos). Se corrigió la alineación de las opciones 5 (`Revisar o Cancelar`) y 6 (`Hablar con agente`), se incorporó el aviso de privacidad (Ley 1581 de 2012) antes de pedir datos personales en ambos flujos, se añadió el desglose explícito de tarifa base y recargo por persona adicional tanto en `H Procesar Reserva Paso` como en `H Resumen y Pago IA`, y se conectó la liberación inmediata de bloqueos temporales en Redis (`POST /api/bookings/unlock`) al cancelar en pasarela, reiniciar sesión (`menu`) o limpiar sesiones inactivas.
- **Aplicación Web (`apps/web`):** Actualmente constituye un **boceto inicial básico** con dos vistas operativas de soporte ([`Conversations.tsx`](file:///home/guarinve/Documentos/SatoriPMS/apps/web/src/pages/Conversations.tsx) para el historial y control del bot por teléfono y [`ReservasDebug.tsx`](file:///home/guarinve/Documentos/SatoriPMS/apps/web/src/pages/ReservasDebug.tsx) para pruebas de reservas y bloqueos). Los módulos administrativos completos (CRUD de las 9 habitaciones por el Administrador, programación de eventos especiales y descuentos, calendario interactivo, check-in, check-out, tienda, finanzas, reseñas y autenticación JWT) se encuentran en estado **Aprobado y pendiente**.
- **Documentación y Presupuesto:** Toda la documentación de `README.md`, `docs/README.md`, `docs/modulos/` (excepto `EstadoActual.md`), `docs/Diagramas/` y `docs/Presupuesto/` (incluyendo [`Presupuesto_SatoriPMS.xlsx`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto_SatoriPMS.xlsx)) ha sido actualizada, alineada con el código real y redactada en lenguaje apto para el cliente conforme a la sección 12.C de `GEMINI.md`.

---

## 2. Cuadro Resumen de Componentes y Documentos

Los estados utilizados corresponden estrictamente al vocabulario de la sección 8 de [`GEMINI.md`](file:///home/guarinve/Documentos/SatoriPMS/GEMINI.md): **Existente y verificado**, **Aprobado y pendiente**, **Propuesto**, **En desarrollo**, **Obsoleto** y **No verificado**.

### 2.1 Componentes Técnicos del Sistema

| Componente | Estado | Documento relacionado | Última actualización |
| :--- | :--- | :--- | :---: |
| **Infraestructura Docker Compose (PostgreSQL 16, Redis 7, n8n, API, Web, Cloudflared)** | Existente y verificado | [`Infraestructura.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Infraestructura.md) | 2026-11-03 |
| **Pipeline CI/CD en GitHub Actions (`.github/workflows/ci.yml` — Java 21 Maven + React)** | Existente y verificado | [`Infraestructura.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Infraestructura.md) | 2026-11-03 |
| **Esquema de Base de Datos y Migraciones Flyway (`V1` a `V5`)** | Existente y verificado | [`Database.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Database.md) | 2026-11-03 |
| **Plantillas de Semillas SQL (`V2__seed_rooms.sql.example` 9 hab., `V6__seed_products.sql.example`, `dev_seed.sql`)** | Existente y verificado | [`Database.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Database.md) | 2026-11-03 |
| **Archivos locales de semillas reales (`V2__seed_rooms.sql`, `V3__seed_products.sql`)** | No verificado | [`Database.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Database.md) | 2026-11-03 |
| **Candado Nivel 1 en Redis (`RedisLockService.java` — Scripts Lua + `POST /api/bookings/unlock`)** | Existente y verificado | [`BackendAPI.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/BackendAPI.md) | 2026-11-03 |
| **Candado Nivel 2 en PostgreSQL (`no_overlapping_bookings` `EXCLUDE USING gist`)** | Existente y verificado | [`Database.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Database.md) | 2026-11-03 |
| **API REST de Reservas (`BookingController`, `BookingService`: `available`, `lock`, `unlock`, `confirm`, `pay-remaining`, `cancel`)** | Existente y verificado | [`BackendAPI.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/BackendAPI.md) | 2026-11-03 |
| **API REST de Conversaciones (`ConversationController`: mensajes, listado de chats y `toggle-bot`)** | Existente y verificado | [`BackendAPI.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/BackendAPI.md) | 2026-11-03 |
| **Flujo Chatbot WhatsApp V8 (`flows/n8n/V8_ChatbotReservas.json` — 83 nodos, menú guiado + IA Gemini)** | Existente y verificado | [`Chatbot.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Chatbot.md) | 2026-11-03 |
| **Flujos Chatbot anteriores (`V1` a `V7` en `flows/n8n/`)** | Obsoleto | [`Chatbot.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Chatbot.md) | 2026-11-03 |
| **Validación criptográfica `X-Hub-Signature-256` e idempotencia por `message_id` en flujo V8** | Aprobado y pendiente | [`Seguridad.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Seguridad.md) | 2026-11-03 |
| **Suite de Pruebas del Chatbot (`tests/chatbot/*.js`, `verify_n8n_flow_integrity.py`)** | Existente y verificado | [`Chatbot.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Chatbot.md) | 2026-11-03 |
| **Aplicación Web — Boceto inicial (`Conversations.tsx` y `ReservasDebug.tsx`)** | En desarrollo | [`AplicacionWeb.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/AplicacionWeb.md) | 2026-11-03 |
| **Administración CRUD de las 9 Habitaciones (crear, editar, eliminar sin reservas activas) por el Administrador** | Aprobado y pendiente | [`AplicacionWeb.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/AplicacionWeb.md) | 2026-11-03 |
| **Gestión de Eventos Especiales y Descuentos por Temporada (API, tabla y panel web)** | Aprobado y pendiente | [`AplicacionWeb.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/AplicacionWeb.md) | 2026-11-03 |
| **Paneles Web Operativos (Calendario de ocupación, Check-in, Check-out, Reserva Manual)** | Aprobado y pendiente | [`AplicacionWeb.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/AplicacionWeb.md) | 2026-11-03 |
| **Módulo de Tienda e Inventario en Backend y Web (`products`, `inventory_movements`)** | Aprobado y pendiente | [`TiendaInventario.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/TiendaInventario.md) | 2026-11-03 |
| **Módulo de Facturación, Finanzas, Egresos, Turnos y Exportación Excel** | Aprobado y pendiente | [`FacturacionFinanzas.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/FacturacionFinanzas.md) | 2026-11-03 |
| **Módulo de Reseñas Persistidas en BD y Fidelización de Clientes** | Aprobado y pendiente | [`ResenasFidelizacion.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/ResenasFidelizacion.md) | 2026-11-03 |
| **Autenticación JWT, Spring Security por Roles (`admin`/`receptionist`) y Bitácora de Auditoría** | Aprobado y pendiente | [`Seguridad.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Seguridad.md) | 2026-11-03 |
| **Issues del repositorio en GitHub (`#1` a `#108`: 54 cerrados, 34 abiertos) y Pull Request `#109`** | Existente y verificado | [`GestionProyecto.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/GestionProyecto.md) | 2026-11-03 |
| **Tablero externo GitHub Projects #2 (requiere alcance `read:project` en `gh auth`)** | No verificado | [`GestionProyecto.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/GestionProyecto.md) | 2026-11-03 |
| **Prototipo visual externo en Figma** | No verificado | [`DiseñoUXUI.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/DiseñoUXUI.md) | 2026-11-03 |
| **Conectividad con cuentas productivas de Meta WhatsApp Cloud API, Pasarela de Pagos y Cloudflare Tunnel** | No verificado | [`Infraestructura.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Infraestructura.md) | 2026-11-03 |

### 2.2 Documentos del Proyecto

| Componente (Documento) | Estado | Documento relacionado | Última actualización |
| :--- | :--- | :--- | :---: |
| [`GEMINI.md`](file:///home/guarinve/Documentos/SatoriPMS/GEMINI.md) | Existente y verificado | Reglas maestras del proyecto | 2026-11-03 |
| [`README.md`](file:///home/guarinve/Documentos/SatoriPMS/README.md) | Existente y verificado | Carta de presentación raíz | 2026-11-03 |
| [`docs/README.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/README.md) | Existente y verificado | Carta de presentación de `docs/` | 2026-11-03 |
| [`docs/modulos/EstadoActual.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/EstadoActual.md) | Existente y verificado | Documento único de estado, cambios y decisiones | 2026-11-03 |
| [`docs/CambiosPendientes.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/CambiosPendientes.md) | Existente y verificado | Acumulado de cambios por commit desde el último push | 2026-11-03 |
| [`docs/modulos/GeneralidadesNucleo.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/GeneralidadesNucleo.md) | Existente y verificado | Propósito, 9 habitaciones, tarifas, reembolsos y doble candado | 2026-11-03 |
| [`docs/modulos/Chatbot.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Chatbot.md) | Existente y verificado | Especificación funcional del asistente WhatsApp | 2026-11-03 |
| [`docs/modulos/AplicacionWeb.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/AplicacionWeb.md) | Existente y verificado | Especificación funcional de la aplicación web, CRUD habitaciones y eventos | 2026-11-03 |
| [`docs/modulos/BackendAPI.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/BackendAPI.md) | Existente y verificado | Especificación de servicios centrales y puntos de comunicación | 2026-11-03 |
| [`docs/modulos/Database.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Database.md) | Existente y verificado | Especificación de base de datos, tablas y memoria rápida | 2026-11-03 |
| [`docs/modulos/Seguridad.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Seguridad.md) | Existente y verificado | Especificación de roles, privacidad, sesión y auditoría | 2026-11-03 |
| [`docs/modulos/Infraestructura.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Infraestructura.md) | Existente y verificado | Especificación de contenedores, red, respaldos e integración continua | 2026-11-03 |
| [`docs/modulos/TiendaInventario.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/TiendaInventario.md) | Existente y verificado | Especificación de tienda interna y movimientos inmutables | 2026-11-03 |
| [`docs/modulos/FacturacionFinanzas.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/FacturacionFinanzas.md) | Existente y verificado | Especificación de ingresos, egresos, turnos y reportes en Excel | 2026-11-03 |
| [`docs/modulos/ResenasFidelizacion.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/ResenasFidelizacion.md) | Existente y verificado | Especificación de reseñas, filtro Google Maps y fidelización | 2026-11-03 |
| [`docs/modulos/GestionProyecto.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/GestionProyecto.md) | Existente y verificado | Metodología, equipo, etapas y criterios de calidad | 2026-11-03 |
| [`docs/modulos/DiseñoUXUI.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/DiseñoUXUI.md) | Existente y verificado | Identidad visual, paleta de colores, tipografía y componentes | 2026-11-03 |
| [`docs/Diagramas/README.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/README.md) y diagramas `01` a `05` | Existente y verificado | 5 diagramas Mermaid alineados con el código real y redacción cliente | 2026-11-03 |
| [`docs/Presupuesto/Presupuesto_SatoriPMS.xlsx`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto_SatoriPMS.xlsx) | Existente y verificado | Libro financiero oficial (5 hojas, 684 fórmulas, redacción cliente) | 2026-11-03 |
| [`docs/Presupuesto/Presupuesto.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto.md) | Existente y verificado | Resumen ejecutivo y desglose presupuestal alineado al `.xlsx` | 2026-11-03 |
| [`docs/Presupuesto/Actividad4_Crisis_Presupuestal.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Actividad4_Crisis_Presupuestal.md) | Existente y verificado | Análisis de escenarios de contingencia alineado al `.xlsx` | 2026-11-03 |
| [`docs/Reuniones/ReunionCliente.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/Reuniones/ReunionCliente.md) | Existente y verificado | Transcripción histórica intacta de levantamiento con el cliente | 2026-10-08 |
| [`docs/Actividades/ACTIVIDAD 4 (Escenarios de Crisis Presupuestal).pdf`](file:///home/guarinve/Documentos/SatoriPMS/docs/Actividades/ACTIVIDAD%204%20(Escenarios%20de%20Crisis%20Presupuestal).pdf) | Existente y verificado | Enunciado de referencia en formato PDF (intacto) | 2026-10-20 |

---

## 3. Estado Detallado del Proyecto (16 Puntos de la Sección 4.A)

### 3.1 Descripción General y Objetivos

**Torre Satori PMS** resuelve la gestión manual de reservas, la pérdida de clientes fuera del horario de recepción y el riesgo de sobreventa en el **Hotel Torre Satori** (Sevilla, Valle del Cauca). Sus objetivos principales son:
1. Automatizar la atención, cotización, reserva, cobro de anticipos (50% o 100%), pago de saldos y cancelación de estadías las 24 horas a través de WhatsApp.
2. Impedir de forma absoluta los cruces de reservas mediante un mecanismo de doble candado concurrente (Redis + PostgreSQL).
3. Proveer una aplicación web para la recepción y administración del hotel que centralice las **9 habitaciones**, la programación de eventos especiales y descuentos, el registro de llegadas y salidas, la tienda interna, las finanzas y la fidelización de huéspedes.

### 3.2 Alcance y Requisitos

El alcance funcional completo del proyecto comprende **32 requerimientos (`REQ-01` a `REQ-32`, 150 puntos de esfuerzo)** agrupados en 6 módulos funcionales:
1. **Motor de Reservas y Asistente en WhatsApp:** Reserva guiada y con inteligencia artificial, aviso de privacidad (Ley 1581 de 2012), desglose de tarifa base y recargo por persona adicional, abonos del 50% o 100%, consulta y pago de saldo pendiente, cancelación con reembolso calculado estrictamente sobre el monto pagado (`paid_amount`), liberación inmediata de bloqueos temporales en Redis y transferencia a agente humano.
2. **Operación de Recepción y Administración Web:** Gestión completa (crear, editar precios/capacidades/descripciones y eliminar sin reservas pendientes o activas) de las **9 habitaciones** por parte del Administrador, programación de **eventos especiales y descuentos por temporada**, calendario interactivo de ocupación, check-in, check-out, reservas manuales y bandeja de conversaciones.
3. **Tienda Interna e Inventario:** Catálogo de productos, ventas directas o con cargo a la habitación, y kardex inmutable de movimientos de inventario (`ENTRY`, `EXIT`, `SALE`, `ADJUSTMENT`).
4. **Facturación, Finanzas y Turnos:** Consolidado de ingresos y egresos, liquidación de turnos de recepción y exportación contable en Excel.
5. **Reseñas y Fidelización:** Captura de reseñas en WhatsApp con redirección a Google Maps para calificaciones de 4 y 5 estrellas, moderación interna y detección de huéspedes frecuentes.
6. **Seguridad y Auditoría:** Autenticación por credenciales, control de permisos por rol (`admin` y `receptionist`) y bitácora inmutable de auditoría (`audit_logs`).

### 3.3 Características y Componentes Principales

- **Backend API (`apps/api`):** Aplicación Java 21 con Spring Boot 3.3.5, Spring Data JPA, Spring Data Redis y Flyway. Expone los controladores [`BookingController.java`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/java/com/satoripms/api/booking/BookingController.java), [`ConversationController.java`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/java/com/satoripms/api/conversation/ConversationController.java) y [`HealthController.java`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/java/com/satoripms/api/HealthController.java).
- **Servicio de Bloqueo Atómico (`RedisLockService.java`):** Ejecuta dos scripts Lua sobre un conjunto ordenado (`ZSET`) en Redis por habitación (`room:locks:{roomId}`), almacenando intervalos codificados como `startEpochMs:endEpochMs:sessionId` y verificando que `existingStart < reqEnd` y `existingEnd > reqStart` con expiración de 900 segundos (15 minutos).
- **Base de Datos Relacional (`PostgreSQL 16`):** Ocho tablas creadas por Flyway (`V1` a `V5`), incluyendo la restricción `no_overlapping_bookings` (`EXCLUDE USING gist (room_id WITH =, daterange(check_in, check_out, '[)') WITH &&) WHERE (status IN ('pending_payment', 'confirmed'))`).
- **Orquestador Conversacional (`flows/n8n/V8_ChatbotReservas.json`):** Flujo de 83 nodos en n8n que integra el webhook de WhatsApp, gestión de sesión en Redis (`session:{phone}` con TTL de 1800 segundos), máquina de estados determinista (`H Router Principal`, `H Procesar Reserva Paso`, `H Gestion Reserva`), agente de inteligencia artificial con Google Gemini Flash Lite (`A Construir Prompt IA`, `G Llamar Gemini IA`, `A Procesar Respuesta IA`, `H Resumen y Pago IA`), liberación inmediata de candados (`API Liberar Bloqueo Temporal`, `API Liberar Bloqueo Inactivo`) y cron de limpieza (`Cron Limpieza Sesiones` cada 5 minutos).
- **Aplicación Web (`apps/web`):** SPA en React 18, TypeScript y Vite 5 con enrutamiento en [`App.tsx`](file:///home/guarinve/Documentos/SatoriPMS/apps/web/src/App.tsx) hacia [`Conversations.tsx`](file:///home/guarinve/Documentos/SatoriPMS/apps/web/src/pages/Conversations.tsx) y [`ReservasDebug.tsx`](file:///home/guarinve/Documentos/SatoriPMS/apps/web/src/pages/ReservasDebug.tsx).

### 3.4 Estructura y Organización del Repositorio

```text
SatoriPMS/
├── .github/workflows/ci.yml                 # Integración continua (Java 21 Maven + React Vite)
├── apps/
│   ├── api/                                 # Backend Spring Boot 3.3.5 (Java 21)
│   │   ├── src/main/java/com/satoripms/api/
│   │   │   ├── booking/                     # Controlador, servicio, entidades y DTOs de reservas y habitaciones
│   │   │   ├── conversation/                # Controlador, entidades y repositorios de historial de chat
│   │   │   ├── lock/                        # RedisLockService (scripts Lua atómicos)
│   │   │   └── config/                      # CorsConfig y RedisConfig
│   │   └── src/main/resources/db/migration/ # Migraciones Flyway V1..V5 y plantillas V2 y V6 (.example)
│   └── web/                                 # Frontend React 18 + TypeScript + Vite
│       └── src/pages/                       # Vistas iniciales: Conversations.tsx y ReservasDebug.tsx
├── db/seed/dev_seed.sql                     # Semilla de desarrollo (9 habitaciones, productos, admin)
├── docs/
│   ├── README.md                            # Carta de presentación de la documentación
│   ├── CambiosPendientes.md                 # Cambios acumulados por commit desde el último push
│   ├── Actividades/                         # Enunciado PDF de referencia (intacto)
│   ├── Diagramas/                           # 5 diagramas de arquitectura y procesos + README
│   ├── Presupuesto/                         # Presupuesto_SatoriPMS.xlsx, Presupuesto.md, Actividad4
│   ├── Reuniones/                           # Transcripción ReunionCliente.md (intacta)
│   └── modulos/                             # EstadoActual.md + 12 especificaciones funcionales para cliente
├── flows/n8n/                               # V8_ChatbotReservas.json (activo) y V1..V7 (históricos)
├── scripts/                                 # Scripts operativos de levantamiento y respaldo
├── tests/chatbot/                           # Generador Python de V8, validador de integridad y 10 tests JS
├── docker-compose.yml                       # Orquestación local de los 6 contenedores
├── GEMINI.md                                # Directrices maestras del proyecto
└── README.md                                # Carta de presentación principal del repositorio
```

### 3.5 Recursos y Elementos Disponibles

- **Entorno Dockerizado completo:** Definido en [`docker-compose.yml`](file:///home/guarinve/Documentos/SatoriPMS/docker-compose.yml) y configurable mediante [`.env.example`](file:///home/guarinve/Documentos/SatoriPMS/.env.example).
- **Generador y verificador determinista del flujo n8n:** [`tests/chatbot/build_v8_chatbot_flow.py`](file:///home/guarinve/Documentos/SatoriPMS/tests/chatbot/build_v8_chatbot_flow.py) construye [`flows/n8n/V8_ChatbotReservas.json`](file:///home/guarinve/Documentos/SatoriPMS/flows/n8n/V8_ChatbotReservas.json) y [`tests/chatbot/verify_n8n_flow_integrity.py`](file:///home/guarinve/Documentos/SatoriPMS/tests/chatbot/verify_n8n_flow_integrity.py) valida todas sus conexiones.
- **Suite de pruebas extremo a extremo del chatbot:** 10 scripts en `tests/chatbot/` ejecutables mediante `tests/chatbot/run_all.sh`.
- **Modelo financiero integral:** [`docs/Presupuesto/Presupuesto_SatoriPMS.xlsx`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto_SatoriPMS.xlsx) con 5 hojas vinculadas dinámicamente y 684 fórmulas verificadas.

### 3.6 Estado Detallado de Cada Componente y Documento

#### A. Componentes de Código e Infraestructura
1. **Base de Datos y Migraciones (`apps/api/src/main/resources/db/migration/`):**
   - **Estado:** `Existente y verificado`.
   - `V1__init_schema.sql`: Crea tablas `rooms`, `customers`, `bookings`, `products`, `inventory_movements`, `system_users`, `audit_logs` y la restricción `no_overlapping_bookings`.
   - `V3__align_id_types_with_jpa.sql`: Alinea las claves primarias e identificadores foráneos a `BIGINT` (`Long`).
   - `V4__add_booking_group_fields.sql`: Añade `reservation_code`, `holder_name`, `holder_doc`, `paid_amount` y `extra_guests`.
   - `V5__create_chat_messages_table.sql`: Crea `chat_messages` y añade `bot_enabled` a `customers`.
   - Plantillas: `V2__seed_rooms.sql.example` contiene las **9 habitaciones de referencia** (`101`–`103`, `201`–`203`, `301`–`303`) y `V6__seed_products.sql.example` contiene los 12 productos iniciales sin colisionar con `V3`.
2. **Backend API (`apps/api`):**
   - **Estado:** `Existente y verificado` para el núcleo de reservas, bloqueos y conversaciones; `Aprobado y pendiente` para CRUD de habitaciones, eventos especiales, tienda, finanzas, reseñas y autenticación JWT.
   - Endpoints activos verificados en código:
     - `GET /api/health` (`HealthController.java`)
     - `GET /api/bookings/available` (`BookingController.java`)
     - `POST /api/bookings/lock` (`BookingController.java`)
     - `POST /api/bookings/unlock` (`BookingController.java` — libera de inmediato todos los candados temporales de una sesión o grupo de habitaciones)
     - `POST /api/bookings/confirm` (`BookingController.java` — persiste reservas con `source` `"chatbot"` o `"web"`, calcula tarifa base + recargo por huéspedes adicionales y elimina el bloqueo en Redis)
     - `GET /api/bookings/details` (`BookingController.java` — calcula `estimatedRefund` sobre `totalPaidAmount`)
     - `POST /api/bookings/pay-remaining` (`BookingController.java`)
     - `POST /api/bookings/cancel` (`BookingController.java` — calcula reembolso real sobre `paidAmount` según ventanas `> 72h` = 100%, `24h–72h` = 50%, `< 24h` = 0%)
     - `POST /api/conversations/messages`, `GET /api/conversations`, `GET /api/conversations/{phone}/messages`, `PATCH /api/conversations/{phone}/toggle-bot` (`ConversationController.java`).
3. **Flujo Chatbot WhatsApp (`flows/n8n/V8_ChatbotReservas.json`):**
   - **Estado:** `Existente y verificado` (83 nodos).
   - Opciones del menú principal alineadas con el código y las pruebas: `1` Habitaciones y precios, `2` Disponibilidad, `3` Reservar, `4` Dejar reseña, `5` Revisar o cancelar reserva, `6` Hablar con un agente.
   - Incluye aviso de privacidad (Ley 1581 de 2012) antes de capturar nombre y documento tanto en el flujo guiado (`H Procesar Reserva Paso`) como en el flujo asistido por IA (`A Construir Prompt IA`).
   - Muestra el desglose explícito de tarifa base + recargo por persona adicional tanto en el resumen del flujo guiado como en el nodo `H Resumen y Pago IA`.
   - Libera de inmediato los bloqueos temporales en Redis (`POST /api/bookings/unlock`) cuando el usuario cancela en el paso de pago, escribe `menu` para reiniciar su sesión o cuando el cron de limpieza elimina una sesión inactiva.
   - **Elementos aún no activos en el flujo V8 (Estado: `Aprobado y pendiente`):** La verificación criptográfica de firma `X-Hub-Signature-256` en el nodo webhook y el descarte de mensajes duplicados por `message_id` en Redis están definidos en la especificación de seguridad (`Seguridad.md`), pero aún no están conectados como nodos activos dentro de `V8_ChatbotReservas.json`.
4. **Aplicación Web (`apps/web`):**
   - **Estado:** `En desarrollo` (boceto inicial).
   - Solo existen las páginas `Conversations.tsx` (bandeja de chats e interruptor del bot) y `ReservasDebug.tsx` (herramienta de prueba de reservas web que envía `source: "web"`).
   - Faltan por construir todas las vistas operativas definitivas: inicio de sesión, administración CRUD de las 9 habitaciones por el Administrador, programación de eventos especiales y descuentos, calendario de ocupación, check-in, check-out, tienda, finanzas, reseñas y auditoría.

#### B. Documentación Funcional, Diagramas y Presupuesto
- Todos los documentos de `docs/modulos/` (excepto `EstadoActual.md`) fueron reescritos como **especificaciones funcionales y de diseño orientadas al cliente** (sin fragmentos de código, sin nombres de funciones, sin códigos internos `HU-*`/`CU-*`/`RN-*` y sin emojis), explicando con claridad cómo debe funcionar el sistema completo.
- Los documentos con mayor carga técnica (`BackendAPI.md`, `Database.md`, `Infraestructura.md`, `Seguridad.md`) explican cada concepto en español natural e incluyen el formato `Concepto en español : "identificador_tecnico"` dispuesto en la sección 12.C de `GEMINI.md`.
- Los 5 diagramas en `docs/Diagramas/` fueron reestructurados con sintaxis Mermaid limpia, bien distribuida y alineada con los endpoints reales, estados en minúscula (`'pending_payment'`, `'confirmed'`, `'finished'`, `'cancelled'`), el desbloqueo inmediato en Redis, el reembolso sobre lo pagado y la administración de las 9 habitaciones y eventos especiales.
- El libro [`Presupuesto_SatoriPMS.xlsx`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto_SatoriPMS.xlsx) y los documentos [`Presupuesto.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto.md) y [`Actividad4_Crisis_Presupuestal.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Actividad4_Crisis_Presupuestal.md) están 100% sincronizados en cifras (`$24.685.000 COP` CAPEX, `$289.842 COP/mes` OPEX, `$28.163.100 COP` TCO Año 1, 9 habitaciones, 150 puntos) y redactados sin jerga interna.

#### C. Auditoría de Issues en GitHub (`#1` a `#108`) y Pull Request `#109` frente al Código Real
- Mediante GitHub CLI (`gh issue list --repo JuanJarias/SatoriPMS --limit 120 --state all` y `gh pr view 109`) se verificó el estado real del repositorio remoto:
  - **Total de Issues registrados:** **88 issues** (numerados del `#1` al `#108`), con **54 cerrados (`CLOSED`)** y **34 abiertos (`OPEN`)**.
  - **Pull Request `#109`:** `feat(core): integración de persistencia PostgreSQL, concurrencia Redis, flujos n8n y arquitectura operativa` (`feat/database-redis-setup` hacia `main`), **fusionado (`MERGED`)** en `origin/main` (commit `633def8`).
  - **Tablero GitHub Projects #2:** Permanece como `No verificado` debido a que el token de sesión actual requiere el alcance adicional `read:project` (`gh auth refresh -s read:project`).
- **Discrepancias detectadas entre los Issues de GitHub y el código real (prevalece el código según Sección 12.D):**
  1. *Issues marcados como `CLOSED` en GitHub cuya implementación real en código aún está pendiente (`Aprobado y pendiente`):*
     - `#20` (`CU-02b: Cancelar reserva App Web — Recepcionista`), `#24` y `#25` (`CU-03: Registrar check-in`), `#26` (`Crear reserva manual`), `#27` y `#28` (`CU-04: Registrar check-out`), `#79` (`[TASK-15] Login con JWT y guard de rol`), `#80` (`[TASK-16] Gateway WebSocket`), `#82` (`[TASK-17] Asociar consumos de tienda a la habitación para cobro en check-out`) y `#90` a `#94` (`[DEP-01..05]` Despliegue en producción, activación de WhatsApp Business productivo y capacitación presencial).
  2. *Issues que figuran como `OPEN` en GitHub pero cuya funcionalidad ya está implementada y verificada en `V8_ChatbotReservas.json` y `BookingService.java`:*
     - `#30` (`[E1-CU-01] Manejar habitación no disponible al confirmar selección`), `#31` (`[E2-CU-01] Rechazar y sugerir alternativas cuando se excede capacidad máxima`), `#32` (`[E3-CU-01] Job de liberación automática de bloqueo temporal vencido`), `#33` (`[E4-CU-01] Manejo de reintento cuando falla el pago`), `#46` (`[HU-04] Dejar reseña y calificación después del check-out`), `#52` (`[HU-09] Recibir recomendación de habitación asistida por IA`) y `#76` (`[CU-01.3] Validar capacidad y aplicar cargo por persona extra`).

### 3.7 Decisiones Importantes Vigentes

Las decisiones arquitectónicas y de negocio vigentes se detallan en la Sección 5 (Registro de Decisiones) e incluyen:
- **DEC-01:** Arquitectura de monolito modular en Java 21 / Spring Boot 3.3 sobre VPS Linux frente a microservicios o SaaS comercial.
- **DEC-02:** Mecanismo de doble candado concurrente (scripts Lua en Redis con TTL de 15 min + liberación inmediata y restricción `EXCLUDE USING gist` en PostgreSQL).
- **DEC-03:** Política de reembolso por cancelación calculada estrictamente sobre el monto efectivamente pagado (`paid_amount`).
- **DEC-04:** Operación sobre 9 habitaciones de referencia con administración CRUD exclusiva del Administrador (prohibiendo eliminar habitaciones con reservas pendientes o activas) y programación de eventos especiales y descuentos.
- **DEC-05:** Unificación del seguimiento del proyecto en `EstadoActual.md` y `CambiosPendientes.md`, manteniendo el resto de documentos orientados al cliente.

### 3.8 Avances Realizados

1. Implementación y verificación del backend de reservas, doble candado Redis + PostgreSQL y bandeja de conversaciones en Spring Boot 3.3.5.
2. Implementación y verificación del flujo conversacional híbrido `V8_ChatbotReservas.json` (83 nodos) en n8n con menú guiado, agente IA Gemini Flash Lite, aviso de privacidad, desglose de recargo por persona adicional, opciones 5 y 6 corregidas y liberación inmediata de bloqueos temporales.
3. Corrección de defectos en código y configuración: tabla `system_users` en `dev_seed.sql`, plantilla `V2__seed_rooms.sql.example` con 9 habitaciones, renombrado de `V6__seed_products.sql.example`, cálculo de `estimatedRefund` sobre `totalPaidAmount`, soporte de `source = "web"`, endpoint `POST /api/bookings/unlock` y pipeline Maven Java 21 en `.github/workflows/ci.yml`.
4. Actualización integral y normalización de toda la documentación (`README.md`, `docs/README.md`, 12 módulos en `docs/modulos/`, 6 archivos en `docs/Diagramas/` y 3 archivos en `docs/Presupuesto/` incluyendo `Presupuesto_SatoriPMS.xlsx`).

### 3.9 Trabajos Pendientes

1. **Backend y Base de Datos (`apps/api`):**
   - Crear migración Flyway `V6` (o siguiente numeración estructural) para la tabla de eventos especiales y descuentos (`special_events`) y campos adicionales de habitaciones si se requieren.
   - Implementar endpoints REST protegidos por rol Administrador para el CRUD de las 9 habitaciones (`POST /api/rooms`, `PUT /api/rooms/{id}`, `DELETE /api/rooms/{id}` validando ausencia de reservas en `'pending_payment'` o `'confirmed'`) y para eventos especiales (`GET/POST/PUT/DELETE /api/special-events`).
   - Integrar el descuento de eventos especiales vigentes en el cálculo de tarifas de `BookingService`.
   - Implementar los controladores y servicios de Check-in, Check-out, Tienda e Inventario (`ProductController`, `InventoryController`), Finanzas (`FinanceController`, exportación Apache POI), Reseñas (`ReviewController`), Fidelización y Seguridad JWT (`Spring Security` + `audit_logs`).
2. **Aplicación Web (`apps/web`):**
   - Evolucionar el boceto actual hacia la aplicación web completa para Recepcionista y Administrador (login, calendario de ocupación, CRUD de las 9 habitaciones, eventos especiales, check-in, check-out, reserva manual, tienda, finanzas y reseñas).
3. **Chatbot WhatsApp (`flows/n8n/V8_ChatbotReservas.json`):**
   - Incorporar la validación criptográfica `X-Hub-Signature-256` y la deduplicación por `message_id` en la entrada del webhook cuando se conecte la cuenta productiva de Meta.
4. **Definición comercial con el cliente:**
   - Recibir del propietario del Hotel Torre Satori la descripción comercial definitiva y los precios reales de cada una de las 9 habitaciones para reemplazar las tarifas de prueba actuales.

### 3.10 Problemas Conocidos y Riesgos

- **Tarifas y descripciones de habitaciones en modo prueba:** Actualmente las 9 habitaciones (`101`–`103`, `201`–`203`, `301`–`303`) utilizan tarifas y descripciones de referencia para permitir el desarrollo y las pruebas. Esto se mitigará mediante el módulo CRUD de habitaciones en la aplicación web, que permitirá al Administrador editar precios, capacidades y descripciones en cualquier momento sin tocar el código.
- **Herramientas de compilación en el host local:** En el entorno anfitrión actual no están instalados globalmente los binarios `mvn` ni `npm` en el `PATH` (las compilaciones se ejecutan dentro de los contenedores definidos en `docker-compose.yml` y en GitHub Actions).

### 3.11 Restricciones y Dependencias

- **Restricciones de negocio:** Ninguna habitación con reservas pendientes de pago (`pending_payment`) o confirmadas (`confirmed`) puede ser eliminada; ningún movimiento de inventario ni registro de auditoría puede editarse o borrarse; todo reembolso se calcula exclusivamente sobre el monto pagado (`paid_amount`).
- **Dependencias externas para salida a producción:** Verificación de la cuenta comercial en Meta Business Manager, adquisición de la línea móvil dedicada para el bot, llave productiva de Google AI Studio (`GEMINI_API_KEY`) y credenciales productivas de la pasarela de pagos.

### 3.12 Características Futuras Previstas

- Pasarela de pagos en línea con confirmación automática por webhook (reemplazando la simulación de pasarela actual del MVP).
- Envío automático de mensajes de recordatorio antes de la llegada y campañas promocionales de eventos especiales a huéspedes frecuentes.
- Sincronización de calendarios con portales externos (Booking / Airbnb) en una fase posterior a la estabilización del sistema principal.

### 3.13 Propuestas Todavía No Aprobadas

- Actualmente no existen propuestas técnicas sin aprobar; todas las mejoras planteadas en la revisión integral (liberación inmediata del bloqueo en Redis, cálculo de reembolso sobre lo pagado, CRUD de las 9 habitaciones por el Administrador, programación de eventos especiales y descuentos, aviso de privacidad y desglose de recargos en WhatsApp) fueron aprobadas por el usuario e incorporadas al diseño y al código base.

### 3.14 Referencias a los Documentos de Respaldo

- Reglas de trabajo y documentación: [`GEMINI.md`](file:///home/guarinve/Documentos/SatoriPMS/GEMINI.md)
- Cambios pendientes de commit/push: [`docs/CambiosPendientes.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/CambiosPendientes.md)
- Levantamiento de requerimientos con el cliente: [`docs/Reuniones/ReunionCliente.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/Reuniones/ReunionCliente.md)
- Modelo financiero oficial: [`docs/Presupuesto/Presupuesto_SatoriPMS.xlsx`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto_SatoriPMS.xlsx) y [`docs/Presupuesto/Presupuesto.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto.md)
- Especificaciones de módulos: [`docs/modulos/`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/)
- Diagramas de arquitectura y flujo: [`docs/Diagramas/`](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/)

### 3.15 Fecha de la Última Revisión Integral

- **2026-11-03** (Revisión integral completa de código, base de datos, flujos n8n, pruebas, presupuesto, diagramas y documentación).

### 3.16 Fecha del Último Punto de Control

- **2026-11-03** (Punto de control establecido tras completar la Fase 2 de la revisión integral).

---

## 4. Registro de Cambios

Ordenado cronológicamente con lo más reciente primero, conforme a la sección 4.B y 12.B de [`GEMINI.md`](file:///home/guarinve/Documentos/SatoriPMS/GEMINI.md).

### 4.1 Entrada del 2026-11-03 — Revisión Integral del Proyecto, Correcciones en Código/Flujo V8 y Normalización Documental

- **Fecha:** `2026-11-03`
- **Categoría:** Cambio realizado (código, flujo conversacional, pruebas, presupuesto y documentación completa) + Decisiones aprobadas.
- **Descripción:**
  1. Se corrigieron defectos puntuales en el código fuente y configuración: nombre de tabla `system_users` en [`db/seed/dev_seed.sql`](file:///home/guarinve/Documentos/SatoriPMS/db/seed/dev_seed.sql); actualización de [`V2__seed_rooms.sql.example`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/resources/db/migration/V2__seed_rooms.sql.example) a 9 habitaciones de referencia; renombrado de `V3__seed_products.sql.example` a [`V6__seed_products.sql.example`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/resources/db/migration/V6__seed_products.sql.example); corrección de `estimatedRefund` en [`BookingService.java`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/java/com/satoripms/api/booking/BookingService.java) para que calcule el reembolso sobre `totalPaidAmount` (`paid_amount`); soporte del campo `source` (`"web"` / `"chatbot"`) en [`BookingBatchRequestDto.java`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/java/com/satoripms/api/booking/BookingBatchRequestDto.java) y [`ReservasDebug.tsx`](file:///home/guarinve/Documentos/SatoriPMS/apps/web/src/pages/ReservasDebug.tsx); creación del endpoint `POST /api/bookings/unlock` en [`BookingController.java`](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/java/com/satoripms/api/booking/BookingController.java); exclusión de `.directory` en [`.gitignore`](file:///home/guarinve/Documentos/SatoriPMS/.gitignore); y reemplazo del flujo de GitHub Actions en [`.github/workflows/ci.yml`](file:///home/guarinve/Documentos/SatoriPMS/.github/workflows/ci.yml) por Java 21 + Maven.
  2. Se actualizó [`tests/chatbot/build_v8_chatbot_flow.py`](file:///home/guarinve/Documentos/SatoriPMS/tests/chatbot/build_v8_chatbot_flow.py) y se regeneró [`flows/n8n/V8_ChatbotReservas.json`](file:///home/guarinve/Documentos/SatoriPMS/flows/n8n/V8_ChatbotReservas.json) (pasando de 80 a 83 nodos): se corrigió el orden de las opciones 5 (`Revisar o Cancelar`) y 6 (`Hablar con agente`), se añadió el aviso de privacidad antes de solicitar datos personales en los flujos guiado e IA, se incorporó el desglose explícito de tarifa base + recargo por persona adicional en `H Procesar Reserva Paso` y `H Resumen y Pago IA`, y se conectó la liberación inmediata de bloqueos temporales en Redis (`POST /api/bookings/unlock`) al cancelar el pago, reiniciar con `menu` o limpiar sesiones inactivas. Se actualizaron los scripts de prueba [`test_cancelacion_reembolso.js`](file:///home/guarinve/Documentos/SatoriPMS/tests/chatbot/test_cancelacion_reembolso.js), [`test_pago_saldo_restante.js`](file:///home/guarinve/Documentos/SatoriPMS/tests/chatbot/test_pago_saldo_restante.js) y [`test_escalamiento_agente_humano.js`](file:///home/guarinve/Documentos/SatoriPMS/tests/chatbot/test_escalamiento_agente_humano.js).
  3. Se reescribieron [`README.md`](file:///home/guarinve/Documentos/SatoriPMS/README.md), [`docs/README.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/README.md), los 12 documentos de especificación en `docs/modulos/`, los 6 documentos en `docs/Diagramas/` y los 3 documentos en `docs/Presupuesto/` (incluyendo la actualización de textos en [`Presupuesto_SatoriPMS.xlsx`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto_SatoriPMS.xlsx)), aplicando las reglas de redacción para el cliente (sección 12.C de `GEMINI.md`), incorporando las **9 habitaciones de referencia**, el **CRUD de habitaciones por el Administrador**, la **gestión de eventos especiales y descuentos**, y la **política de reembolso sobre el monto pagado**.
- **Motivo:** Solicitud expresa del usuario de realizar una revisión integral del proyecto conforme a la sección 5 y sección 12 de `GEMINI.md`, corrigiendo discrepancias entre código y documentos, solucionando defectos puntuales en el backend y en el flujo V8, y adaptando todos los documentos orientados al cliente.
- **Estado anterior y posterior:**
  - *Anterior:* Documentos con referencias a tecnologías descartadas (NestJS/TypeORM), códigos internos (`HU-*`, `CU-*`, `RN-*`), cifras presupuestales divergentes entre `.xlsx` y `.md`, opciones 5 y 6 invertidas en `V8_ChatbotReservas.json`, sin liberación inmediata en Redis al cancelar o reiniciar sesión, `estimatedRefund` calculado sobre `totalGroupPrice` en `getReservationDetailsByCode`, colisión de versión `V3` en plantillas SQL y pipeline CI configurado para Node.js en `apps/api`.
  - *Posterior:* Código, plantillas SQL, flujo n8n V8 (83 nodos), tests, CI/CD, modelo financiero `.xlsx` y toda la documentación 100% coherentes, verificados y alineados con las directrices de `GEMINI.md`.
- **Elementos afectados:** `.gitignore`, `.github/workflows/ci.yml`, `db/seed/dev_seed.sql`, `V2__seed_rooms.sql.example`, `V6__seed_products.sql.example` (antes `V3`), `BookingBatchRequestDto.java`, `BookingService.java`, `BookingController.java`, `ReservasDebug.tsx`, `build_v8_chatbot_flow.py`, `V8_ChatbotReservas.json`, 3 tests JS del chatbot, `README.md`, `docs/README.md`, `docs/CambiosPendientes.md`, 13 archivos en `docs/modulos/`, 6 archivos en `docs/Diagramas/` y 3 archivos en `docs/Presupuesto/`.
- **Consecuencias y dependencias:** Los cambios locales quedan listos y segmentados en [`docs/CambiosPendientes.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/CambiosPendientes.md) en 5 commits coherentes por propósito, pendientes de que el usuario autorice su commit y push.
- **Verificaciones realizadas:**
  - Ejecución de `python3 tests/chatbot/build_v8_chatbot_flow.py` y `python3 tests/chatbot/verify_n8n_flow_integrity.py` con resultado exitoso (`83 nodos`, `0 errores`, `0 enlaces rotos`, `0 nodos huérfanos`).
  - Verificación estructural y XML de `docs/Presupuesto/Presupuesto_SatoriPMS.xlsx` mediante script Python (`0 errores XML`, `684 fórmulas intactas`, `0 códigos internos HU/CU/RN`).
  - Inspección estática completa de los cambios en Java, TypeScript, SQL y Markdown.
- **Problemas identificados:** Los binarios `mvn` y `npm` no se encuentran instalados directamente en el `PATH` del sistema operativo anfitrión (se ejecutan dentro de los contenedores Docker o en GitHub Actions), por lo que la compilación Maven/Vite fuera de contenedor no se ejecutó en esta sesión.
- **Estado final:** `Existente y verificado`.

### 4.2 Entrada del 2026-10-25 — Implementación del Flujo Conversacional Híbrido V8, Historial de Chat y Reservas Grupales (Commit `605c230`)

- **Fecha:** `2026-10-25`
- **Categoría:** Cambio realizado (enviado al repositorio remoto en `origin/feat/database-redis-setup`).
- **Descripción:** Creación de las migraciones `V4__add_booking_group_fields.sql` y `V5__create_chat_messages_table.sql`, implementación de `ConversationController`, soporte de reservas multi-habitación bajo un mismo `reservation_code`, pago de saldo restante (`pay-remaining`), cancelación con cálculo de reembolso (`cancel`), vista web de conversaciones (`Conversations.tsx`) y construcción del flujo `V8_ChatbotReservas.json` con asistente IA Gemini Flash Lite y suite de pruebas en `tests/chatbot/`.
- **Motivo:** Dotar al sistema de atención híbrida (guiada + IA), soporte para múltiples habitaciones por reserva y bandeja de supervisión humana desde la aplicación web.
- **Estado anterior y posterior:** Paso de flujos preliminares (`V1`–`V7`) y reservas individuales a un motor de reservas grupales e individuales con persistencia de mensajes y control de activación del bot por cliente.
- **Elementos afectados:** `apps/api/src/main/java/com/satoripms/api/booking/*`, `conversation/*`, `V4`, `V5`, `apps/web/src/pages/Conversations.tsx`, `flows/n8n/V8_ChatbotReservas.json` y `tests/chatbot/*`.
- **Consecuencias y dependencias:** Sirvió como base para las correcciones y mejoras aplicadas en la revisión integral del `2026-11-03`.
- **Verificaciones realizadas:** Pruebas de integración del flujo en `tests/chatbot/` y validación de migraciones Flyway `V1` a `V5`.
- **Problemas identificados:** Opciones 5 y 6 invertidas en el router del flujo V8 y cálculo de `estimatedRefund` sobre el total de la reserva en la vista previa de detalles (ambos corregidos el `2026-11-03`).
- **Estado final:** `Existente y verificado`.

---

## 5. Registro de Decisiones

Cada decisión documenta su contexto, la alternativa adoptada, las alternativas descartadas, sus consecuencias y su vigencia (secciones 4.C y 12.B de [`GEMINI.md`](file:///home/guarinve/Documentos/SatoriPMS/GEMINI.md)).

### DEC-01: Arquitectura de Monolito Modular en Java 21 / Spring Boot 3.3 sobre VPS Linux

- **Contexto:** Se requería una plataforma de backend robusta, transaccional y económica de sostener mensualmente para un hotel de 9 habitaciones en Sevilla, Valle del Cauca.
- **Decisión tomada:** Adoptar un monolito modular en **Java 21 y Spring Boot 3.3.5** desplegado junto con PostgreSQL 16, Redis 7 y n8n mediante Docker Compose en un servidor privado virtual (VPS Linux de 4 GB RAM).
- **Alternativas descartadas:**
  1. *Arquitectura de microservicios distribuidos:* Descartada por sobrecosto operativo en memoria RAM, complejidad de red innecesaria para la escala del hotel y mayor tiempo de mantenimiento.
  2. *Backend en Node.js / NestJS con TypeORM:* Explorado en bocetos documentales iniciales, pero descartado en favor de la solidez tipada y transaccional de Java 21, Spring Boot, JPA/Hibernate y Flyway.
  3. *Suscripción a un PMS comercial en la nube (Cloudbeds / Mews):* Descartada por su alto costo recurrente (`~$330 USD/mes` frente a `~$70 USD/mes` de OPEX total en SatoriPMS).
- **Consecuencias:** Ahorro estimado de `$12.955.900 COP/año` para el hotel, control total del código y despliegue simplificado en un solo servidor.
- **Vigencia:** Vigente.

### DEC-02: Mecanismo de Doble Candado Concurrente (Redis Lua + PostgreSQL `EXCLUDE USING gist`) y Desbloqueo Inmediato

- **Contexto:** Evitar de forma absoluta que dos clientes (por WhatsApp o recepción web) reserven la misma habitación en fechas superpuestas mientras uno de ellos realiza el pago del anticipo.
- **Decisión tomada:** Implementar un doble candado:
  1. **Candado Nivel 1 (Temporal en Redis):** Conjunto ordenado (`ZSET`) por habitación evaluado de forma atómica con scripts Lua por un máximo de 15 minutos (`900 segundos`), acompañado del endpoint `POST /api/bookings/unlock` para liberar inmediatamente los intervalos cuando el usuario cancela el pago, reinicia su sesión (`menu`) o expira por inactividad en n8n.
  2. **Candado Nivel 2 (Definitivo en PostgreSQL):** Restricción `no_overlapping_bookings` (`EXCLUDE USING gist (room_id WITH =, daterange(check_in, check_out, '[)') WITH &&) WHERE (status IN ('pending_payment', 'confirmed'))`).
- **Alternativas descartadas:**
  1. *Verificación simple mediante consultas `SELECT` antes de `INSERT`:* Descartada por ser vulnerable a condiciones de carrera cuando dos peticiones llegan en el mismo milisegundo.
  2. *Esperar pasivamente los 15 minutos del TTL en Redis cuando el cliente cancela o reinicia la conversación:* Descartada porque retenía innecesariamente el inventario del hotel durante 15 minutos.
- **Consecuencias:** Cero sobreventas garantizadas desde el motor de base de datos y disponibilidad recuperada en tiempo real ante abandonos o cancelaciones.
- **Vigencia:** Vigente.

### DEC-03: Política de Reembolso Calculada Estrictamente sobre el Monto Efectivamente Pagado (`paid_amount`)

- **Contexto:** Dado que el hotel permite confirmar reservas abonando el 50% o el 100% del valor total, era indispensable definir con precisión la base de cálculo de los reembolsos por cancelación.
- **Decisión tomada:** Estipular tanto en el código (`BookingService.getReservationDetailsByCode` y `BookingService.cancelBooking`) como en toda la documentación que los porcentajes de devolución (`100%` con más de 72 horas de anticipación, `50%` entre 24 y 72 horas, y `0%` con menos de 24 horas) se aplican **exclusivamente sobre el monto que el cliente haya pagado realmente (`paid_amount`)**, nunca sobre el valor total pactado de la reserva si solo abonó una parte.
- **Alternativas descartadas:** Calcular el reembolso estimado sobre el precio total de la reserva (`totalPrice`), lo cual generaba valores de devolución superiores o incongruentes frente a lo realmente desembolsado por un huésped con abono del 50%.
- **Consecuencias:** Transparencia contable total para el hotel y para el huésped tanto al consultar los detalles de su reserva como al ejecutar la cancelación.
- **Vigencia:** Vigente.

### DEC-04: Base de 9 Habitaciones de Referencia, Administración CRUD por el Administrador y Eventos Especiales

- **Contexto:** El hotel cuenta con **9 habitaciones** de referencia, pero sus descripciones comerciales y tarifas definitivas aún están siendo consolidadas por el cliente (actualmente se emplean datos de prueba). Además, en la reunión con el cliente ([`ReunionCliente.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/Reuniones/ReunionCliente.md)) se solicitó flexibilidad para modificar habitaciones y ofrecer promociones en fechas especiales.
- **Decisión tomada:**
  1. Estandarizar las **9 habitaciones de referencia** (`101`–`103`, `201`–`203`, `301`–`303`) en las semillas de base de datos, documentación y modelo presupuestal.
  2. Incluir en el diseño de la aplicación web y de la API un módulo exclusivo para el **Administrador** que permita **crear, editar (precio por noche, capacidad de personas, descripción, permiso de mascotas, estado) y eliminar habitaciones**, con la regla estricta de que **solo se puede eliminar una habitación si no tiene reservas pendientes o activas**.
  3. Incluir un módulo de **eventos especiales y descuentos por temporada** donde el Administrador defina rangos de fechas y porcentajes de descuento que se apliquen automáticamente en las cotizaciones por WhatsApp y recepción.
- **Alternativas descartadas:** Mantener las habitaciones y tarifas fijas en archivos SQL de migración, lo que obligaría a intervenir el código fuente cada vez que el hotel cambie sus precios o descripciones.
- **Consecuencias:** El proyecto avanza sin bloqueos usando las 9 habitaciones de referencia con datos de prueba, y el cliente tendrá autonomía total desde la aplicación web para actualizar su catálogo real y lanzar campañas de descuento.
- **Vigencia:** Vigente.

### DEC-05: Unificación Documental en `EstadoActual.md` y `CambiosPendientes.md` y Redacción Orientada al Cliente

- **Contexto:** Necesidad de evitar duplicidades entre múltiples archivos de estado y asegurar que toda la documentación técnica/funcional pueda entregarse directamente al cliente sin jerga de programación ni códigos internos.
- **Decisión tomada:**
  1. Concentrar todo el estado de implementación, historial de cambios y decisiones en [`docs/modulos/EstadoActual.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/EstadoActual.md) y los cambios pendientes de envío en [`docs/CambiosPendientes.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/CambiosPendientes.md) (prohibiendo crear `PROJECT_STATE.md`, `PROJECT_CHANGELOG.md` o `PROJECT_DECISIONS.md`).
  2. Redactar todos los demás documentos (`README.md`, `docs/README.md`, `docs/modulos/*`, `docs/Diagramas/*`, `docs/Presupuesto/*`) como documentos comprensibles para el cliente que explican cómo debe funcionar el sistema completo, usando el formato `Concepto en español : "identificador_tecnico"` solo cuando es indispensable citar un nombre técnico.
- **Alternativas descartadas:** Mezclar el estado de avance parcial dentro de cada documento de módulo o mantener fragmentos de código Java/SQL en los manuales de los módulos.
- **Consecuencias:** Separación limpia entre las especificaciones del producto para el cliente y el control técnico de avance del proyecto.
- **Vigencia:** Vigente.

---

## 6. Fechas de Control

- **Fecha de la última revisión integral:** `2026-11-03`
- **Fecha del último punto de control:** `2026-11-03`
