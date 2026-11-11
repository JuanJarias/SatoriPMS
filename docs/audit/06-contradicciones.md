# Matriz de Contradicciones y Reglas de Negocio (Fase 1 - Cierre de Decisiones)

**Fecha de actualización:** 2026-11-10  
**Rama:** `migracion-fastapi`  
**Fuentes comparadas:** Contexto oficial del curso (fuente de verdad), repositorio en rama `migracion-fastapi`, tag de respaldo `legacy-java-backup` y tablero de GitHub Projects (`gh project item-list 2`, `gh issue list`).

---

## 1. Tabla de Contradicciones y Decisiones de Arquitectura

| Tema | Contexto Oficial | Repo Legado / Tablero | Estado | Decisión y Aplicación |
| :--- | :--- | :--- | :---: | :--- |
| **Estados canónicos de reserva** | Estados activos: `BLOQUEADA_TEMPORAL`, `CONFIRMADA`, `EN_CURSO`; terminales: `EXPIRADA`, `CANCELADA`. | Repo y frontend usaban minúsculas en inglés (`pending_payment`, `confirmed`, etc.). | **Resuelta** | Estados canónicos en base de datos en mayúsculas en español (`BLOQUEADA_TEMPORAL`, `CONFIRMADA`, `EN_CURSO`, `EXPIRADA`, `CANCELADA`). El frontend React conserva una única capa de mapeo/traducción. Aplicada en `AGENTS.md:13` y `05-plan-migracion.md` (M0, M2). |
| **Mecanismo de Bloqueo Temporal (RN-02)** | `EXCLUDE USING gist` sobre `room_id + daterange` para estados activos. Bloqueo 15 min; disponibilidad ignora vencidos. | En código legado se usaba Redis con TTL de 900s (`RedisLockService.java`). | **Resuelta** | El candado vive como una fila en la tabla `booking` con estado `BLOQUEADA_TEMPORAL` y columna `expires_at`, protegida por `EXCLUDE USING gist`. Antes de insertar, se expiran en la misma transacción los bloqueos vencidos de esa habitación. Aplicada en `AGENTS.md:14` y `05-plan-migracion.md` (M0, M2). |
| **Persistencia de Sesión del Chatbot (n8n)** | n8n solo es adaptador; contexto conversacional en FastAPI/PostgreSQL, no en Redis. | El flujo `V8_ChatbotReservas.json` usaba 5 nodos de Redis. | **Resuelta** | n8n opera sin Redis; la sesión conversacional se almacena en FastAPI/PostgreSQL (tabla `conversation`). Los flujos n8n se adaptan en M3 con llamadas HTTP directas a FastAPI (camino feliz). Aplicada en `AGENTS.md:10`, `03-limpieza.md` y `05-plan-migracion.md` (M3). |
| **Confirmación de Reserva y Pasarela de Pagos** | Solo se confirma con webhook de pago validado (`X-Hub-Signature-256`). Pasarela por definir. | `POST /api/bookings/confirm` confirmaba directo; web tenía botón de confirmación sin pasarela. | **Resuelta** | Recepción confirma manualmente en sitio con registro inmutable en auditoría. El chatbot confirma exclusivamente con webhook validado por firma HMAC `X-Hub-Signature-256` e idempotencia. Pasarela tras interfaz con mock sandbox (Wompi/MercadoPago por definir). Aplicada en `AGENTS.md:15` y `05-plan-migracion.md` (M3, M4). |
| **Ítems "Done" en el tablero que no existen en código real** | Progreso en FastAPI inicia en 0% para el backend. | Issues `#29`, `#35`, etc., estaban "Done" pero correspondían a Java. | **Resuelta** | Se **REUTILIZAN y reubican las tarjetas existentes** en el tablero con la etiqueta `portar-python`, evitando duplicar tarjetas innecesarias. Aplicada en `AGENTS.md:16` y `05-plan-migracion.md`. |
| **Estructura y Nomenclatura de Épicas** | 6 épicas: E1 Reservas/Chatbot, E2 Operación web, E3 Finanzas, E4 Tienda, E5 Reseñas, E6 Roles. | Tablero mezclaba hitos antiguos (`DU`, `Épica 1` fusionada). | **Resuelta** | Se adopta formalmente el estándar E1 a E6 en todas las especificaciones y se sincronizarán las etiquetas de las tarjetas reutilizadas en el tablero. Aplicada en `AGENTS.md:5` y `05-plan-migracion.md:1.1`. |
| **Desviación de lenguaje en Frontend (TS vs. JS)** | Documentos decían JS; el repo está en React 18 + Vite con TypeScript. | `apps/web` usa TypeScript 5.0 con compilación limpia (`tsc`). | **Resuelta** | Desviación ratificada y aceptada formalmente: se conserva TypeScript en `apps/web`. Aplicada en `AGENTS.md:4` y `04-conservar.md`. |
| **Fórmula de Sueldo de Recepcionista (HU-07 / RN-11)** | "Fórmula de sueldo: PENDIENTE DE DEFINIR (no asumir)". | Issue `#45` no especifica porcentajes ni fórmulas. | **Pendiente** | **Qué necesito de mí:** Definición formal con el stakeholder de la fórmula salarial (base fija, comisión o mixto) y periodicidad de corte. El módulo queda fuera de Sprint 5 (reubicado en Backlog v1.1). |
| **Descuentos y Beneficios de Fidelización (HU-12)** | "Descuentos (configurables en base de datos): PENDIENTE DE DEFINIR". | Issue `#47` sin reglas claras ni porcentajes. | **Pendiente** | **Qué necesito de mí:** Definición del esquema y porcentaje de descuentos para huéspedes recurrentes. El módulo queda fuera de Sprint 5 (reubicado en Backlog v1.1). |
| **Tiempo Real para Calendario de Ocupación** | SSE o WebSocket para calendario (HU-03). | Código Java tenía WebSocket STOMP; web hacía polling cada 5s. | **Resuelta** | Se usará Server-Sent Events (SSE). Para el frontend de Sprint 5 se mantiene inicialmente polling con TanStack Query y se añade el endpoint SSE como tarea P2 (`05-plan-migracion.md` M5c). Aplicada en `AGENTS.md:17`. |
| **Regla de No-Show a las 12:00 (RN-13 previa)** | No verificada; ausente de RN oficiales (RN-01..04). | Figuraba en AGENTS.md viejo; sin issue en GitHub. | **Resuelta** | Excluida formalmente y fuera de alcance. La cancelación por no-show es potestad de recepción para no perjudicar a viajeros demorados en carretera. Aplicada en `AGENTS.md:17` y `05-plan-migracion.md:1.3`. |
| **Datos Obligatorios de Huésped y Retención (Ley 1581)** | "Datos obligatorios, conservación: PENDIENTE DE DEFINIR (no asumir)". | Modelos solicitaban nombre, cédula y teléfono. | **Pendiente** | **Qué necesito de mí:** Validación final de la lista de campos legalmente requeridos para registro hotelero y plazo de retención. En código P1 se aplica el principio de datos mínimos y flag booleano de autorización. |

---

## 2. Tabla de Reglas de Negocio (RN) y Asignación de Lotes

| RN | Descripción | Fuente | Épica | Estado | Decisión y Asignación |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **RN-01** | Capacidad máxima de habitación (9 habs) y cálculo proporcional de recargo por persona adicional. | Oficial / Issues `#76`, `#74` | E1 Reservas | **Resuelta** | P1 (Lote M2): Validación en modelos Pydantic y lógica de cotización de habitaciones. |
| **RN-02** | Bloqueo temporal atómico de 15 min en DB + `EXCLUDE USING gist` sobre `room_id + daterange` para estados activos. | Oficial / Issues `#75`, `#30`, `#83` | E1 Reservas | **Resuelta** | P1 (Lotes M0, M2): Constraint GiST en PostgreSQL 16 y expiración atómica en misma transacción. Disponibilidad ignora expirados inline. |
| **RN-03** | Política de reembolso proporcional en cancelaciones (>72h: 100%, 24-72h: 50%, <24h: 0%). | Oficial / Issues `#35`, `#36` | E1 / E3 | **Resuelta** | P2 (Lote M5a): Algoritmo puro de liquidación de reembolsos portado si hay margen de tiempo. |
| **RN-04** | Venta de tienda con control de stock sin saldo negativo y liquidación al check-out. | Oficial / Issues `#48`, `#56` | E4 Tienda | **Resuelta** | Fuera de alcance Sprint 5: Reubicada en Backlog v1.1. |
| **RN-05** | Liquidación de saldo restante (50%) garantizado antes de completar el check-out. | Tablero / Issue `#39` | E2 Operación web | **Resuelta** | P2 (Lote M5a / M4): Integración de cobro de saldo restante. |
| **RN-06** | Validación de check-in: solo huéspedes con reserva confirmada y fecha actual (transición a `EN_CURSO`). | Tablero / Issue `#34` | E2 Operación web | **Resuelta** | P1 (Lote M4): Botón de recepción con registro inmutable en auditoría. |
| **RN-07** | Beneficios y descuentos por fidelización para huéspedes recurrentes (HU-12). | Tablero / Issue `#47` | E5 Fidelización | **Pendiente** | **Qué necesito de mí:** Definición de porcentajes de descuento. Fuera de alcance Sprint 5 (v1.1). |
| **RN-08** | Cálculo automatizado de sueldo mensual (fijo, comisión, mixto) (HU-07). | Tablero / Issue `#45` | E3 Finanzas | **Pendiente** | **Qué necesito de mí:** Definición de fórmula salarial. Fuera de alcance Sprint 5 (v1.1). |
| **RN-09** | RBAC estricto: Recepcionista (operación diaria) vs. Administrador (tarifas, eventos, usuarios). | Tablero / Issue `#49` | E6 Roles | **Resuelta** | P1 (Lote M1): Autenticación JWT y dependencias `require_role` en FastAPI. |
| **RN-10** | Registro inmutable de auditoría (timestamp, actor, acción, entidad) para operaciones críticas. | Tablero / Issue `#59` | E6 Roles | **Resuelta** | P1 (Lote M1): Tabla `audit_log` en PostgreSQL con inserción en operaciones clave. |
| **RN-12** | Consentimiento informado de datos personales según Ley 1581 antes de persistir titular. | AGENTS.md / docs seguridad | E1 / E6 | **Resuelta** | P1 (Lote M2): Flag booleano obligatorio en formulario de huésped. |
| **RN-13** | Liberación automática No-Show a las 12:00 del mediodía. | AGENTS.md anterior | E2 Operación web | **Resuelta** | Descartada formalmente de común acuerdo por riesgo operativo al huésped. |

---

## 3. Resumen de Estados

* **Contradicciones de Arquitectura:** 9 Resueltas, 3 Pendientes de definición del stakeholder (Sueldo HU-07, Descuentos HU-12, Política retención Ley 1581).
* **Reglas de Negocio:** 10 Resueltas (asignadas a P1, P2 o descartadas formalmente), 2 Pendientes de fórmula (RN-07 y RN-08, diferidas a v1.1).
* **Total:** 19 Resueltas, 5 Pendientes. Ninguna fila quedó sin estado asignado.
