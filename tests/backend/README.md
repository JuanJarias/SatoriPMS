# Pruebas del Servidor Central (Backend) — Torre Satori

Este directorio contiene la suite automatizada de pruebas del servidor central de **SatoriPMS** (Python 3.12 / FastAPI / PostgreSQL 16). Cada prueba llama a la API directamente y trabaja sobre una base de datos PostgreSQL real, sin simulaciones de la base de datos, para comprobar las reglas del negocio tal como se ejecutan en producción.

Su propósito es garantizar que la prevención de sobreventas, la seguridad de los datos del huésped, el cálculo de precios y reembolsos, la confirmación de pagos y las operaciones del panel web se mantengan correctos con cada cambio. Las pruebas del asistente de WhatsApp (flujos de n8n) están en [tests/chatbot/](../chatbot/README.md).

---

## Estructura del Directorio

```text
tests/backend/
├── conftest.py                      # Prepara la base aislada satoripms_test y aplica las migraciones de Alembic
├── test_seguridad_y_precios.py      # Documento del titular, código TS-XXXX, pago externo y precios por noche (11 pruebas)
├── test_n8n_integration.py          # Recorrido completo del chatbot contra la API y sesiones en PostgreSQL (3 pruebas)
├── test_booking_lock.py             # Bloqueo temporal de 15 minutos, expiración y canal SSE (4 pruebas)
├── test_concurrency_rn02.py         # Restricción contra sobreventa (EXCLUDE GiST) con solicitudes simultáneas (3 pruebas)
├── test_rooms_availability.py       # Disponibilidad, capacidad y recargo por persona adicional (2 pruebas)
├── test_payment_webhook.py          # Webhook de pago con firma, idempotencia y enlace de Wompi (3 pruebas)
├── test_auth.py                     # Inicio de sesión, JWT y permisos por rol (3 pruebas)
├── test_web_operations.py           # Check-in/out, habitaciones, cafetería, tienda, egresos y Excel (5 pruebas)
└── test_health.py                   # Salud del servicio, extensión btree_gist y 9 habitaciones (2 pruebas)
```

En total son **36 pruebas**. La configuración global está en [pytest.ini](../../pytest.ini) en la raíz del repositorio.

---

## Tecnologías y Estándares

| Tecnología / Herramienta | Rol en Pruebas | Versión / Estándar |
| :--- | :--- | :--- |
| pytest | Ejecutor de la suite | >= 8.3 |
| pytest-asyncio | Pruebas de funciones asíncronas (`asyncio_mode = auto`) | >= 0.24 |
| httpx (`ASGITransport`) | Cliente HTTP que llama a la aplicación FastAPI en memoria | >= 0.27 |
| PostgreSQL | Base de datos real de pruebas con extensión `btree_gist` | 16 |
| Alembic | Aplica el esquema completo antes de ejecutar los casos | >= 1.14 |
| Python | Lenguaje de la suite | >= 3.12 |

---

## Arquitectura de Pruebas

Las pruebas importan la aplicación FastAPI y la invocan por HTTP sin abrir un puerto de red. Antes de ejecutar el primer caso, `conftest.py` prepara la base de datos:

```mermaid
flowchart TD
    Inicio["pytest"] --> Conf["conftest.py<br/>pytest_configure"]
    Conf --> Url["Construye DATABASE_URL<br/>con el nombre terminado en _test"]
    Url --> Crea["pytest_sessionstart<br/>Crea satoripms_test si no existe"]
    Crea --> Mig["alembic upgrade head<br/>Esquema 001 a 005"]
    Mig --> Casos["Casos de prueba<br/>httpx + FastAPI + PostgreSQL"]
    Casos --> Reglas["Reglas verificadas:<br/>RN-01 capacidad, RN-02 sobreventa,<br/>RN-03 reembolso, RN-12 consentimiento"]
```

**Protección de los datos reales:** la suite se niega a ejecutarse si el nombre de la base no termina en `_test`. Si `DATABASE_URL` apunta a `satoripms`, las pruebas usan `satoripms_test`; también se puede indicar otra con `TEST_DATABASE_URL`. Los datos operativos nunca se tocan.

---

## Catálogo Detallado de Pruebas (36 Casos)

### Seguridad y precios (`test_seguridad_y_precios.py`)
Reglas de seguridad del chatbot y cálculo de tarifas con eventos especiales.

- **Sin eventos:** cada noche mantiene la tarifa base.
- **Recargo por noche:** un evento con recargo solo afecta a las noches que caen dentro de sus fechas.
- **Descuento y fecha de fin inclusiva:** la última fecha del evento también recibe el descuento.
- **Eventos superpuestos:** sus porcentajes se suman y los eventos inactivos se ignoran.
- **Piso en cero:** el precio de una noche nunca baja de cero.
- **Código `TS-XXXX`:** aleatorio, sin los caracteres `0`, `O`, `1` ni `I`.
- **Documento del titular:** sin documento responde 400; con documento equivocado responde 404 idéntico a "no existe"; con el correcto la cédula sale enmascarada (`******5666`); un prefijo del código no encuentra nada.
- **Pago externo:** confirma la reserva pendiente con el 50% o el 100%, es idempotente por transacción y exige llave de servicio o administrador.
- **Retención de la habitación:** una reserva `PENDIENTE_PAGO` impide que otro usuario bloquee las mismas fechas.
- **Eventos sobre la cotización y la reserva:** el total se ajusta noche por noche.
- **Listado de monitoreo:** `GET /api/bookings/debug` usa los estados del contrato de n8n y exige autenticación.

### Flujo completo del chatbot (`test_n8n_integration.py`)
- **Sesiones en PostgreSQL:** guardar, leer y borrar la sesión de una conversación y escalar a un agente humano.
- **Ciclo de vida de una reserva:** disponibilidad, bloqueo, reserva pendiente, pago aprobado (50%), consulta con documento, pago del saldo y cancelación con reembolso del 100% (regla RN-03).
- **Flujo V10 sin Redis:** verifica que `flows/n8n/V10_ChatbotReservas.json` no tenga nodos Redis y use las rutas de sesión de la API.

### Bloqueo temporal y sobreventa (`test_booking_lock.py`, `test_concurrency_rn02.py`)
- **Validaciones al bloquear:** consentimiento de datos personales (RN-12) y capacidad máxima (RN-01).
- **Expiración atómica:** un bloqueo vencido se marca como expirado y se crea el nuevo de 15 minutos.
- **Diez solicitudes simultáneas:** una obtiene el bloqueo (200) y nueve reciben conflicto (409).
- **Programador de expiración y canal SSE:** el lote de expiración funciona y el canal de eventos exige autenticación.
- **Restricción GiST (RN-02):** rechaza reservas activas con fechas cruzadas, permite fechas contiguas y estados inactivos, y con solicitudes concurrentes solo una prospera.

### Disponibilidad (`test_rooms_availability.py`)
- **Recargo por persona adicional y filtro de capacidad (RN-01).**
- **Bloqueos:** un bloqueo vigente oculta la habitación; uno vencido se ignora.

### Pagos (`test_payment_webhook.py`)
- **Firma inválida o ausente:** responde 401.
- **Firma válida:** confirma la reserva y un segundo aviso idéntico no se procesa de nuevo.
- **Checksum de Wompi y enlace de pago de prueba.**

### Autenticación (`test_auth.py`)
- **Inicio de sesión correcto:** entrega un JWT y deja registro en la bitácora de auditoría.
- **Credenciales incorrectas o token alterado:** responde 401.
- **Recepcionista en una función de administrador:** responde 403.

### Operaciones del panel web (`test_web_operations.py`)
- **Reserva manual, check-in y check-out** con auditoría.
- **Habitaciones:** alta, edición, número editable sin colisiones y protección al eliminar una habitación con reservas activas.
- **Cafetería, folio y eventos:** comanda a la habitación y eventos especiales.
- **Tienda, egresos, usuarios, reseñas de Google y exportación a Excel.**

### Salud (`test_health.py`)
- **Endpoint de salud** con base de datos conectada.
- **Extensión `btree_gist`** instalada y las 9 habitaciones cargadas.

---

## Guía de Ejecución

**Requisitos:** PostgreSQL 16 en marcha (por ejemplo con `./scripts/start-dev.sh --no-frontend` o `docker compose up -d postgres`) y las dependencias de Python instaladas:

```bash
python3 -m venv .venv
.venv/bin/pip install -r apps/api/requirements.txt
```

**Variable de entorno:** `DATABASE_URL` debe tener el formato `postgresql+psycopg://usuario:clave@localhost:5432/satoripms`. No sirve el formato `jdbc:postgresql://...` del servidor Java anterior. Si la variable no está definida, se lee del archivo `.env` de la raíz y, a falta de ambos, se usa el valor de desarrollo.

```bash
# Toda la suite (desde la raíz del repositorio)
.venv/bin/pytest

# Un archivo o una prueba concreta
.venv/bin/pytest tests/backend/test_seguridad_y_precios.py -v
.venv/bin/pytest tests/backend/test_auth.py::test_login_success_returns_jwt_and_records_audit

# Con otra base de datos de pruebas
TEST_DATABASE_URL=postgresql+psycopg://satori:satori_dev@localhost:5432/otra_test .venv/bin/pytest
```

El proceso termina con código distinto de cero si alguna prueba falla, por lo que sirve directamente en integración continua.

---

## Políticas y Reglas del Negocio Validadas

1. **Cero sobreventas (RN-02):** la restricción `EXCLUDE USING gist` de PostgreSQL impide dos reservas activas con fechas cruzadas para una habitación, incluso con solicitudes simultáneas. Los estados que retienen la habitación son `BLOQUEADA_TEMPORAL`, `PENDIENTE_PAGO`, `CONFIRMADA` y `EN_CURSO`.
2. **Bloqueo de 15 minutos:** el bloqueo temporal es una fila con vencimiento; los bloqueos vencidos se ignoran en la disponibilidad y se expiran atómicamente.
3. **Reembolso sobre lo abonado (RN-03):** más de 72 horas antes del ingreso, 100%; entre 24 y 72 horas, 50%; menos de 24 horas, 0%, siempre sobre el monto efectivamente pagado.
4. **Reserva firme solo con pago aprobado:** el chatbot deja la reserva en `PENDIENTE_PAGO` y únicamente el pago aprobado de la pasarela la confirma.
5. **Protección de datos del huésped:** el chatbot debe presentar código y documento del titular; ante un documento incorrecto no se revela si la reserva existe, y el documento nunca se devuelve completo.
6. **Precios por noche (provisional, pendiente de confirmar con el cliente):** descuentos y recargos de eventos especiales se aplican noche por noche.

---

## Integración Continua

El flujo de GitHub Actions (`.github/workflows/ci.yml`) ejecuta `pytest` en el trabajo de backend con un PostgreSQL 16 efímero, junto con la compilación de la web y las pruebas del chatbot que no necesitan servicios.
