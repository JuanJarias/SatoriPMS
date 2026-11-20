# Servicios del Servidor Central (Backend API) — SatoriPMS

## 1. Propósito del Módulo

El **Servidor Central** es el núcleo lógico de **SatoriPMS**. Actúa como único punto de coordinación entre el asistente de WhatsApp, la aplicación web de recepción y administración y la base de datos del hotel. Está construido con **Python 3.12 y FastAPI**, y toda su persistencia vive en **PostgreSQL 16**: no depende de Redis ni de ningún otro almacén para los bloqueos.

Su función es garantizar que todas las reglas del negocio —como el cálculo de precios con personas adicionales o eventos especiales, el bloqueo de 15 minutos contra sobreventa, la validación de abonos del 50% y 100%, el cálculo de reembolsos sobre lo efectivamente pagado y los permisos exclusivos del administrador— se apliquen de manera uniforme y segura sin importar desde qué canal se realice la operación.

La documentación interactiva de todas las operaciones se publica en `http://localhost:8080/docs` (OpenAPI).

### Rutas y versiones
Las operaciones de la aplicación web se publican bajo `/api/v1/...`. Las que usa el orquestador del chatbot (n8n) se publican además en `/api/...` sin versión, con el mismo comportamiento. En este documento se citan las rutas de n8n (`/api/...`); la web usa las equivalentes con `/api/v1/`.

### Control de Acceso
Ninguna operación del servidor central está abierta al público:
- **Personal del hotel:** inicia sesión con usuario y contraseña (`Iniciar sesión : "POST /api/v1/auth/login"`) y recibe una credencial digital firmada (JWT) con vigencia limitada (por defecto, un turno de 8 horas), que acompaña cada operación posterior. La credencial indica si la persona es **Administrador** o **Recepcionista**, y el servidor rechaza las operaciones reservadas al Administrador cuando las intenta otro perfil.
- **Asistente de WhatsApp:** se identifica con una llave de servicio privada (encabezado `X-Service-Key`, variable `SATORI_SERVICE_KEY`) que solo conocen el servidor central y el orquestador del chatbot. Con ella únicamente puede realizar las operaciones propias de la atención al huésped (disponibilidad, bloqueos, reservas, consulta, pago de saldo, cancelación y confirmación de pagos de la pasarela).
- **Protección de los datos del huésped:** cuando la solicitud proviene del asistente de WhatsApp, consultar, pagar el saldo o cancelar una reserva exige el código de reserva **y** el documento del titular. Si el documento no coincide, el servidor responde exactamente igual que si la reserva no existiera (HTTP 404), y nunca devuelve el documento completo (solo sus últimos 4 dígitos, por ejemplo `******5666`).

---

## 2. Operaciones de Disponibilidad, Habitaciones y Eventos Especiales

### A. Consulta de Habitaciones Disponibles
- **Concepto para el negocio:** Permite conocer qué habitaciones están libres y habilitadas para hospedar a un grupo de viajeros en un rango de fechas determinado, filtrando según la cantidad de adultos, niños y si viajan con mascota.
- **Funcionamiento:** El servidor busca las habitaciones activas que no tengan reservas confirmadas, en curso o pendientes de pago en esas fechas y que cumplan con la capacidad solicitada; descarta cualquier habitación con un bloqueo temporal vigente de otro usuario (los bloqueos vencidos se ignoran) y cotiza cada una aplicando las tarifas, el recargo por persona adicional y los eventos especiales vigentes.
- **Identificador técnico de la operación:** `Consulta de disponibilidad : "GET /api/rooms/availability"`
- **Parámetros de entrada:** `Fecha de entrada : "checkIn"` y `Fecha de salida : "checkOut"` (formato `AAAA-MM-DD`), `Cantidad de adultos : "adults"`, `Cantidad de niños : "children"` y `Viaja con mascota : "pet"`.

### B. Administración del Catálogo de Habitaciones
- **Concepto para el negocio:** Permite al personal consultar las habitaciones (referencia actual de **9 habitaciones**, numeradas del 1 al 9) y al administrador crearlas, actualizar toda su información comercial y eliminarlas cuando corresponda. Recepción puede cambiar el estado físico (disponible, ocupada, limpieza, mantenimiento).
- **Regla de protección al eliminar:** Si la habitación tiene reservas activas, la operación se rechaza (HTTP 409) informando el motivo, para proteger a los huéspedes con reserva vigente.
- **Identificadores técnicos de las operaciones:**
  - `Listar habitaciones : "GET /api/v1/rooms"`
  - `Crear habitación (Administrador) : "POST /api/v1/rooms"`
  - `Editar habitación (Administrador) : "PUT /api/v1/rooms/{id}"`
  - `Cambiar estado operativo : "PATCH /api/v1/rooms/{id}/status"`
  - `Eliminar habitación sin reservas activas (Administrador) : "DELETE /api/v1/rooms/{id}"`

### C. Gestión de Eventos Especiales y Descuentos por Fechas
- **Concepto para el negocio:** Permite al administrador definir temporadas o eventos especiales (fecha de inicio, fecha de fin y porcentaje) para incentivar la ocupación o gestionar fechas de alta demanda turística en Sevilla. El porcentaje es **con signo**: positivo es un descuento y negativo es un recargo.
- **Aplicación sobre el precio (regla provisional, pendiente de confirmar con el cliente):** El ajuste se aplica **noche por noche**: solo las noches de la estadía que caen dentro de las fechas del evento (ambas fechas incluidas) reciben el descuento o el recargo. Si varios eventos coinciden en una misma noche, sus porcentajes se suman, y el precio de una noche nunca baja de cero. El recargo por persona adicional se ajusta con el promedio de las noches de la estadía. La alternativa pendiente de decisión es aplicar el primer evento a toda la estadía.
- **Identificadores técnicos de las operaciones:**
  - `Consultar eventos : "GET /api/v1/events"`
  - `Crear evento (Administrador) : "POST /api/v1/events"`
  - `Editar evento : "PUT /api/v1/events/{id}"`
  - `Activar o desactivar evento : "PATCH /api/v1/events/{id}/toggle"`
  - `Eliminar evento : "DELETE /api/v1/events/{id}"`

---

## 3. Operaciones de Bloqueo Temporal y Prevención de Sobreventa

### A. Adquisición de Bloqueo Temporal por 15 Minutos
- **Concepto para el negocio:** Cuando un viajero elige una habitación en WhatsApp o un recepcionista inicia una reserva, el servidor coloca un candado temporal de 15 minutos (900 segundos) sobre esa habitación y esas fechas. Así, ningún otro usuario puede tomarla mientras el primero escribe sus datos y realiza el pago.
- **Funcionamiento interno:** El bloqueo es una **fila de reserva en estado `BLOQUEADA_TEMPORAL` con una hora de vencimiento** (`expires_at`). Antes de crearla, el servidor marca como expirados los bloqueos vencidos de esa habitación dentro de la misma transacción. La restricción `EXCLUDE USING gist` de PostgreSQL impide que dos filas activas se crucen, de modo que la sobreventa es imposible aunque dos solicitudes lleguen en el mismo instante. Un proceso programado revisa cada 60 segundos y expira los bloqueos vencidos.
- **Identificador técnico de la operación:** `Bloquear habitación temporalmente : "POST /api/bookings/lock"` (HTTP 409 si el rango se cruza con otra reserva o bloqueo vigente).
- **Datos devueltos:** `Código único de bloqueo : "lockToken"` (identificador de la fila), `Tiempo de vigencia en segundos : "ttlSeconds"` (900) y el precio cotizado de la estadía.

### B. Liberación Inmediata de Bloqueos Temporales
- **Concepto para el negocio:** Si el huésped decide cancelar antes de pagar, escribe *"menú"* para reiniciar su conversación o su sesión se cierra por inactividad, el servidor marca de inmediato el bloqueo como expirado, devolviendo la habitación al inventario al instante.
- **Identificador técnico de la operación:** `Liberar bloqueo temporal : "POST /api/bookings/unlock"`
- **Datos recibidos:** Lista de habitaciones y sus códigos de bloqueo (`"rooms"` con `"roomId"` y `"lockToken"`).

---

## 4. Operaciones de Confirmación, Consulta, Pago de Saldo y Cancelación de Reservas

### A. Estados de una reserva
En la base de datos los estados están en español: `BLOQUEADA_TEMPORAL`, `PENDIENTE_PAGO`, `CONFIRMADA`, `EN_CURSO`, `EXPIRADA` y `CANCELADA`. Las respuestas dirigidas al chatbot los traducen al contrato que usa el flujo de n8n: `locked`, `pending_payment`, `confirmed`, `checked_in`, `expired` y `cancelled`. Los estados `BLOQUEADA_TEMPORAL`, `PENDIENTE_PAGO`, `CONFIRMADA` y `EN_CURSO` retienen la habitación.

### B. Confirmación de Reserva (Individual o Grupal)
- **Concepto para el negocio:** Registra la reserva de una o varias habitaciones bajo un mismo código grupal (`reservationGroupId`), guarda o actualiza la ficha del huésped titular y sus acompañantes, calcula el precio total (noches con sus ajustes por eventos especiales y recargo por personas adicionales) y genera el código público `TS-XXXX`: cuatro caracteres aleatorios y únicos, sin `0`, `O`, `1` ni `I` para evitar confusiones.
- **Reservas del chatbot:** quedan en estado `PENDIENTE_PAGO` con pago `pending` y monto abonado en cero. La habitación sigue retenida y **solo el pago aprobado de la pasarela la confirma** (sección F).
- **Reservas del personal:** cuando confirma un recepcionista autenticado, se registra el pago de inmediato según la modalidad (`Opción de pago : "paymentOption"`): `full` deja la reserva `CONFIRMADA` y `paid` (100%); `deposit` la deja `CONFIRMADA` y `partial` (50%).
- **Canal de origen (`source`):** `"chatbot"` o `"web"`.
- **Identificadores técnicos:** `Confirmar reserva : "POST /api/bookings/confirm"` y `Crear reserva manual desde recepción : "POST /api/v1/bookings/manual"`.

### C. Consulta de Reserva por Código Único
- **Concepto para el negocio:** Permite al huésped en WhatsApp o al recepcionista consultar todos los detalles de una reserva con su código `TS-XXXX` (por ejemplo, `TS-7K4Q`), que debe coincidir exactamente; también se acepta el identificador de grupo completo. Desde WhatsApp se exige además el documento del titular (encabezado `X-Guest-Document`). Devuelve las habitaciones asignadas, fechas, noches, datos del titular, valor total, **monto efectivamente abonado**, **saldo pendiente** y la política de reembolso aplicable en ese instante.
- **Identificador técnico de la operación:** `Consultar reserva por código : "GET /api/bookings/group/{code}"`

### D. Pago del Saldo Restante (Segundo 50%)
- **Concepto para el negocio:** Cuando una reserva fue garantizada con el anticipo del 50%, permite liquidar el 50% restante. Pasa el monto abonado al 100% del valor de la estadía y el estado de pago a `Pagada : "paid"`. Si la reserva no tiene saldo pendiente o está cancelada, responde HTTP 409. Desde WhatsApp el cuerpo debe incluir `{"document": "..."}`.
- **Identificador técnico de la operación:** `Pagar saldo restante de reserva : "POST /api/bookings/group/{code}/pay-remaining"`

### E. Cancelación de Reserva y Cálculo de Reembolso sobre lo Pagado
- **Concepto para el negocio:** Anula todas las habitaciones del código de reserva, liberando de inmediato las fechas en la base de datos, y calcula el reembolso **estrictamente sobre el valor que el cliente haya pagado** (`paid_amount`), según las horas que falten para la hora de entrada (15:00 del día de llegada):
  - Más de 72 horas antes: devolución del **100% de lo abonado**.
  - Entre 24 y 72 horas antes: devolución del **50% de lo abonado**.
  - Menos de 24 horas antes: **0% de devolución**.
- **Identificador técnico de la operación:** `Cancelar reserva grupal : "POST /api/bookings/group/{code}/cancellation"` (desde WhatsApp, con `{"document": "..."}`).

### F. Conciliación de Pagos Externos (Pasarela de Pago)
- **Concepto para el negocio:** Mientras el huésped no paga, la reserva permanece `PENDIENTE_PAGO` y retiene la habitación. Cuando la pasarela (Wompi) confirma la transacción `APPROVED`, el orquestador del chatbot invoca esta operación: la reserva pasa a `CONFIRMADA`, el pago a `partial` (50%) o `paid` (100%) y se asienta el importe pagado. La operación es **idempotente por transacción** (`transactionId`): repetirla no duplica el pago, y una transacción ya usada en otra reserva se rechaza con HTTP 409. Solo la llave de servicio o un administrador pueden invocarla.
- **Identificadores técnicos:**
  - `Confirmar pago externo por código : "POST /api/bookings/group/{code}/confirm-external-payment"`
  - `Confirmar pago externo con código en el cuerpo : "POST /api/bookings/confirm-external-payment"` (campo `reservationCode`)
  - `Webhook directo de la pasarela con firma : "POST /api/v1/payments/webhook"` (valida la firma HMAC `X-Hub-Signature-256` o el checksum de Wompi y aplica idempotencia por `payment_id`)
  - `Generar enlace de pago : "POST /api/v1/payments/checkout-link"`

### G. Operaciones de Recepción
- **Concepto para el negocio:** Permiten listar las reservas, registrar el ingreso físico del huésped (pasa a `EN_CURSO`) y procesar su salida una vez liquidados todos los cargos de alojamiento y consumos.
- **Identificadores técnicos:**
  - `Listar reservas (web) : "GET /api/v1/bookings"`
  - `Listado de monitoreo con estados del contrato de n8n : "GET /api/bookings/debug"` (uso interno; expone documentos completos)
  - `Registrar ingreso (Check-in) : "POST /api/v1/bookings/{id}/check-in"`
  - `Registrar salida (Check-out) : "POST /api/v1/bookings/{id}/check-out"`

---

## 5. Conversaciones, Reseñas, Tienda, Cafetería y Finanzas

### A. Sesiones del chatbot y escalamiento a recepción
- `Listar conversaciones de WhatsApp : "GET /api/v1/conversations"`: Bandeja de chats para el panel web; la web la consulta por sondeo.
- `Aviso del chatbot de que un huésped pidió un agente : "POST /api/notifications/agent-request"`: Lo invoca n8n con la llave de servicio (`{"wa_id", "name", "context"}`). Marca como escalada la conversación en curso y responde 202.
- `Escalar una conversación : "POST /api/v1/conversations/{id}/escalation"`: Marca la conversación como escalada y registra auditoría.
- `Sesión conversacional : "GET | POST | PUT | DELETE /api/v1/conversations/session/{key}"`: Guarda en PostgreSQL el estado de la conversación y los enlaces de pago. Lo usa la versión V10 del flujo de n8n, que reemplaza los nodos de Redis; la V9 aún conserva su sesión en Redis (ver [Chatbot](Chatbot.md)).

### B. Reseñas
- `Resumen de reseñas : "GET /api/v1/reviews/summary"`: Calificación promedio, total de opiniones y distribución por estrellas consultadas en Google Places. El chatbot canaliza las opiniones al perfil oficial de **Torre Satori en Google Reviews**; la aplicación web opera en modo de solo lectura.

### C. Tienda interna, Salgados Café y folio de la habitación
- `Productos de la tienda : "GET | POST /api/v1/store/products"` y `"PUT | DELETE /api/v1/store/products/{ref}"`: Inventario y precios (altas, cambios y bajas solo para el administrador).
- `Venta de tienda : "POST /api/v1/store/sales"`: Descuenta existencias y, si se pide, carga el consumo al folio de la habitación.
- `Carta y comandas de la cafetería : "GET | POST /api/v1/restaurant/menu"`, `"GET | POST /api/v1/restaurant/orders"` y `"PATCH /api/v1/restaurant/orders/{ref}/status"`.
- `Cargos pendientes o históricos del folio : "GET /api/v1/folio-charges"`.

### D. Finanzas y reportes
- `Egresos : "GET | POST /api/v1/expenses"` y `"POST /api/v1/expenses/{id}/void"` (anulación lógica; el egreso no se borra).
- `Resumen financiero : "GET /api/v1/finance/summary"`: Ingresos, egresos y desglose por canal.
- `Exportación contable : "GET /api/v1/reports/export.xlsx"`: Libro de Excel con resumen, reservas, egresos e inventario.

### E. Usuarios, auditoría y tiempo real
- `Perfil, cambio de contraseña y gestión de cuentas : "GET /api/v1/auth/me"`, `"POST /api/v1/auth/change-password"`, `"GET | POST /api/v1/auth/users"` y `"PATCH /api/v1/auth/users/{id}"` (cuentas solo para el administrador).
- `Bitácora de auditoría inmutable : "GET /api/v1/auth/audit-logs"` (solo administrador).
- `Notificaciones en tiempo real : "GET /api/v1/events/stream"`: Canal SSE autenticado que avisa a la web los cambios de reservas, bloqueos y habitaciones.
- `Salud del servicio : "GET /api/v1/health"`.
