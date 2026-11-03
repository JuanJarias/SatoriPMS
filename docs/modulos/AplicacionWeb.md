# Aplicación Web (Recepción y Administración) — SatoriPMS

## 1. Propósito del Módulo

La **Aplicación Web** es el centro de control operativo y administrativo de **Torre Satori**. Está diseñada para que el personal de recepción gestione de forma ágil el día a día del hotel (ocupación, llegadas, salidas, reservas presenciales, atención de chats escalados y ventas de vitrina) y para que el administrador tenga autonomía total sobre la configuración del negocio (catálogo de habitaciones, tarifas, eventos especiales con descuentos, inventario, finanzas y personal).

---

## 2. Perfiles de Usuario y Control de Vistas

El acceso a la aplicación web requiere iniciar sesión con usuario y contraseña, adaptando las pantallas disponibles según el rol asignado:

- **Recepcionista:** Tiene acceso al calendario de ocupación, gestión de llegadas (check-in) y salidas (check-out), creación de reservas manuales, bandeja de conversaciones de WhatsApp que requieren atención humana y punto de venta de la tienda interna.
- **Administrador:** Cuenta con acceso completo a todas las funciones de recepción y, de manera exclusiva, a los módulos de **administración de habitaciones (crear, editar y eliminar)**, **configuración de eventos especiales y descuentos por fechas**, administración de catálogo e inventario de productos, reportes financieros, registro de gastos, liquidación de turnos, moderación de reseñas y gestión de usuarios del sistema.

---

## 3. Módulos Operativos de Recepción

### A. Calendario Interactivo de Ocupación y Estado de Habitaciones
Presenta en una cuadrícula visual las habitaciones del hotel (referencia actual de 9 habitaciones) cruzadas por los días de la semana o del mes:
- **Colores y estados claros:** Distingue visualmente las habitaciones disponibles, ocupadas, reservadas con pago completo, reservadas con anticipo del 50%, bloqueadas temporalmente por un cliente en proceso de pago (15 minutos) y fuera de servicio por mantenimiento o limpieza.
- **Consulta rápida:** Al hacer clic sobre cualquier bloque del calendario, el recepcionista visualiza los datos del titular, documento, teléfono de WhatsApp, acompañantes, mascota, monto pagado y saldo pendiente.
- **Cambio de estado operativo:** Permite marcar una habitación como *"En mantenimiento"* o *"En limpieza"* para que no sea ofrecida por el chatbot de WhatsApp hasta que vuelva a habilitarse como *"Disponible"*.

### B. Registro de Llegada del Huésped (Check-in)
Cuando el viajero se presenta en la recepción del hotel:
1. El recepcionista localiza la reserva por código, documento de identidad o nombre del titular.
2. Verifica y actualiza los datos del titular y los nombres de los acompañantes.
3. Si la reserva fue confirmada con el **anticipo del 50%**, el panel muestra el saldo restante del 50% y permite registrar su cobro en el momento del ingreso (o mantenerlo en la cuenta de la habitación para liquidarlo a la salida, según acuerdo con el huésped).
4. Cambia el estado de la habitación a ocupada y habilita la cuenta de la estadía para recibir cargos de la tienda interna.

### C. Registro de Salida y Liquidación de Cuenta (Check-out)
Al finalizar la estadía del huésped:
1. El sistema presenta el estado de cuenta consolidado de la reserva:
   - Valor total del hospedaje y monto previamente abonado.
   - Saldo pendiente de alojamiento (si aún no se había cancelado el segundo 50%).
   - Listado detallado de todos los **consumos de la tienda interna** cargados a la habitación que se encuentren pendientes de pago.
2. **Validación de paz y salvo:** El sistema no permite finalizar la salida mientras existan cargos o saldos abiertos sin marcar como pagados.
3. Una vez registrado el pago total de los pendientes, la reserva pasa a estado **Finalizada**, se emite el soporte de cierre de cuenta y la habitación queda liberada para limpieza y nuevos huéspedes.

### D. Creación de Reservas Manuales (Huéspedes Presenciales o Telefónicos)
Para los viajeros que llegan directamente a la puerta del hotel o llaman por teléfono sin usar WhatsApp:
- El recepcionista ingresa las fechas de entrada y salida, cantidad de adultos, niños y mascota.
- El sistema consulta en tiempo real las mismas habitaciones disponibles que ve el chatbot (respetando los bloqueos temporales activos y las reservas confirmadas) y aplica primero un bloqueo preventivo antes de confirmar.
- Registra el origen de la reserva como canal web (`Origen de la reserva : "web"`) para diferenciarla en los reportes respecto a las ventas logradas por el asistente de WhatsApp (`Origen de la reserva : "chatbot"`).

### E. Bandeja de Conversaciones y Atención Humana
Muestra las conversaciones de WhatsApp en las que el viajero solicitó hablar con un agente humano o tiene una solicitud especial (como cotizar el alquiler completo del hotel para un evento familiar):
- Resalta en la parte superior los chats con solicitud de atención humana activa.
- Permite consultar el contexto del cliente y reanudar el asistente automático una vez resuelta la inquietud del viajero.

---

## 4. Módulos Exclusivos de Administración

### A. Gestión Completa del Catálogo de Habitaciones (Crear, Editar y Eliminar)
Dado que las características comerciales del hotel evolucionan con el tiempo, el **Administrador** dispone de un panel dedicado para gestionar las habitaciones sin depender de soporte técnico:
1. **Crear habitación:** Permite dar de alta una nueva habitación definiendo su número identificador, nombre comercial, descripción, categoría o tipo (Estándar, Doble, Suite, Múltiple), capacidad base incluida en la tarifa, capacidad máxima de adultos y niños, tarifa base por noche, valor del recargo por persona adicional, política de admisión de mascotas y estado inicial.
2. **Editar habitación:** Permite modificar en cualquier momento el precio por noche, el recargo por persona adicional, las capacidades de personas, la descripción, el nombre, el permiso de mascotas o el estado operativo de cualquiera de las habitaciones. Los nuevos precios se aplican de inmediato a las nuevas cotizaciones sin alterar el valor pactado en las reservas que ya fueron confirmadas con anterioridad.
3. **Eliminar habitación (con protección de reservas):**
   - Esta acción está restringida exclusivamente al rol de **Administrador**.
   - Antes de eliminar una habitación, el sistema verifica obligatoriamente que **no tenga ninguna reserva activa, confirmada, en curso o pendiente de pago**. Si existe al menos una reserva vigente o futura en esa habitación, el sistema rechaza la eliminación y muestra una alerta indicando cuáles reservas deben reubicarse o finalizarse primero.
   - Si la habitación no tiene reservas pendientes ni actuales pero registra estadías históricas pasadas, el sistema ofrece su desactivación permanente del catálogo comercial para no perder la trazabilidad contable de los meses anteriores.

### B. Eventos Especiales, Temporadas y Descuentos por Fechas
En consonancia con las necesidades expresadas por el propietario del hotel, el **Administrador** cuenta con una función de programación de **Eventos Especiales y Temporadas**:
- **Definición de fechas especiales:** Permite crear un evento indicando su nombre comercial (por ejemplo, *"Semana Santa"*, *"Festival Bandola"*, *"Promoción de Temporada Baja"* o *"Descuento de Aniversario"*), la fecha de inicio y la fecha de fin.
- **Tipo de ajuste tarifario:** El administrador define si el evento aplica un **porcentaje de descuento** (por ejemplo, 15% de descuento en días entre semana de temporada baja) o una **tarifa especial de temporada alta** sobre todas las habitaciones o sobre categorías específicas.
- **Condiciones opcionales del evento:** Permite asociar un número mínimo de noches de estadía para fechas de altísima demanda o habilitar paquetes grupales.
- **Aplicación automática:** Tanto el chatbot de WhatsApp como el formulario web de recepción calculan automáticamente el descuento o la tarifa del evento cuando las fechas consultadas por el viajero coinciden con el calendario del evento activo.

### C. Tienda, Finanzas, Reseñas y Seguridad
Desde el menú administrativo, el administrador accede igualmente a:
- El control de productos, existencias y alertas de inventario (detallado en [TiendaInventario.md](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/TiendaInventario.md)).
- El balance financiero de ingresos, gastos, liquidación de turnos de recepción y exportación contable en Excel (detallado en [FacturacionFinanzas.md](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/FacturacionFinanzas.md)).
- La moderación de reseñas y el listado de clientes frecuentes para campañas de fidelización (detallado en [ResenasFidelizacion.md](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/ResenasFidelizacion.md)).
- La gestión de cuentas de usuario del personal y el historial de auditoría (detallado en [Seguridad.md](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Seguridad.md)).
