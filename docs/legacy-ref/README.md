# Referencias Legadas para Migración a FastAPI

Este directorio preserva especificaciones técnicas de la implementación previa (Java / Spring Boot / Flyway) que sirven como insumo para el desarrollo del nuevo monolito modular en Python 3.12 (FastAPI + SQLAlchemy + Alembic).

---

## 1. Migraciones de Base de Datos (`db-migrations/`)
Contiene los scripts SQL del backend Java (esquema, semillas y las migraciones `V6` a `V9` de eventos, restaurante, reseñas y `booking_code`) y las plantillas de semilla `R__seed_*.sql.example`:
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


---

## Nota de integración (2026-11-19)

Los documentos de `docs/Diagramas/` (01 a 03) y `docs/modulos/` (`BackendAPI.md`, `Database.md`) permanecen en su ubicación original y se actualizan a FastAPI. Las versiones Java previas están en el tag `legacy-java-backup` y en el historial de `main` hasta el commit `3185c2b`.
