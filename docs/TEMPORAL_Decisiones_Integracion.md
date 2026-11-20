# Decisiones pendientes de la integración `migracion-fastapi` → `main`

> **Documento temporal.** Bórralo cuando se resuelvan los puntos. Está pensado para que lo revise el compañero que trabajó en `migracion-fastapi`.

## Qué se hizo

La rama `integracion-fastapi` se creó desde `main` y se le fusionó `migracion-fastapi` (PR #112). Los conflictos se resolvieron así:

- **Backend:** FastAPI reemplaza al Java. El Java sigue en el tag `legacy-java-backup`.
- **Web:** se tomó `apps/web` completa de `migracion-fastapi`. Solo se agregó una línea en `store.tsx` para mapear el estado nuevo `PENDIENTE_PAGO`.
- **Infraestructura:** `main` aportó los `scripts/` (start, stop, reset, status, sync-n8n-flow) y el CI, adaptados a FastAPI. `docker-compose.yml` ya no usa Maven ni Flyway.
- **Chatbot:** se conserva el flujo V9 de `main` con sus pruebas. Tu V10 (sesión en PostgreSQL) queda junto al V9.
- **Documentos:** los de `main` se reescribieron para FastAPI. Los de la Actividad 5 son los tuyos (11 de noviembre).

También se portaron al backend FastAPI las reglas de seguridad y precio que tenía el Java:

| Regla | Dónde |
|---|---|
| Documento del titular obligatorio para el chatbot (400 sin él, 404 si no coincide, cédula enmascarada) | `apps/api/routers/n8n_compat.py` |
| Código `TS-XXXX` aleatorio y único (antes salía de los últimos 4 caracteres del UUID) | `apps/api/services/payment_service.py` |
| Estado `PENDIENTE_PAGO`: la reserva del chatbot retiene la habitación hasta que Wompi aprueba el pago | migración `005`, `models/booking.py` |
| `confirm-external-payment` idempotente por transacción | `n8n_compat.py` |
| Eventos especiales aplicados noche por noche (descuento negativo = recargo) | `apps/api/services/pricing.py` |
| `GET /api/bookings/debug` con estados en inglés (contrato de n8n) | `n8n_compat.py` |

Verificación: `pytest` 36/36, suite del chatbot 65/65, y las 7 pruebas en vivo del chatbot contra FastAPI con n8n y Wompi reales.

## Decisiones que necesitamos de ti

### 1. ¿Qué hacemos con los archivos de tu rama que quedaron duplicados u obsoletos?

No se borró nada de lo tuyo. Propuesta (marca lo que estés de acuerdo en eliminar):

| Archivo | Motivo | Propuesta |
|---|---|---|
| `docs/Presentaciones/Actividad5_Transicion_Servicio.pdf` y `docs/Presentaciones/SatoriPMS_Actividad5_Presentacion.pdf` | Son el mismo PDF (5,8 MB) | Dejar uno |
| `docs/Presentaciones/Actividad5_Transicion_Servicio.html` | Mismo contenido que `index.html` de la raíz | Dejar uno |
| `docs/audit/03-limpieza.md`, `docs/audit/08-limpieza2.md` | Planes de limpieza que ya se ejecutaron | Borrar |
| `docs/audit/05-plan-migracion.md` | Plan de migración ya ejecutado | Archivar o borrar |
| `docs/audit/01`, `04`, `06`, `09`, `10`, `11`, `12` | Auditorías y estado de despliegue; son registros históricos | Conservar o archivar |
| `AGENTS.md` | Reglas para tu agente de IA (prohíbe Java y Redis, "push solo a `migracion-fastapi`", fecha 2026-11-10). Contradice el repositorio integrado | Borrar, o reescribir para el repo integrado |
| `docs/ROADMAP.md` | Sus enlaces `file:///home/jjarias/...` no abren en otros equipos | Corregir enlaces |
| `docs/CONTEXTO_PARA_IA_EXTERNA.md`, `docs/GUIA_TELEMATICA.md` | Guías escritas antes de la integración | Revisar y actualizar |
| `docs/legacy-ref/` | Migraciones Flyway, contratos Java y flujo V8; todo está en el tag `legacy-java-backup` | Borrar cuando estés de acuerdo |
| `docs/aprendizaje/*` | Notas por lote. `P1.md` enlaza a `db/seed/dev_seed.sql`, que ya no existe | Conservar; arreglar ese enlace |

### 2. Flujo n8n: ¿portamos tu V10 para poder quitar Redis?

- El **V9** (el de `main`) manda la llave de servicio y el documento del titular, revierte la reserva si falla el cobro y confirma el pago de Wompi. Guarda la sesión en **Redis**.
- Tu **V10** guarda la sesión en PostgreSQL (sin Redis), pero **no** tiene lo anterior.
- Hoy `docker-compose.yml` conserva Redis **solo para n8n**; la API no lo usa.

Propuesta: pasarle al V10 los cambios de seguridad, la reversión y el pago de Wompi del V9, probarlo, y entonces quitar Redis. ¿Quién lo hace y cuándo?

### 3. ¿Debe vencer una reserva `PENDIENTE_PAGO`?

Hoy retiene la habitación sin límite de tiempo (igual que hacía el Java). Si el huésped nunca paga, la habitación queda ocupada hasta que alguien la cancele. Opciones:
- Vencerla junto con el enlace de Wompi (24 horas).
- Dejarla sin vencimiento y que recepción la cancele a mano.

Si se elige vencerla, hay que ampliar el job de expiración, que hoy solo revisa `BLOQUEADA_TEMPORAL`.

### 4. Regla de eventos especiales por noche (por confirmar con el cliente)

Cada noche se multiplica por `1 − Σ descuentos + Σ recargos` de los eventos activos que la cubren (fechas inclusivas, mínimo 0). El recargo por persona adicional usa el promedio de las noches. La alternativa es aplicar el primer evento a toda la estadía. Hay que preguntarle al cliente cuál prefiere; el cambio está solo en `apps/api/services/pricing.py`.

### 5. Endpoints de WhatsApp para la web (siguen pendientes)

No existen: alternar el bot (`toggle-bot`), enviar mensajes manuales de recepción y el simulador de pruebas.

## Cosas a tener en cuenta al probar

- Si tu `.env` tiene `DATABASE_URL=jdbc:postgresql://...` (formato del Java), cámbialo a `postgresql+psycopg://...` para correr `pytest` o la API fuera de Docker.
- Una base de datos creada con el esquema del Java no sirve para FastAPI. Para empezar de cero: `./scripts/reset-dev.sh --start`.
- Las cuentas `admin / admin123` y `recepcion / recepcion123` de la migración `002` son **solo de desarrollo**.
- `GET /api/bookings/debug` devuelve documentos completos a quien tenga la llave de servicio. Es de uso interno y habría que retirarlo o limitarlo antes de producción.
- Las pruebas `test_cancelacion_reembolso.js` y `test_pago_saldo_restante.js` necesitan reservas existentes: en una base vacía, ejecuta antes `test_e2e_reserva_wompi_v9.js`.
