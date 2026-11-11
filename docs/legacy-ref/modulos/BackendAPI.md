# Servicios del Servidor Central (Backend API) — SatoriPMS

## 1. Propósito del Módulo

El **Servidor Central** es el núcleo lógico de **SatoriPMS**. Actúa como único punto de coordinación entre el asistente de WhatsApp, la aplicación web de recepción y administración, la memoria rápida de bloqueos temporales y la base de datos del hotel.

Su función es garantizar que todas las reglas del negocio —como el cálculo de precios con personas adicionales o eventos especiales, el bloqueo de 15 minutos contra sobreventa, la validación de abonos del 50% y 100%, el cálculo de reembolsos sobre lo efectivamente pagado y los permisos exclusivos del administrador— se apliquen de manera uniforme y segura sin importar desde qué canal se realice la operación.

---

## 2. Operaciones de Disponibilidad, Habitaciones y Eventos Especiales

### A. Consulta de Habitaciones Disponibles
- **Concepto para el negocio:** Permite conocer qué habitaciones están libres y habilitadas para hospedar a un grupo de viajeros en un rango de fechas determinado, filtrando según la cantidad de adultos, niños y si viajan con mascota.
- **Funcionamiento:** El servidor busca primero las habitaciones activas que no tengan reservas confirmadas ni pendientes de pago en esas fechas y que cumplan con la capacidad total solicitada; enseguida descarta cualquier habitación que tenga un bloqueo temporal de 15 minutos activo por parte de otro usuario y aplica las tarifas o descuentos de eventos especiales vigentes.
- **Identificador técnico de la operación:** `Consulta de disponibilidad : "GET /api/rooms/availability"`
- **Parámetros de entrada:**
  - `Fecha de entrada : "checkIn"` (formato `AAAA-MM-DD`)
  - `Fecha de salida : "checkOut"` (formato `AAAA-MM-DD`)
  - `Cantidad de adultos : "adults"`
  - `Cantidad de niños : "children"`
  - `Viaja con mascota : "pet"`

### B. Administración del Catálogo de Habitaciones (Solo Administrador)
- **Concepto para el negocio:** Permite al administrador del hotel crear nuevas habitaciones, actualizar toda su información comercial (número, nombre, tipo, tarifa por noche, recargo por persona adicional, capacidades de adultos y niños, admisión de mascotas, estado operativo) y eliminar habitaciones cuando corresponda.
- **Regla de protección al eliminar:** Cuando el administrador solicita eliminar una habitación, el servidor verifica que no exista ninguna reserva en estado pendiente de pago o confirmada asociada a esa habitación. Si tiene reservas pendientes o actuales, la operación se rechaza informando el motivo para proteger a los huéspedes con reserva vigente.
- **Identificadores técnicos de las operaciones:**
  - `Listar catálogo completo de habitaciones : "GET /api/rooms"`
  - `Crear nueva habitación : "POST /api/rooms"`
  - `Editar información de una habitación : "PUT /api/rooms/{id}"`
  - `Eliminar habitación sin reservas pendientes : "DELETE /api/rooms/{id}"`

### C. Gestión de Eventos Especiales y Descuentos por Fechas (Solo Administrador)
- **Concepto para el negocio:** Permite definir temporadas o eventos especiales en el calendario (con fecha de inicio, fecha de fin y porcentaje de descuento o ajuste tarifario) para incentivar la ocupación o gestionar fechas de alta demanda turística en Sevilla.
- **Identificadores técnicos de las operaciones:**
  - `Consultar eventos y promociones : "GET /api/events"`
  - `Crear evento especial o descuento : "POST /api/events"`
  - `Actualizar evento especial : "PUT /api/events/{id}"`
  - `Eliminar o desactivar evento : "DELETE /api/events/{id}"`

---

## 3. Operaciones de Bloqueo Temporal y Prevención de Sobreventa

### A. Adquisición de Bloqueo Temporal por 15 Minutos
- **Concepto para el negocio:** Cuando un viajero elige una habitación en WhatsApp o un recepcionista inicia una reserva manual, el servidor coloca un candado temporal de 15 minutos (900 segundos) sobre esa habitación y esas fechas. Así, ningún otro usuario puede tomarla mientras el primero escribe sus datos y realiza el pago.
- **Funcionamiento interno:** Utiliza un registro de intervalos de fechas en memoria rápida (`Intervalos bloqueados por habitación : "lock:room:{roomId}:intervals"`) y metadatos con expiración automática (`Metadatos del bloqueo : "lock:room:{roomId}:metadata:{token}"`). Si el rango de fechas se cruza con otro bloqueo vigente, devuelve un aviso de conflicto (código HTTP 409) para que el usuario elija otra habitación.
- **Identificador técnico de la operación:** `Bloquear habitación temporalmente : "POST /api/bookings/lock"`
- **Datos devueltos:** `Código único de bloqueo : "lockToken"`, `Tiempo de vigencia en segundos : "ttlSeconds"` (900) y `Precio base cotizado : "totalPrice"`.

### B. Liberación Inmediata de Bloqueos Temporales
- **Concepto para el negocio:** Si el huésped decide cancelar la reserva antes de pagar, escribe *"menú"* para reiniciar su conversación o su sesión se cierra por inactividad, el servidor elimina de inmediato el bloqueo temporal en memoria sin esperar a que se cumplan los 15 minutos, devolviendo la habitación al inventario disponible al instante.
- **Identificador técnico de la operación:** `Liberar bloqueo temporal : "POST /api/bookings/unlock"`
- **Datos recibidos:** Lista de habitaciones y sus códigos de bloqueo (`Lista de bloqueos a liberar : "locks"` con `Identificador de habitación : "roomId"` y `Código de bloqueo : "lockToken"`).

---

## 4. Operaciones de Confirmación, Consulta, Pago de Saldo y Cancelación de Reservas

### A. Confirmación de Reserva (Individual o Grupal)
- **Concepto para el negocio:** Registra en firme la reserva de una o varias habitaciones bajo un mismo código grupal (`Identificador de grupo de reserva : "reservationGroupId"`), guarda o actualiza la ficha del huésped titular y sus acompañantes, calcula el precio total (sumando noches base y recargo por personas adicionales), procesa la modalidad de pago elegida y libera los bloqueos temporales de memoria.
- **Modalidades de pago admitidas (`Opción de pago : "paymentOption"`):**
  - `Pago completo del 100% : "full"`: La reserva queda en estado `Confirmada : "confirmed"`, estado de pago `Pagada : "paid"`, monto abonado igual al 100% del total y saldo pendiente en cero.
  - `Anticipo del 50% : "deposit"`: La reserva queda en estado `Confirmada : "confirmed"`, estado de pago `Pago parcial : "partial"`, monto abonado igual al 50% del total y el 50% restante como saldo pendiente.
- **Identificación del canal de origen (`Origen de la reserva : "source"`):** Registra si la reserva provino del asistente de WhatsApp (`"chatbot"`) o del panel de recepción (`"web"`).
- **Identificador técnico de la operación:** `Confirmar reserva : "POST /api/bookings/confirm"`

### B. Consulta de Reserva por Código Único
- **Concepto para el negocio:** Permite tanto al huésped en WhatsApp como al recepcionista consultar todos los detalles de una reserva ingresando los 8 caracteres de su código único. Devuelve las habitaciones asignadas, fechas, noches, datos del titular, valor total, **monto efectivamente abonado**, **saldo pendiente** y el cálculo exacto de la política de reembolso aplicable en ese instante.
- **Identificador técnico de la operación:** `Consultar reserva por código : "GET /api/bookings/group/{code}"`

### C. Pago del Saldo Restante (Segundo 50%)
- **Concepto para el negocio:** Cuando una reserva fue garantizada con el anticipo del 50%, esta operación permite liquidar el 50% restante antes del ingreso o en recepción. Actualiza el monto pagado (`Monto abonado : "paid_amount"`) al 100% del valor total de la estadía, cambia el estado de pago a `Pagada : "paid"` y deja el saldo pendiente en cero.
- **Identificador técnico de la operación:** `Pagar saldo restante de reserva : "POST /api/bookings/group/{code}/pay-remaining"`

### D. Cancelación de Reserva y Cálculo de Reembolso sobre lo Pagado
- **Concepto para el negocio:** Anula todas las habitaciones asociadas al código de reserva, liberando de inmediato las fechas en la base de datos para nuevos huéspedes, y calcula el monto a reembolsar **estrictamente sobre el valor que el cliente haya pagado hasta ese momento** (`Monto abonado : "paid_amount"`), según las horas que falten para la hora de entrada (15:00 del día de llegada):
  - Más de 72 horas antes: devolución del **100% de lo abonado**.
  - Entre 24 y 72 horas antes: devolución del **50% de lo abonado**.
  - Menos de 24 horas antes: **0% de devolución**.
- **Identificador técnico de la operación:** `Cancelar reserva grupal : "POST /api/bookings/group/{code}/cancellation"`

### E. Operaciones de Recepción (Check-in, Check-out y Monitoreo)
- **Concepto para el negocio:** Permiten al recepcionista listar las reservas en tiempo real, registrar el ingreso físico del huésped en el hotel y procesar su salida una vez verificada la liquidación de todos los cargos de alojamiento y consumos de tienda.
- **Identificadores técnicos de las operaciones:**
  - `Listado general y monitoreo de reservas : "GET /api/bookings/debug"`
  - `Registrar ingreso del huésped (Check-in) : "POST /api/bookings/{id}/check-in"`
  - `Registrar salida del huésped (Check-out) : "POST /api/bookings/{id}/check-out"`

---

## 5. Operaciones de Conversaciones, Reseñas, Tienda y Finanzas

### A. Reseñas y Calificaciones de Huéspedes
- `Consultar reseñas recientes : "GET /api/reviews"`: Devuelve las últimas opiniones registradas con su calificación de 1 a 5 estrellas, comentario, nombre del autor y fecha.
- `Registrar nueva reseña : "POST /api/reviews"`: Guarda una nueva calificación enviada desde el chatbot de WhatsApp o desde el panel web.

### B. Bandeja de Conversaciones y Escalamiento a Recepción
- `Listar conversaciones de WhatsApp : "GET /api/conversations"`: Permite al panel web consultar los chats de los huéspedes, priorizando aquellos que solicitaron atención de un recepcionista humano.
- `Notificar escalamiento a agente humano : "POST /api/conversations/{id}/escalation"`: Registra la solicitud de transferencia a recepción humana y emite la alerta en tiempo real al panel web mediante conexión continua (`Canal de notificaciones en tiempo real : "/ws"`).

### C. Tienda Interna, Inventario y Finanzas
- **Catálogo y consumos de tienda:** Operaciones para crear y editar productos (`Gestión de productos : "/api/products"`), registrar compras con descuento automático de existencias y asociar el cargo a una reserva activa o como venta directa de mostrador (`Registro de consumos : "/api/consumptions"`).
- **Movimientos financieros y reportes:** Operaciones para consolidar los ingresos por reservas y tienda, registrar gastos operativos del hotel (`Movimientos financieros : "/api/finances"`), calcular el pago de turnos del personal de recepción y generar el archivo contable descargable en formato Excel (`Exportación contable : "GET /api/finances/export"`).
