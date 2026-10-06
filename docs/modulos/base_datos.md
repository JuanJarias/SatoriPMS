# Módulo — Base de Datos y Persistencia

### 1. Motor y Extensiones

PostgreSQL 16, con la extensión `btree_gist` habilitada, requerida para combinar una columna de igualdad (`room_id`) con una de solapamiento de rangos (`stay_range`) dentro de una restricción `EXCLUDE`.

---

### 2. Modelo de Datos

| Tabla | Campos clave | Notas |
|---|---|---|
| `guest` | `whatsapp_phone` (único), `name`, `email`, `document_number` | Identidad mínima del huésped |
| `room` | `number` (único), `type`, `base_adults_capacity`, `max_adults_capacity`, `children_capacity`, `extra_guest_price`, `allows_pets`, `price_per_night`, `status`, `active` | `CHECK (max_adults_capacity >= base_adults_capacity)` |
| `conversation` | `guest_id`, `status`, `step`, `check_in`, `check_out`, `selected_room_id`, `adults`, `children`, `with_pet`, `total_price`, `lock_token`, `lock_expires_at` | Único índice: una sola conversación activa por huésped |
| `booking` | `guest_id`, `room_id`, `conversation_id` (único), `check_in`, `check_out`, `stay_range`, `status`, `payment_status`, `total_price`, `source`, `lock_id`, `reservation_group_id`, `companions` | Restricción anti-doble-reserva (ver sección 3). `payment_status` acepta: `pending`, `paid`, `refunded`, `partial`. |
| `receipt` | `booking_id`, `issued_at`, `amount`, `reference` | Recibo asociado a cada reserva pagada (RN-05). Planificado en el esquema del Documento Maestro; aún no creado en migraciones. |
| `review` | `guest_id`, `room_id`, `booking_id` (único), `rating` (1–5), `comment` | Una reseña por reserva |
| `product` | `name`, `description`, `price`, `stock`, `active` | Catálogo de tienda |
| `consumption` | `booking_id`, `product_id`, `quantity`, `unit_price`, `paid` | El booleano `paid` indica si el consumo se pagó de contado o se carga al check-out |
| `system_users` | `username` (único), `password_hash`, `role`, `name`, `active` | Roles `admin`/`receptionist` |

---

### 3. Integridad y Concurrencia

```sql
CONSTRAINT no_overlapping_bookings EXCLUDE USING gist (
    room_id WITH =,
    stay_range WITH &&
) WHERE (status IN ('pending_payment', 'confirmed'))
```

Esta restricción es la materialización, a nivel de base de datos, del principio de anti-doble reserva: PostgreSQL rechaza de forma atómica cualquier operación que genere una `stay_range` solapada para la misma habitación mientras el estado sea `pending_payment` o `confirmed`. Al cancelar una reserva (estado `cancelled`), las fechas se liberan automáticamente al salir del `WHERE` de la restricción.

Otras restricciones relevantes: `chk_booking_dates` (`check_in < check_out`), `chk_booking_range_not_empty`, e índices `gist` sobre `stay_range` para eficiencia.

---

### 4. Migraciones Flyway

| Versión | Propósito |
|---|---|
| V1 | Esquema completo inicial (guest, room, conversation, booking, review, product, consumption, system_users) |
| V2 | Carga inicial de 9 habitaciones de ejemplo |
| V3 | Migra las claves primarias/foráneas a `BIGINT`, para alinear con JPA/Hibernate |
| V4 | Agrega `reservation_group_id` (UUID) y `companions` a `booking`; `document_number` a `guest` |

---

### 5. Patrón de Archivos de Semilla (`.example`)

Los archivos `.sql.example` sí se versionan en Git (con datos de ejemplo); el archivo real con datos del hotel queda fuera del control de versiones, de forma análoga al patrón `.env`/`.env.example`. Si el archivo real no existe, Flyway simplemente no aplica esa migración.
