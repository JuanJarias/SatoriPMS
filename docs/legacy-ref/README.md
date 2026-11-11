# Referencias Legadas para Migración a FastAPI

Este directorio preserva especificaciones técnicas de la implementación previa (Java / Spring Boot / Flyway) que sirven como insumo para el desarrollo del nuevo monolito modular en Python 3.12 (FastAPI + SQLAlchemy + Alembic).

---

## 1. Migraciones de Base de Datos (`db-migrations/`)
Contiene los 6 scripts SQL originales de esquema y semillas:
- `V1__initial_schema.sql`: DDL base con extensión `btree_gist` y constraint `no_overlapping_bookings EXCLUDE USING gist (room_id WITH =, stay_range WITH &&) WHERE (status IN ('pending_payment', 'confirmed'))`.
- `V2__seed_rooms.sql.example`: Plantilla de habitaciones de ejemplo.
- `V3__align_id_types_with_jpa.sql`: Alineación de claves foráneas y primarias a BIGINT.
- `V4__booking_groups_and_guest_document.sql`: Columnas `reservation_group_id`, `companions` y `document_number`.
- `V5__add_paid_amount_and_review_entity.sql`: Columna `paid_amount` y soporte para reseñas de Google y directas.
- `V6__seed_products.sql.example`: Semilla de productos para la tienda.

> [!NOTE]
> **Estado de verificación:** *No verificable: pendiente de probar en el primer lote de Alembic*.

---

## 2. Especificación de Endpoints (`endpoints-java.md`)
Detalla los contratos de entrada, salida, códigos HTTP y reglas de negocio de los endpoints REST previamente implementados en los controladores Java (`BookingController`, `ConversationController`, `ReviewController`), para garantizar paridad funcional al portar a routers de FastAPI.
