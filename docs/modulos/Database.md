# Módulo — Base de Datos y Persistencia

## 1. Motor y Extensiones

PostgreSQL 16, con la extensión `btree_gist` habilitada. Esta extensión es necesaria para combinar una columna de igualdad (`room_id`) con una de solapamiento de rangos (`stay_range`) dentro de una restricción `EXCLUDE`. El esquema se versiona con Flyway y se mapea desde el backend con JPA e Hibernate. Redis complementa la persistencia con datos efímeros: sesiones conversacionales y bloqueos temporales de habitaciones.

## 2. Modelo de Datos

| Tabla | Campos clave | Notas |
|---|---|---|
| `guest` | `whatsapp_phone` (único), `name`, `email`, `document_number` | Identidad mínima del huésped. |
| `room` | `number` (único), `type`, `base_adults_capacity`, `max_adults_capacity`, `children_capacity`, `extra_guest_price`, `allows_pets`, `price_per_night`, `status`, `active` | `CHECK (max_adults_capacity >= base_adults_capacity)`. `status` admite `available`, `occupied`, `cleaning` y `maintenance`. |
| `conversation` | `guest_id`, `status`, `step`, `check_in`, `check_out`, `selected_room_id`, `adults`, `children`, `with_pet`, `total_price`, `lock_token`, `lock_expires_at` | Un índice único garantiza una sola conversación activa por huésped. `status` admite `active`, `escalated`, `cancelled`, `completed` y `expired`. |
| `booking` | `guest_id`, `room_id`, `conversation_id`, `check_in`, `check_out`, `stay_range`, `status`, `payment_status`, `total_price`, `paid_amount`, `source`, `lock_id`, `reservation_group_id`, `companions` | Un registro por habitación reservada. Restricción anti-doble-reserva (ver sección 3). `stay_range` es una columna generada de tipo `daterange`. `paid_amount NUMERIC(10,2) NOT NULL DEFAULT 0.00`. |
| `receipt` | `booking_id`, `issued_at`, `amount`, `reference` | Recibo inmutable asociado a cada reserva pagada (RN-05). |
| `review` | `guest_id`, `room_id`, `booking_id`, `rating` (1 a 5), `comment`, `author_name`, `source`, `created_at` | `guest_id`, `room_id` y `booking_id` son nulables para admitir reseñas importadas de Google. `source` admite `chatbot`, `google` y `web`. |
| `product` | `name`, `description`, `price`, `stock`, `active` | Catálogo de la tienda. |
| `consumption` | `booking_id`, `product_id`, `quantity`, `unit_price`, `paid` | `paid` indica si el consumo se pagó de contado o se carga a la cuenta de la habitación para liquidarse en el check-out. |
| `system_users` | `username` (único), `password_hash`, `role`, `name`, `active` | `role` admite `admin` y `receptionist`. La contraseña se almacena con BCrypt. |

### 2.1 Estados y Valores Permitidos

| Campo | Valores |
|---|---|
| `booking.status` | `pending_payment`, `confirmed`, `finished`, `cancelled` |
| `booking.payment_status` | `pending`, `paid`, `partial`, `refunded` |
| `booking.source` | `chatbot`, `web` |
| `room.status` | `available`, `occupied`, `cleaning`, `maintenance` |
| `review.source` | `chatbot`, `google`, `web` |
| `system_users.role` | `admin`, `receptionist` |

El estado visual "Bloqueo temporal" del panel de habitaciones no se almacena en `room.status`: se deriva de la existencia de un bloqueo vigente en Redis para esa habitación.

### 2.2 Grupo de Reserva y Código de Consulta

Cuando un huésped reserva varias habitaciones en una misma operación, el sistema crea un registro `booking` por habitación y todos comparten el mismo `reservation_group_id` (UUID). Los totales, el monto pagado y el saldo pendiente que ve el huésped son valores agregados del grupo. El huésped identifica su reserva con un código de 8 caracteres, formado por los primeros 8 caracteres del `reservation_group_id` en mayúsculas (por ejemplo `B457F45D`); el UUID completo también es válido como código de consulta.

## 3. Integridad y Concurrencia

```sql
CONSTRAINT no_overlapping_bookings EXCLUDE USING gist (
    room_id WITH =,
    stay_range WITH &&
) WHERE (status IN ('pending_payment', 'confirmed'))
```

Esta restricción materializa a nivel de base de datos el principio de anti-doble reserva: PostgreSQL rechaza de forma atómica cualquier operación que genere una `stay_range` solapada para la misma habitación mientras el estado sea `pending_payment` o `confirmed`. No depende del código de aplicación para funcionar. Al cancelar una reserva (estado `cancelled`), las fechas se liberan automáticamente al salir del `WHERE` de la restricción, y el registro permanece como historial.

Otras restricciones relevantes: `chk_booking_dates` (`check_in < check_out`), `chk_booking_range_not_empty` e índices `gist` sobre `stay_range` para que la validación sea eficiente y cumpla el requisito de responder en menos de 3 segundos.

## 4. Datos en Redis

| Clave | Contenido | Ciclo de vida |
|---|---|---|
| `session:{waId}` | Estado de la conversación del chatbot: estado y paso actuales, indicador `agent_active`, borrador de reserva y datos del remitente | Se renueva en cada mensaje saliente y expira por inactividad |
| Bloqueos de habitación | Token de bloqueo por habitación y rango de fechas, gestionado con scripts Lua | TTL de 900 segundos; se libera al confirmar la reserva o al terminar el flujo sin reservar |

## 5. Migraciones Flyway

| Versión | Archivo | Propósito |
|---|---|---|
| V1 | `V1__init_schema.sql` | Esquema inicial completo: guest, room, conversation, booking, review, product, consumption y system_users |
| V2 | `V2__seed_rooms.sql` | Carga inicial de 9 habitaciones de ejemplo |
| V3 | `V3__bigint_fk_alignment.sql` | Migra las claves primarias y foráneas a `BIGINT` para alinear con JPA e Hibernate |
| V4 | `V4__add_reservation_group_and_companions.sql` | Agrega `reservation_group_id` (UUID) y `companions` a `booking`, y `document_number` a `guest` |
| V5 | `V5__add_paid_amount_and_review_entity.sql` | Agrega `paid_amount` a `booking`, adapta `review` (agrega `author_name`, `source` y la nulabilidad de las claves foráneas externas) y precarga reseñas semilla de Google |

Cada migración recibe un número de versión único dentro de `classpath:db/migration`. Cualquier archivo de semilla nuevo se numera con la siguiente versión disponible.

## 6. Patrón de Archivos de Semilla

Los archivos `.sql.example` se versionan en Git con datos de ejemplo. El archivo real con los datos del hotel queda fuera del control de versiones, de forma análoga al patrón `.env` y `.env.example`. Si el archivo real no existe, Flyway simplemente no aplica esa migración y la tabla queda vacía sin afectar el resto del esquema.
