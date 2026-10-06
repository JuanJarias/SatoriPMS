# Módulo — Estado Actual del Proyecto

> Este módulo es el único lugar del proyecto donde se documenta el avance real: qué está construido, qué falta y qué decisiones se han tomado. El resto de los módulos describen el sistema tal como está diseñado, sin notas de progreso.

---

### 1. Resumen General del Estado

| Área | Estado | Detalle |
|---|---|---|
| **Reserva guiada por WhatsApp** | ✅ Implementada | Flujo completo paso a paso: fechas, selección multi-habitación, bloqueo temporal en Redis (15 min), huéspedes, datos del titular, mascota, acompañantes (cantidad exacta), resumen y confirmación. Persistencia en PostgreSQL por lote (`V6_ChatbotReservas.json`). |
| **Revisar o Cancelar reserva** | ✅ Implementada | Búsqueda por código de 8 caracteres o UUID; presentación de detalles de reserva sin estados internos de habitación; cálculo automático de política de reembolso (RN-03); doble confirmación; cancelación en base de datos con liberación inmediata de habitaciones. |
| **Escalamiento a recepcionista** | ⚠️ Parcialmente implementado | Silenciamiento automático del bot mediante `agent_active = true` en Redis. Falta el panel en la app web para marcar la conversación como resuelta. |
| **Reserva asistida por IA** | ⚠️ Diseñada | La IA (Gemini 2.0 Flash) actúa como capa de normalización de lenguaje natural en el flujo guiado (interpreta respuestas flexibles). Falta construir el subflujo 100% autónomo donde el huésped describe su reserva en un único mensaje libre. |
| **Reseñas (chatbot y web)** | ❌ Pendiente | Falta migrar `ReviewController` de datos en memoria a persistencia real en base de datos (`ReviewRepository` JPA). |
| **Integración de pagos (MercadoPago)** | ❌ Pendiente | El flujo V6 crea la reserva en estado `pending_payment`. Falta añadir el nodo de creación de preferencia de pago y el webhook de confirmación. |
| **Backend API** | ✅ Funcional (core) | Endpoints implementados y probados: disponibilidad, bloqueo temporal, confirmación de reservas (batch), consulta por código de grupo, cancelación con reembolso. Falta: login/JWT, notificaciones, gestión de habitaciones (CRUD), reseñas persistidas. |
| **Base de datos** | ✅ Implementada | PostgreSQL 16 con extensión `btree_gist`, 4 migraciones Flyway y restricción excluyente anti-doble reserva. |
| **Infraestructura y Scripts** | ✅ Implementada | `start-dev.sh` optimizado: compilación rápida con Maven en el host (~3s) y Docker Compose para Postgres, Redis, n8n y API. Sin automatización de túneles. |
| **Aplicación web** | ⚠️ En desarrollo | Vista `ReservasDebug.tsx` conectada a la base de datos real con polling en tiempo real y creación de reservas desde formulario. Falta: diseño UX/UI final, calendario interactivo, check-in/out, tienda, finanzas y demás módulos. |
| **Tienda y Finanzas** | ❌ Pendiente | Tablas creadas en el esquema inicial; endpoints y vistas planificados para sprints 3 y 4. |

---

### 2. Problemas Resueltos Recientemente (Sprint 2)

1. **Auto-bloqueo al confirmar reserva (Backend):** Corregido en `BookingService` para verificar colisiones reales vía SQL y validar el `lockToken` en Redis, sin interferir con el propio lock del usuario.
2. **Error 403 en confirmación de reservas (n8n → API):** Corregido error de sintaxis (coma sobrante) en `SecurityConfig.java` que impedía la compilación y mantenía activos los rechazos de seguridad.
3. **Serialización doble de payload en n8n:** El nodo `API Confirmar Reserva` enviaba `JSON.stringify(...)` como string en lugar del objeto JSON real; corregido para enviar el objeto directamente.
4. **Filtro de nombres cortos en acompañantes:** Ajustado `filter(n => n.length > 0)` (antes `> 2`) para admitir nombres cortos e iniciales sin relajar la exigencia de cantidad exacta.
5. **Modelo de Gemini inexistente:** URL corregida de `gemini-3.8-flash` (404) a `gemini-2.0-flash`.
6. **Demora en compilación Docker:** Rediseñado el pipeline en `start-dev.sh` y `Dockerfile` para compilar el JAR con Maven local en ~3 segundos.
7. **Subflujo de Consulta y Cancelación en V6:** Implementados los endpoints `GET /api/bookings/group/{code}` y `POST /api/bookings/group/{code}/cancellation` con política de reembolso (RN-03), y el subflujo conversacional completo con doble confirmación.
8. **Constraint de `payment_status`:** Identificado que PostgreSQL solo acepta `pending`, `paid`, `refunded`, `partial`. Corregido el service para no usar valores fuera de ese `CHECK`.

---

### 3. Pendiente de Implementación (Prioridades)

- **Sprint 2 (actual):**
  - Integración de la pasarela de pago MercadoPago Sandbox en el flujo V6 (crear preferencia, webhook de confirmación, recibos).
- **Sprint 3:**
  - Panel de habitaciones/calendario en tiempo real.
  - Check-in y check-out desde la aplicación web.
  - Diseño UX/UI con Tailwind CSS configurado.
  - Canal WebSocket STOMP para actualizaciones en tiempo real.
- **Sprint 4:**
  - Persistencia real de reseñas (`ReviewRepository` JPA).
  - Módulo de tienda e inventario (endpoints + vistas).
  - Módulo de finanzas y reportes.
  - Gestión de roles y auditoría (login JWT, tabla de auditoría).
  - Aviso explícito de finalidad y autorización de datos personales en el chatbot (Ley 1581).
  - Subflujo autónomo de reserva asistida por IA (Módulo 2.4 completo).

---

### 4. Deuda Técnica Conocida

- `ReviewController.java` usa datos mock en memoria — necesita entidad JPA y repositorio real.
- `ChatbotController.java` está completamente vacío.
- `ConversationController` escalación retorna stub vacío; falta endpoint `/api/notifications/agent-request`.
- `Calendario.tsx` es una página huérfana sin ruta asignada en el router.
- El nodo `H Confirmar Bloqueo` (singular) quedó huérfano en V5/V6 tras migrar a `H Confirmar Bloqueos` (plural).
- Falta agregar validación de la firma de los mensajes entrantes de WhatsApp y evitar duplicados.
- El panel de conversaciones de la app web usa clases Tailwind sin configuración activa de Tailwind.
