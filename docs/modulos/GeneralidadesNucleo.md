# Generalidades y Núcleo del Negocio — SatoriPMS

## 1. Contexto del Negocio

**Torre Satori** es un hotel boutique familiar ubicado en **Sevilla, Valle del Cauca**, municipio reconocido por su tradición cafetera, su paisaje cultural y su constante flujo turístico durante fines de semana, puentes festivos y celebraciones regionales (como el Festival Bandola, las Fiestas aniversarias y Semana Santa).

Tradicionalmente, la gestión del hotel se ha realizado mediante atención manual por WhatsApp y apuntes en hojas de cálculo o cuadernos físicos. Este esquema presenta cuatro limitaciones principales:
1. **Pérdida de reservas fuera de horario:** Cuando un viajero escribe en la noche o madrugada solicitando disponibilidad y precios, la demora en la respuesta provoca que reserve en otro alojamiento.
2. **Riesgo de sobreventa:** Si dos personas consultan por la misma habitación al mismo tiempo —una por WhatsApp y otra en la recepción física—, existe el riesgo de comprometer dos veces el mismo espacio.
3. **Descontrol de cobros y consumos adicionales:** Los productos consumidos en la vitrina o tienda del hotel (bebidas, mecato, artículos personales) y los abonos parciales requieren un consolidado claro al momento de la salida del huésped.
4. **Dependencia de intermediarios:** Las plataformas externas de reserva cobran comisiones cercanas al 18% por cada estadía. Fortalecer el canal directo de WhatsApp permite conservar ese margen en beneficio del hotel.

---

## 2. Propósito del Sistema

**SatoriPMS** es una solución integral diseñada a la medida de Torre Satori que unifica la atención automatizada por WhatsApp con un panel web administrativo y de recepción. Su propósito es automatizar la venta directa de habitaciones las 24 horas del día, impedir cualquier cruce o duplicidad de reservas y entregar a la administración control total sobre sus habitaciones, tarifas, eventos especiales, tienda interna, ingresos, egresos y reseñas de clientes.

El catálogo de referencia actual del hotel contempla **9 habitaciones** (utilizando inicialmente datos y tarifas de referencia mientras se formaliza el listado comercial definitivo del hotel), con la flexibilidad de que el administrador pueda crear, editar o retirar habitaciones directamente desde la aplicación web en cualquier momento.

---

## 3. Capacidades Principales de la Plataforma

El sistema se organiza en áreas funcionales que cubren de principio a fin la operación del hotel:

| Área Funcional | Propósito Operativo | Usuarios Principales |
|---|---|---|
| **Reserva Guiada y Asistente con Inteligencia Artificial por WhatsApp** | Atender al viajero las 24 horas, consultar disponibilidad real por fechas, cantidad de personas y mascotas, bloquear temporalmente la habitación elegida y confirmar la reserva con pago total o anticipo del 50%. | Huéspedes y viajeros |
| **Autogestión de Reservas por WhatsApp** | Permitir al huésped consultar el detalle de su reserva mediante su código único, pagar el saldo pendiente antes de llegar al hotel o cancelar su estadía aplicando la política de reembolso vigente. | Huéspedes y viajeros |
| **Escalamiento a Recepción Humana** | Silenciar el asistente automático cuando el viajero solicita atención personalizada o tiene una solicitud especial (como reservar todo el hotel para un grupo familiar) y notificar de inmediato a la recepción. | Huéspedes y Recepcionista |
| **Panel Operativo de Recepción (Check-in, Check-out y Reservas Manuales)** | Visualizar el calendario de ocupación, registrar el ingreso de los huéspedes verificando su documento y acompañantes, registrar reservas presenciales o telefónicas y liquidar la salida cobrando saldos o consumos pendientes. | Recepcionista y Administrador |
| **Administración del Catálogo de Habitaciones** | Crear nuevas habitaciones, editar toda su información (precio por noche, capacidad de adultos y niños, recargo por persona adicional, admisión de mascotas, descripción y estado) y eliminar habitaciones que no tengan reservas activas o pendientes. | Administrador |
| **Eventos Especiales, Temporadas y Descuentos** | Definir rangos de fechas para eventos especiales, temporadas altas o campañas promocionales en las que se apliquen descuentos o tarifas diferenciadas de forma automática. | Administrador |
| **Tienda Interna e Inventario** | Administrar el catálogo de productos de vitrina, registrar ventas de contado o con cargo a la habitación del huésped y controlar las existencias con alertas de agotamiento. | Recepcionista y Administrador |
| **Facturación, Finanzas y Turnos** | Registrar ingresos y gastos operativos del hotel, calcular el pago de turnos del personal de recepción según las horas y recargos configurados, y exportar el balance contable mensual en formato Excel. | Administrador |
| **Reseñas y Fidelización de Huéspedes** | Recopilar calificaciones de los clientes al finalizar su estadía, invitarlos a publicar su opinión en Google Maps y reconocer a los huéspedes frecuentes para otorgarles beneficios o descuentos. | Huéspedes y Administrador |
| **Seguridad, Roles y Auditoría** | Proteger el acceso al sistema diferenciando los permisos del Recepcionista y del Administrador, resguardar los datos personales conforme a la ley y mantener un historial inalterable de operaciones críticas. | Administrador |

---

## 4. Reglas de Negocio Fundamentales

Las siguientes reglas rigen el comportamiento de todos los módulos del sistema:

### A. Cálculo de Tarifas, Personas Adicionales y Eventos Especiales
- Cada habitación tiene una tarifa base por noche (`Precio por noche : "price_per_night"`), una capacidad base incluida en dicha tarifa (`Capacidad base de adultos : "base_adults_capacity"`) y una capacidad máxima permitida (`Capacidad máxima de adultos : "max_adults_capacity"` y `Capacidad de niños : "children_capacity"`).
- Cuando el número de huéspedes supera la capacidad base sin exceder el tope máximo de la habitación, el sistema suma automáticamente el valor configurado por cada persona adicional (`Precio por persona adicional : "extra_guest_price"`), mostrándolo de forma desglosada en el resumen antes del pago.
- Si la fecha de la estadía coincide con un **evento especial o campaña promocional** configurada por el administrador, el sistema aplica el descuento o ajuste tarifario correspondiente sobre las noches incluidas en dicho evento.

### B. Prevención Estricta de Sobreventa (Doble Protección)
- Ninguna habitación puede asignarse a dos reservas distintas cuyas fechas se crucen.
- **Primera protección (Bloqueo temporal de 15 minutos):** En el instante en que un huésped selecciona una habitación en WhatsApp o en la web, el sistema la bloquea temporalmente por 15 minutos. Durante ese lapso, ningún otro usuario puede tomarla. Si el huésped cancela la operación o reinicia su conversación, el bloqueo se libera de inmediato; si abandona el chat sin responder, el bloqueo se elimina automáticamente al expirar la sesión.
- **Segunda protección (Restricción en base de datos):** Al confirmar la reserva, la base de datos verifica de manera definitiva que no exista ningún cruce de fechas entre la fecha de llegada (`Fecha de entrada : "check_in"`) y la fecha de salida (`Fecha de salida : "check_out"`). El día de salida de un huésped queda habilitado para recibir a un nuevo viajero a partir de la hora de entrada.

### C. Modalidades de Pago (100% o Anticipo del 50%)
- Para confirmar una reserva, el huésped puede elegir entre:
  1. **Pago total (100%):** La reserva queda confirmada y completamente saldada (`Estado del pago : "paid"`).
  2. **Anticipo del 50%:** La reserva queda confirmada y garantizada con el pago de la mitad del valor total (`Estado del pago : "partial"`). El 50% restante queda registrado como saldo pendiente y puede pagarse en cualquier momento desde WhatsApp antes del viaje o directamente en la recepción del hotel.

### D. Política de Cancelación y Reembolso sobre lo Abonado
- Todo cálculo de devolución por cancelación se realiza **exclusivamente sobre el dinero que el huésped haya pagado efectivamente hasta ese momento** (`Monto abonado : "paid_amount"`), nunca sobre el valor total no pagado de la reserva.
- Tomando como referencia las 15:00 horas (3:00 p. m.) del día de llegada, se aplican tres ventanas de tiempo:
  - **Más de 72 horas de anticipación:** Reembolso del **100%** del monto abonado.
  - **Entre 24 y 72 horas de anticipación:** Reembolso del **50%** del monto abonado.
  - **Menos de 24 horas de anticipación o no presentación en el hotel:** **0%** de reembolso (sin devolución).
- Al confirmarse la cancelación, las habitaciones quedan libres de inmediato para nuevos viajeros. *(Los plazos de horas e importes de penalidad son parametrizables según la política definitiva que establezca la administración de Torre Satori).*

### E. Reglas de Administración de Habitaciones
- Únicamente el usuario con perfil de **Administrador** está autorizado para crear nuevas habitaciones, modificar los datos de las habitaciones existentes (nombre, número, tipo, precio por noche, recargo por persona adicional, capacidad de adultos y niños, admisión de mascotas y estado operativo) o eliminarlas.
- **Condición obligatoria para eliminar una habitación:** El sistema impide eliminar cualquier habitación que tenga reservas activas, confirmadas o pendientes de pago en el presente o hacia el futuro. Si una habitación cuenta con historial contable pasado y se retira de operación, se desactiva su disponibilidad comercial (`Habitación activa : "active"`) para preservar la integridad de los reportes financieros históricos.

### F. Reglas de Tienda, Inventario y Salida del Huésped (Check-out)
- Los productos del catálogo de la tienda interna que tengan ventas históricas registradas no se borran físicamente para no alterar la contabilidad; cuando dejan de venderse, se marcan como inactivos.
- Al registrar la salida de un huésped en recepción, el sistema verifica automáticamente si existen saldos pendientes de la estadía o consumos de tienda cargados a la habitación sin pagar, exigiendo su liquidación antes de cerrar la cuenta y liberar la habitación.
