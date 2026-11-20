# Estructura de Datos (Base de Datos) — SatoriPMS

## 1. Propósito del Módulo

La **Base de Datos** de **SatoriPMS** resguarda toda la información comercial, operativa y contable de **Torre Satori** sobre el motor relacional **PostgreSQL 16**. Es también el único lugar donde viven los bloqueos temporales de habitaciones: el servidor central no usa Redis. Su diseño garantiza que los datos de habitaciones, eventos especiales, huéspedes, reservas, pagos, consumos, movimientos financieros y usuarios del personal se almacenen sin duplicidades, manteniendo el historial contable intacto.

---

## 2. Organización de la Información del Hotel

A continuación se describe qué información almacena cada tabla, con su nombre técnico en la base de datos:

### A. Catálogo de Habitaciones (`Habitaciones : "room"`)
Configuración comercial y operativa de cada habitación (referencia actual de **9 habitaciones**, numeradas del `"1"` al `"9"`, administrables desde la aplicación web):
- `Identificador único : "id"` y `Número de habitación : "number"` (único en el hotel).
- `Nombre comercial : "name"`, `Descripción : "description"` y `Tipo : "type"` (por ejemplo, Sencilla, Doble, Familiar, Suite).
- `Capacidad base de adultos : "base_adults_capacity"`: Personas cubiertas por la tarifa base por noche.
- `Capacidad máxima de adultos : "max_adults_capacity"` y `Capacidad de niños : "children_capacity"`.
- `Permitir mascotas : "allows_pets"`, `Precio base por noche : "price_per_night"` y `Precio por persona adicional : "extra_guest_price"`.
- `Estado operativo : "status"`: `available`, `occupied`, `cleaning` o `maintenance`. `Habitación activa : "active"`.
- **Regla de eliminación:** Solo el Administrador puede crear, editar o eliminar habitaciones, y no puede eliminar una con reservas activas.

### B. Eventos Especiales (`Eventos especiales : "special_event"`)
Temporadas, festividades o campañas con ajuste de tarifa por fechas:
- `Nombre : "name"`, `Descripción : "description"`, `Fecha de inicio : "start_date"` y `Fecha de fin : "end_date"` (ambas incluidas).
- `Porcentaje de ajuste : "discount_percentage"`: **con signo**; positivo es descuento y negativo es recargo. Se aplica noche por noche (regla provisional, pendiente de confirmar con el cliente).
- `Evento activo : "active"`.

### C. Directorio de Huéspedes (`Huéspedes : "guest"`)
- `Teléfono de WhatsApp : "whatsapp_phone"` (único; reconoce al huésped en futuras visitas), `Nombre completo : "name"`, `Documento de identidad : "document_number"`, `Correo : "email"` y `Consentimiento de tratamiento de datos : "habeas_data_accepted"` (Ley 1581 de 2012).

### D. Registro de Reservas (`Reservas : "booking"`)
Cada habitación reservada, ya sea desde el chatbot o desde la aplicación web (una fila por habitación; las de un mismo grupo comparten código):
- `Identificador : "id"`, `Habitación : "room_id"` y `Huésped titular : "guest_id"`.
- `Identificador de grupo : "reservation_group_id"` y `Código público : "group_code"`: formato `TS-XXXX` aleatorio y único, compartido por todas las habitaciones del grupo y buscado siempre por coincidencia exacta.
- `Fecha de entrada : "check_in"` y `Fecha de salida : "check_out"`.
- `Estado : "status"`: `BLOQUEADA_TEMPORAL`, `PENDIENTE_PAGO`, `CONFIRMADA`, `EN_CURSO`, `EXPIRADA` o `CANCELADA`.
- `Vencimiento del bloqueo : "expires_at"`: 15 minutos desde que se crea un bloqueo temporal; vacío en las demás reservas.
- `Estado del pago : "payment_status"`: `pending`, `partial` (50%), `paid` (100%) o `refunded`. `Identificador de pago : "payment_id"` (único; garantiza que una transacción no se aplique dos veces).
- `Precio total : "total_price"` y `Monto abonado : "paid_amount"` (base para saldos y reembolsos).
- `Adultos : "adults"`, `Niños : "children"`, `Mascota : "with_pet"` y `Acompañantes : "companions"` (nombres reales de los acompañantes).
- `Canal de origen : "source"`: `"chatbot"` o `"web"`.

### E. Tienda, Cafetería y Folio
- **Tienda (`Productos : "product"`):** `Código : "code"`, `Nombre`, `Categoría`, `Precio : "price"`, `Existencias : "stock"` y `Activo : "active"`.
- **Cafetería Salgados Café:** la carta (`"cafe_menu"`) y las comandas (`"cafe_order"`, con `Reserva : "booking_id"`, `Habitación : "room_id"`, mesa, productos y total).
- **Folio de la habitación (`"folio_charge"`):** cargos de tienda o cafetería asociados a una reserva, con cantidad, precio unitario histórico, total y si ya fueron pagados.

### F. Egresos (`Egresos : "expense"`)
`Fecha : "expense_date"`, `Monto : "amount"`, `Categoría`, `Descripción`, y la anulación lógica (`"voided"`, `"voided_reason"`) que conserva el comprobante sin borrarlo.

### G. Conversaciones de WhatsApp (`Conversaciones : "conversation"`)
Sesión de cada huésped con el chatbot guardada en PostgreSQL: `Llave de sesión : "session_key"`, `Teléfono : "wa_id"`, `Nombre : "sender_name"`, `Estado y paso : "state"` y `"step"`, `Atención humana activa : "agent_active"`, `Contexto : "session_data"` y `Vencimiento : "expires_at"`.

### H. Usuarios del Personal y Auditoría
- **`Usuarios del sistema : "system_users"`:** `Usuario : "username"`, `Contraseña cifrada : "password_hash"`, `Rol : "role"` (`Administrador` o `Recepcionista`), `Nombre : "name"` y `Activo : "active"`.
- **`Bitácora de auditoría : "audit_log"`:** registro inmutable de las acciones críticas (fecha, usuario, acción, entidad e identificador, con el detalle en JSON).

---

## 3. Regla de Exclusión para Impedir Sobreventas

El **primer y único candado** contra la sobreventa es una restricción matemática dentro del motor de base de datos sobre la tabla `Reservas : "booking"` (`Restricción contra reservas superpuestas : "no_overlapping_bookings"`).

Usa un índice de rangos de fechas (`EXCLUDE USING gist`) que impide insertar o actualizar dos reservas para la misma habitación si sus fechas se cruzan (`"[)"`: incluye el día de entrada y excluye el de salida, de modo que un huésped puede salir en la mañana y otro ingresar en la tarde del mismo día), siempre que la reserva esté en un estado que retiene la habitación: `BLOQUEADA_TEMPORAL`, `PENDIENTE_PAGO`, `CONFIRMADA` o `EN_CURSO`. Como el bloqueo temporal de 15 minutos es una fila más de esa tabla, el candado de corta duración y el definitivo son el mismo mecanismo: no hay forma de que dos procesos concurrentes tomen la misma habitación.

---

## 4. Control de Versiones del Esquema (Migraciones)

El esquema se gestiona con **Alembic**. El contenedor de la API ejecuta `alembic upgrade head` cada vez que arranca, por lo que la base siempre queda en la última versión. Las migraciones están en [apps/api/alembic/versions/](../../apps/api/alembic/versions):

1. [001_initial_schema.py](../../apps/api/alembic/versions/001_initial_schema.py): Extensión `btree_gist`, tablas principales (`room`, `guest`, `booking`, `audit_log`), el identificador de pago único y la restricción `EXCLUDE` contra cruces de fechas.
2. [002_system_users.py](../../apps/api/alembic/versions/002_system_users.py): Usuarios del personal y roles. Crea las cuentas de desarrollo `admin` y `recepcion` (**solo desarrollo**: cambie las contraseñas antes de un despliegue real).
3. [003_conversations_and_payments.py](../../apps/api/alembic/versions/003_conversations_and_payments.py): Tabla de sesiones de conversación en PostgreSQL (reemplaza a Redis).
4. [004_rooms_1_to_9_and_operations.py](../../apps/api/alembic/versions/004_rooms_1_to_9_and_operations.py): Habitaciones numeradas del 1 al 9 con las tarifas vigentes y las tablas operativas (tienda, cafetería, folio, eventos y egresos).
5. [005_pending_payment_status.py](../../apps/api/alembic/versions/005_pending_payment_status.py): Estado `PENDIENTE_PAGO`; la restricción de exclusión lo incluye para que la reserva retenga la habitación hasta que llegue el pago.

**Pruebas:** `pytest` crea y migra por su cuenta una base aparte (`satoripms_test`), de modo que nunca toca los datos operativos.

**Referencia histórica:** el esquema del servidor Java anterior (Flyway, `V1`–`V9`) se conserva en [docs/legacy-ref/db-migrations/](../legacy-ref/db-migrations) solo como consulta; no se ejecuta.
