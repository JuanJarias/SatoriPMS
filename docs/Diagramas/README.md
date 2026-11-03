# Índice de Diagramas Técnicos y de Negocio — SatoriPMS

Esta carpeta centraliza los diagramas oficiales de arquitectura, infraestructura, flujos conversacionales, concurrencia y procesos operativos de **Torre Satori PMS**.

Todos los diagramas han sido elaborados en formato **Mermaid estándar**, optimizados con paleta de colores corporativos, tipografía clara, espaciado que evita solapamiento de texto y elementos visuales descriptivos.

---

## Catálogo de Diagramas

| # | Diagrama | Archivo | Propósito y Contenido |
|:---:|---|---|---|
| **01** | **Infraestructura y Servicios** | [`01_Infraestructura_Servicios.md`](01_Infraestructura_Servicios.md) | Topología de contenedores en Docker Compose, asignación de puertos (`:8080`, `:5173`, `:5678`, `:5432`, `:6379`), redes privadas aisladas, volúmenes persistentes y conexiones externas a Meta Cloud API, Google Gemini, Cloudflare y MercadoPago. |
| **02** | **Flujo Integral de Reserva por WhatsApp** | [`02_Flujo_Reserva_WhatsApp.md`](02_Flujo_Reserva_WhatsApp.md) | Secuencia paso a paso desde el primer mensaje del huésped, extracción estructurada con Google Gemini Flash Lite, consulta de disponibilidad, bloqueo temporal de 15 min, selección de abono (50% / 100%) y emisión del voucher digital. |
| **03** | **Concurrencia y Doble Candado Anti-Overbooking** | [`03_Concurrencia_Doble_Candado.md`](03_Concurrencia_Doble_Candado.md) | Detalle del mecanismo de dos niveles que erradica la sobreventa: Nivel 1 en memoria con `RedisLockService` (scripts Lua atómicos con TTL) y Nivel 2 en base de datos con la restricción física `EXCLUDE USING gist` en PostgreSQL 16. |
| **04** | **Gestión Operativa en Recepción (App Web & Sockets)** | [`04_Gestion_Operativa_Recepcion.md`](04_Gestion_Operativa_Recepcion.md) | Flujo operativo del personal del hotel en la aplicación React/Vite: sincronización en tiempo real vía WebSockets STOMP, check-in, cobro de saldos restantes (`/pay-remaining`), check-out y liquidación de consumos de tienda (RN-04). |
| **05** | **Máquina de Estados y Ciclo de Vida de la Reserva** | [`05_Ciclo_Vida_Reserva.md`](05_Ciclo_Vida_Reserva.md) | Modelo de estados de una reserva (`DRAFT_LOCK` $\rightarrow$ `CONFIRMED` $\rightarrow$ `CHECKED_IN` $\rightarrow$ `CHECKED_OUT`), con el desglose de reglas de cancelación y escalas de reembolso proporcional según la antelación (Regla de Negocio RN-03). |

---

## Convenciones de Visualización

* **Contenedores y Servicios Internos:** Agrupados en subgrafos con bordes distintivos y etiquetas técnicas (lenguaje, framework y puerto).
* **Flujos de Información:** Flechas etiquetadas indicando protocolo (REST JSON, WebSocket STOMP, TCP/IP Redis, SQL nativo).
* **Decisiones y Candados:** Rombos de evaluación condicional con salidas explícitas de éxito (verde) y conflicto/error (rojo).
