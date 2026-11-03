# Estructura de Datos (Base de Datos) — SatoriPMS

## 1. Propósito del Módulo

La **Base de Datos** de **SatoriPMS** resguarda toda la información comercial, operativa y contable de **Torre Satori** sobre el motor relacional **PostgreSQL 16**. Su diseño garantiza que los datos de habitaciones, eventos especiales, huéspedes, reservas, pagos, consumos de tienda, movimientos financieros, reseñas y usuarios del personal se almacenen sin duplicidades, manteniendo el historial contable intacto y bloqueando de raíz cualquier intento de asignar una misma habitación a dos reservas en fechas cruzadas.

---

## 2. Organización de la Información del Hotel

A continuación se describe qué información almacena cada entidad del sistema, explicando cada dato en lenguaje de negocio junto con su nombre técnico en la base de datos:

### A. Catálogo de Habitaciones (`Habitaciones : "room"`)
Almacena la configuración comercial y operativa de cada una de las habitaciones del hotel (referencia actual de **9 habitaciones** administrables desde la aplicación web):
- `Identificador único : "id"`: Número interno consecutivo de la habitación.
- `Número de habitación : "number"`: Código visible de la habitación (por ejemplo, `"101"`, `"201"`, `"301"`), único en el hotel.
- `Nombre comercial : "name"` y `Descripción : "description"`: Nombre y detalle de las comodidades de la habitación.
- `Categoría o tipo : "type"`: Clasificación de la habitación (`"ESTANDAR"`, `"DOBLE"`, `"SUITE"`).
- `Capacidad base de adultos : "base_adults_capacity"`: Cantidad de personas cubiertas por la tarifa base por noche.
- `Capacidad máxima de adultos : "max_adults_capacity"` y `Capacidad de niños : "children_capacity"`: Tope máximo de personas permitidas en la habitación.
- `Permitir mascotas : "allows_pets"`: Indica si la habitación es apta para viajeros con mascotas.
- `Precio base por noche : "price_per_night"`: Valor por noche para la capacidad base.
- `Precio por persona adicional : "extra_guest_price"`: Valor que se suma cuando el grupo supera la capacidad base sin exceder el tope máximo.
- `Estado operativo : "status"`: Estado físico actual (`Disponible : "available"`, `Ocupada : "occupied"`, `En mantenimiento : "maintenance"`).
- `Habitación activa : "active"`: Define si la habitación está habilitada para la venta.
- **Regla de eliminación y protección:** Solo el Administrador puede crear, editar o eliminar habitaciones. Una habitación solo puede eliminarse si no tiene ninguna reserva en estado pendiente de pago o confirmada.

### B. Eventos Especiales y Descuentos por Fechas (`Eventos especiales : "special_event"`)
Permite al administrador programar temporadas altas, festividades locales o campañas de descuento en rangos de fechas específicos:
- `Nombre del evento : "name"` y `Descripción : "description"`: Motivo del evento o promoción (por ejemplo, *"Festival Bandola"*, *"Descuento de Temporada Baja"*).
- `Fecha de inicio : "start_date"` y `Fecha de fin : "end_date"`: Rango de días en que aplica el evento.
- `Porcentaje de descuento o ajuste : "discount_percentage"`: Porcentaje de descuento (o incremento en temporada especial) que se aplica sobre las noches dentro del rango.
- `Estadía mínima de noches : "min_nights"`: Cantidad mínima de noches requerida para reservar durante el evento (opcional).
- `Evento activo : "active"`: Indica si la regla tarifaria se encuentra vigente.

### C. Directorio de Huéspedes (`Huéspedes : "guest"`)
Conserva el perfil de cada cliente que se comunica por WhatsApp o se registra en recepción:
- `Identificador único : "id"`.
- `Teléfono de WhatsApp : "whatsapp_phone"`: Número telefónico único del huésped que sirve como llave de reconocimiento automático en futuras visitas.
- `Nombre completo : "name"`: Nombre y apellidos del titular.
- `Documento de identidad : "document_number"`: Cédula o pasaporte del titular (entre 6 y 10 dígitos numéricos).
- `Notas de recepción : "notes"`: Observaciones de atención o preferencias del cliente.

### D. Registro de Reservas (`Reservas : "booking"`)
Contiene cada estadía reservada desde el chatbot de WhatsApp o desde la aplicación web:
- `Identificador de reserva : "id"`.
- `Identificador de grupo de reserva : "reservation_group_id"`: Código único universal (cuyo prefijo de 8 caracteres se entrega al cliente) que agrupa todas las habitaciones tomadas en una misma solicitud familiar o grupal.
- `Habitación asignada : "room_id"` y `Huésped titular : "guest_id"`.
- `Fecha de entrada : "check_in"` y `Fecha de salida : "check_out"`.
- `Estado de la reserva : "status"`: Admite exclusivamente cuatro estados en minúsculas:
  - `Pendiente de pago : "pending_payment"`
  - `Confirmada : "confirmed"`
  - `Finalizada : "finished"`
  - `Cancelada : "cancelled"`
- `Estado del pago : "payment_status"`: Refleja la situación financiera de la reserva (`Pendiente : "pending"`, `Pago parcial del 50% : "partial"`, `Pagada al 100% : "paid"`, `Reembolsada : "refunded"`).
- `Precio total de la estadía : "total_price"`: Valor total calculado (noches base más recargos por persona adicional y ajustes de eventos especiales).
- `Monto abonado : "paid_amount"`: Dinero efectivamente pagado por el huésped hasta el momento (base sobre la cual se calcula cualquier saldo pendiente o reembolso por cancelación).
- `Cantidad de adultos : "adults"`, `Cantidad de niños : "children"`, `Viaja con mascota : "with_pet"` y `Nombres de acompañantes : "companions"`.
- `Canal de origen : "source"`: Indica si la reserva fue tomada por el asistente virtual (`"chatbot"`) o desde recepción (`"web"`).
- `Código de bloqueo utilizado : "lock_id"`: Referencia del candado temporal de 15 minutos con el que se aseguró la habitación.

### E. Catálogo de Productos y Consumos de Tienda (`Productos : "product"` y `Consumos : "consumption"`)
Gestiona la vitrina del hotel y los cargos a las habitaciones:
- **En `Productos : "product"`:** `Nombre del producto : "name"`, `Precio de venta actual : "price"`, `Cantidad en inventario : "stock"` y `Producto activo : "active"`. Si un producto con ventas históricas se retira del mercado, se marca como inactivo en lugar de borrarse físicamente.
- **En `Consumos : "consumption"`:** `Producto vendido : "product_id"`, `Reserva asociada : "booking_id"` (cuando el huésped pide cargarlo a la cuenta de su habitación, o vacío si es una venta de mostrador a un visitante externo), `Cantidad : "quantity"`, `Precio unitario histórico : "unit_price"` (congela el precio al momento de la venta para que futuros cambios de tarifa no alteren cuentas pasadas) y `Consumo pagado : "paid"`.

### F. Movimientos Financieros (`Registros financieros : "financial_record"`)
Consolida el flujo de caja del hotel para los reportes administrativos y la exportación contable:
- `Tipo de movimiento : "type"`: `Ingreso : "income"` o `Egreso : "expense"`.
- `Categoría contable : "category"`: Clasificación del movimiento (reserva, tienda, nómina, servicios públicos, mantenimiento, insumos).
- `Monto : "amount"`, `Descripción : "description"`, `Reserva vinculada : "booking_id"` (si aplica) y `Fecha del movimiento : "date"`.

### G. Reseñas y Opiniones de Huéspedes (`Reseñas : "review"`)
Almacena las valoraciones recopiladas por el chatbot o registradas desde recepción:
- `Nombre del autor : "author_name"`, `Teléfono de WhatsApp : "wa_id"`, `Calificación en estrellas : "rating"` (de 1 a 5), `Comentario : "comment"`, `Canal de origen : "source"` (`"chatbot"` o `"google"`), `Reserva vinculada : "booking_id"`, `Huésped vinculado : "guest_id"` y `Fecha de creación : "created_at"`.

### H. Conversaciones de WhatsApp y Usuarios del Personal (`Conversaciones : "conversation"` y `Usuarios del sistema : "system_users"`)
- **En `Conversaciones : "conversation"`:** Registra el vínculo con cada huésped, su estado de atención (`Atendida por bot : "bot"` o `Escalada a humano : "human_handling"`), si requiere intervención prioritaria (`Requiere agente : "needs_agent"`), fecha del último mensaje y resumen del contexto.
- **En `Usuarios del sistema : "system_users"`:** Almacena las credenciales del personal del hotel (`Nombre de usuario : "username"`, `Contraseña cifrada : "password_hash"`, `Rol : "role"` —`"admin"` o `"receptionist"`—, `Nombre completo : "name"` y `Usuario activo : "active"`).

---

## 3. Regla de Exclusión para Impedir Sobreventas en Base de Datos

Además del bloqueo temporal de 15 minutos en memoria rápida, la tabla `Reservas : "booking"` cuenta con una restricción matemática directamente en el motor de base de datos (`Restricción contra reservas superpuestas : "no_overlapping_bookings"`).

Esta regla utiliza un índice de rangos de fechas (`Índice GiST : "EXCLUDE USING gist"`) que impide insertar o actualizar dos reservas para la misma habitación si sus fechas de entrada y salida se cruzan (`"[)"`: incluye el día de entrada y excluye el día de salida, permitiendo que un huésped salga en la mañana y otro ingrese en la tarde del mismo día), siempre que la reserva se encuentre en estado `Pendiente de pago : "pending_payment"` o `Confirmada : "confirmed"`. Cuando una reserva cambia a `Cancelada : "cancelled"`, el rango queda libre automáticamente.

---

## 4. Control de Versiones del Esquema (Migraciones)

La creación y evolución de las tablas se gestiona de forma automática al iniciar el servidor mediante archivos numerados en [apps/api/src/main/resources/db/migration/](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/resources/db/migration):

1. [V1__initial_schema.sql](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/resources/db/migration/V1__initial_schema.sql): Crea las tablas principales del sistema (`room`, `guest`, `booking`, `product`, `consumption`, `financial_record`, `conversation`, `system_users`), la restricción contra cruces de fechas y los índices de búsqueda rápida.
2. [V2__seed_rooms.sql.example](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/resources/db/migration/V2__seed_rooms.sql.example): Plantilla de carga inicial con las **9 habitaciones de referencia** del hotel. Al copiarse como `V2__seed_rooms.sql`, inserta el catálogo inicial sin exponer tarifas reales en el repositorio público.
3. [V3__align_id_types_with_jpa.sql](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/resources/db/migration/V3__align_id_types_with_jpa.sql): Alinea los tipos de datos de los identificadores numéricos de todas las tablas para soportar volúmenes altos de registros.
4. [V4__booking_groups_and_guest_document.sql](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/resources/db/migration/V4__booking_groups_and_guest_document.sql): Incorpora el documento de identidad del huésped (`document_number`), el código de agrupación para reservas de múltiples habitaciones (`reservation_group_id`) y el listado de acompañantes (`companions`).
5. [V5__add_paid_amount_and_review_entity.sql](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/resources/db/migration/V5__add_paid_amount_and_review_entity.sql): Añade el control del monto efectivamente abonado (`paid_amount`), amplía los estados de pago parcial y crea la tabla de reseñas (`review`) con sus datos iniciales.
6. [V6__seed_products.sql.example](file:///home/guarinve/Documentos/SatoriPMS/apps/api/src/main/resources/db/migration/V6__seed_products.sql.example): Plantilla de carga inicial para los productos de la tienda interna del hotel (se copia localmente como `V6__seed_products.sql`).
7. [dev_seed.sql](file:///home/guarinve/Documentos/SatoriPMS/db/seed/dev_seed.sql): Archivo auxiliar para entornos de desarrollo local que permite crear el usuario inicial de administración en la tabla `Usuarios del sistema : "system_users"`.
