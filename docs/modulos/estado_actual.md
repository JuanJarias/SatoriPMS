# Módulo — Estado Actual del Proyecto

> Este módulo es el único lugar del proyecto donde se documenta el avance real: qué está construido, qué falta y qué decisiones se han tomado. El resto de los módulos describen el sistema tal como está diseñado, sin notas de progreso.

---

### 1. Resumen General del Estado

| Área | Estado | Detalle |
|---|---|---|
| **Reserva guiada por WhatsApp (CU-01)** | ✅ Implementada y Probada | Flujo completo paso a paso con opción de abono (50% anticipo `partial` o 100% total `paid`), bloqueo temporal en Redis (15 min), validación de capacidad, titular, documento, acompañantes exactos y confirmación en PostgreSQL con columna `paid_amount` (`V8_ChatbotReservas.json`). |
| **Revisar o Cancelar reserva (CU-02)** | ✅ Implementada y Probada | Búsqueda por código de 8 caracteres o UUID. Muestra total, pagado a la fecha y saldo pendiente. Si tiene saldo pendiente, permite **pagar el saldo restante** (`POST /api/bookings/group/{code}/pay-remaining`) actualizando a `paid`. Permite cancelar con cálculo de política de reembolso (RN-03) proporcional al monto abonado (`paid_amount`) y doble confirmación. |
| **Reserva asistida por IA (HU-09)** | ✅ Implementada y Probada | Subflujo 100% autónomo en V8 con Google Gemini Flash Lite (`gemini-flash-lite-latest` / `gemini-3.5-flash-lite`). Extrae fechas, huéspedes, titular y documento desde lenguaje natural en un solo mensaje, valida disponibilidad real en backend, genera bloqueo de 15 min en Redis, ofrece pago 50%/100% y confirma la reserva en PostgreSQL. |
| **Reseñas (HU-02, HU-04)** | ✅ Implementada y Probada | Persistencia real en PostgreSQL (`review` table) mediante JPA `Review` y `ReviewRepository`. La opción 3 consulta las últimas reseñas con promedio de estrellas. La opción 4 captura calificación (1-5) y comentario, guarda en base de datos (`POST /api/reviews`) y entrega el enlace directo oficial de Google Maps / Business para publicación pública (`https://search.google.com/local/writereview?placeid=...`). |
| **Escalamiento a recepcionista (HU-06)** | ✅ Implementada y Probada | Silenciamiento automático del bot mediante `agent_active = true` en Redis (`session:{waId}`). Presenta horario de atención. Desactivación y retorno al menú mediante palabras clave (`"menú"`, `"inicio"`). |
| **Backend API** | ✅ Funcional y Probada | Endpoints core implementados y verificados: disponibilidad, bloqueo temporal, confirmación batch con abono parcial/total, consulta por código de grupo, cancelación con reembolso proporcional, pago de saldo pendiente (`/pay-remaining`), listado y creación de reseñas persistidas (`/api/reviews`). |
| **Base de datos** | ✅ Implementada | PostgreSQL 16 con extensión `btree_gist`, 5 migraciones Flyway (`V1` a `V5`) y restricción excluyente anti-doble reserva (`EXCLUDE`). |
| **Infraestructura y Orquestación** | ✅ Implementada | Docker Compose con PostgreSQL, Redis, n8n y API Spring Boot. Flujo activo en n8n: `V8_ChatbotReservas.json` (80 nodos, 0 enlaces rotos, 0 nodos huérfanos). |
| **Integración de pasarela de pago (MercadoPago)** | ⏸️ Excluida temporalmente | Excluida expresamente por instrucción del usuario para esta fase. El flujo simula y registra con precisión los estados `paid` y `partial` en backend. |
| **Aplicación web** | ⚠️ En desarrollo | Vista `ReservasDebug.tsx` conectada a la base de datos real con polling en tiempo real y creación de reservas desde formulario. Falta: diseño UX/UI final, calendario interactivo, check-in/out, tienda, finanzas y demás módulos. |
| **Tienda y Finanzas** | ❌ Pendiente | Tablas creadas en el esquema inicial; endpoints y vistas planificados para sprints 3 y 4. |

---

### 2. Problemas Resueltos Recientemente (Sprint 2 / V8)

1. **Soporte de Pago Parcial (50%) o Total (100%):** Agregada columna `paid_amount` en PostgreSQL (migración Flyway `V5`), actualizada entidad `Booking`, `BookingService`, y n8n para registrar si el huésped abonó la mitad o el total.
2. **Pago de Saldo Restante en Revisar Reserva:** Creado endpoint `POST /api/bookings/group/{code}/pay-remaining` en `BookingController` y `BookingService`. En el chatbot (V8), al consultar una reserva con saldo pendiente, el usuario puede seleccionar la opción 1 para liquidar el saldo pendiente a `$0.00`.
3. **Reembolsos de Cancelación basados en Monto Abonado:** Corregido el cálculo de devolución en `BookingService.cancelReservationGroupByCode` para calcular el porcentaje de reembolso sobre `paid_amount` (lo efectivamente pagado) y no sobre el valor total de la reserva.
4. **Persistencia Real de Reseñas:** Eliminada la lista mock en memoria de `ReviewController`. Creada entidad JPA `Review`, repositorio `ReviewRepository`, migración Flyway `V5` con columnas `source` y `author_name`, y soporte para reseñas desde Chatbot y Google.
5. **Redirección a Reseñas de Google:** Al registrar una reseña desde el chatbot, se almacena en PostgreSQL y se provee al usuario el enlace de redirección oficial (`https://search.google.com/local/writereview?placeid=${GOOGLE_PLACE_ID}`) para publicar la opinión en Google Maps.
6. **Subflujo Autónomo de Asistente IA (HU-09):** Construido el subflujo completo en n8n con `Gemini Asistente IA`, `H Procesar Gemini IA`, `¿IA Fechas Válidas?`, `API Disponibilidad IA`, `H Mostrar Habitaciones IA`, `API Bloquear Habitación IA` y `H Resumen y Pago IA`.
7. **Modelo Gemini Retirado (404/503):** Identificado que Google retiró `gemini-2.0-flash` en la API. Actualizado a `gemini-flash-lite-latest` / `gemini-3.5-flash-lite`, respondiendo con HTTP 200 en extracción estructurada JSON.
8. **Sincronización de Pasos en Máquina de Estados:** Corregido bug crítico en nodos de normalización donde se leía `draft.step` en lugar de `session.step`, lo que causaba reseteos inesperados al menú tras seleccionar habitación.
9. **Integridad 100% en n8n V8:** Generado `V8_ChatbotReservas.json` con 80 nodos interconectados, verificado mediante script de grafos con 0 enlaces rotos, 0 nodos huérfanos y coincidencia estricta en todas las salidas de switches.

---

### 3. Pendiente de Implementación (Próximos Sprints)

- **Sprint 3 (Gestión Operativa y App Web):**
  - Panel de habitaciones y calendario interactivo en tiempo real.
  - Flujos operativos de Check-in (CU-03) y Check-out (CU-04) desde la web.
  - Diseño UX/UI definitivo con Tailwind CSS.
  - Canal WebSocket STOMP para sincronizar cambios entre backend y frontend.
- **Sprint 4 (Comercio y Administración):**
  - Pasarela de pagos MercadoPago Sandbox (webhook y links de pago).
  - Módulo de tienda y catálogo de inventario (CU-05, CU-07, HU-14).
  - Módulo de facturación, egresos y cálculo de sueldos (CU-06, HU-01, HU-07, HU-13).
  - Panel web de moderación de reseñas (HU-10) y fidelización de huéspedes recurrentes (HU-12).
  - Gestión de roles de usuario, login con JWT y tabla de auditoría (HU-05, HU-15).
  - Aviso explícito de autorización y finalidad de datos personales en el chatbot (Ley 1581).

---

### 4. Deuda Técnica Conocida

- `ChatbotController.java` está vacío en el backend (las operaciones de chatbot se canalizan por los controladores de booking y review).
- `ConversationController` retorno de escalación es un stub vacío; la gestión de estado de escalamiento reside actualmente en Redis.
- Falta agregar validación criptográfica de firma SHA-256 de los webhooks entrantes de Meta.
