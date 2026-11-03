# Facturación y Finanzas — SatoriPMS

## 1. Propósito del Módulo

El módulo de **Facturación y Finanzas** centraliza todas las reglas económicas de **Torre Satori**: la cotización de estadías con personas adicionales y eventos especiales, el control de anticipos del 50% y pagos totales del 100%, el cálculo estricto de reembolsos sobre lo abonado, la liquidación de cuentas al finalizar la estadía, el registro de gastos operativos, el cálculo de pago de turnos de recepción y la exportación del balance mensual en Excel.

---

## 2. Cálculo de Tarifas de Hospedaje y Eventos Especiales

### A. Tarifa Base y Recargo por Persona Adicional
Cada habitación del hotel cuenta con:
- Una tarifa base por noche (`Precio por noche : "price_per_night"`).
- Una capacidad base de personas incluidas en esa tarifa (`Capacidad base de adultos : "base_adults_capacity"`).
- Un valor adicional fijo por cada huésped que supere la capacidad base sin exceder el tope máximo permitido en la habitación (`Precio por persona adicional : "extra_guest_price"`).

El valor total de la estadía se obtiene sumando el costo de las noches reservadas más el recargo correspondiente a las personas adicionales. Tanto en el flujo de reserva guiada como en el asistente con inteligencia artificial en WhatsApp y en la aplicación web, el sistema muestra de forma explícita y separada la **tarifa base**, el **recargo por persona adicional** y el **total de la estadía** antes de solicitar el pago.

### B. Eventos Especiales, Temporadas y Descuentos por Fechas
El administrador puede definir en el calendario del sistema **eventos especiales o campañas promocionales** (por ejemplo, descuentos en días de temporada baja o tarifas especiales para festividades locales de Sevilla como el Festival Bandola o Semana Santa). Cuando las fechas seleccionadas por el viajero coinciden con un evento activo, el sistema aplica automáticamente el porcentaje de descuento o el ajuste tarifario configurado sobre las noches correspondientes.

---

## 3. Modalidades de Pago y Control de Saldos

Al confirmar una reserva, el sistema admite dos modalidades financieras:

1. **Pago Completo del 100% (`Opción de pago : "full"`):**
   - El huésped abona la totalidad del valor de la reserva.
   - El monto abonado (`Monto abonado : "paid_amount"`) queda igual al precio total (`Precio total : "total_price"`), el saldo pendiente en `$0.00` y el estado financiero en `Pagada : "paid"`.
2. **Anticipo del 50% (`Opción de pago : "deposit"`):**
   - El huésped garantiza su reserva abonando exactamente la mitad (50%) del valor total de la estadía.
   - El monto abonado registra ese 50% inicial, el estado financiero queda en `Pago parcial : "partial"` y el 50% restante figura como saldo pendiente.
   - **Liquidación del segundo 50%:** El huésped puede pagar el saldo restante en cualquier momento antes de su llegada desde la opción *"Revisar o Cancelar"* del menú de WhatsApp, o bien cancelarlo directamente en la recepción del hotel al momento de su ingreso o salida.

---

## 4. Política de Reembolso por Cancelación (Estrictamente sobre lo Abonado)

Cuando un huésped solicita cancelar su reserva confirmada, el sistema calcula el monto a devolver **exclusivamente sobre el dinero que el cliente haya pagado efectivamente hasta ese momento** (`Monto abonado : "paid_amount"`), nunca sobre el valor total no pagado de la estadía.

Tomando como punto de referencia la hora oficial de entrada al hotel (**15:00 horas / 3:00 p. m.** del día de llegada), se aplican tres tramos de antelación:

| Antelación respecto a la hora de entrada (15:00) | Porcentaje de Reembolso | Ejemplo con reserva de \$200.000 pagada al 100% | Ejemplo con reserva de \$200.000 abonada al 50% (\$100.000 pagados) |
|---|---|---|---|
| **Más de 72 horas antes** | **100% de lo abonado** | Se reembolsan **\$200.000** | Se reembolsan **\$100.000** |
| **Entre 24 y 72 horas antes** | **50% de lo abonado** | Se reembolsan **\$100.000** | Se reembolsan **\$50.000** |
| **Menos de 24 horas antes o no presentación** | **0% (Sin reembolso)** | Se reembolsan **\$0** | Se reembolsan **\$0** |

Antes de ejecutar la cancelación definitiva, el sistema presenta este cálculo exacto al huésped y le solicita su confirmación expresa. *(Los rangos horarios y porcentajes están diseñados para ajustarse como parámetros administrativos según la directriz final del propietario del hotel).*

---

## 5. Liquidación de Cuenta a la Salida del Huésped (Check-out)

En el momento en que el huésped entrega la habitación, el sistema consolida en una sola vista todos los rubros económicos de su estadía:
- Valor total del alojamiento menos los abonos ya realizados.
- Suma de todos los productos de la tienda interna consumidos durante la estadía y cargados a la habitación que aún figuren como no pagados (`Consumo pagado : "paid = false"`).
- **Total neto a pagar en recepción:** Una vez recibido el pago de los rubros abiertos, todos los consumos pasan a estado pagado, la reserva queda en estado `Finalizada : "finished"` y el ingreso queda asentado en el balance del hotel.

---

## 6. Registro de Gastos Operativos y Cálculo de Turnos de Recepción

Para que el administrador conozca la utilidad real del negocio sin recurrir a cuadernos externos, el módulo financiero incluye:

### A. Ingresos y Egresos Operativos
- **Ingresos automáticos:** Cada pago de reserva (anticipo del 50%, pago del 100% o liquidación de saldo) y cada venta pagada de la tienda interna genera automáticamente un movimiento de ingreso (`Tipo de movimiento : "income"`).
- **Egresos manuales:** El administrador puede registrar los gastos del hotel (`Tipo de movimiento : "expense"`), clasificándolos por categoría (nómina y turnos, servicios públicos de energía/agua/internet, compra de insumos de aseo y lavandería, reabastecimiento de vitrina o mantenimiento locativo), indicando fecha, valor y descripción.

### B. Liquidación Configurable de Turnos de Recepción
Atendiendo la dinámica operativa de Torre Satori, el módulo permite calcular el pago correspondiente al personal de recepción a partir de parámetros editables por el administrador (sin valores fijos rígidos):
- Valor de la hora o del turno ordinario diurno.
- Recargos configurables por turno nocturno, dominical o festivo.
- Registro de horas o turnos trabajados en el período y generación automática del egreso de nómina una vez aprobado por el administrador.

---

## 7. Exportación Contable en Formato Excel

En cualquier momento o al cierre del mes, el **Administrador** puede seleccionar un rango de fechas y descargar un **Informe Contable en Excel (`.xlsx`)** listo para revisión gerencial o contable, el cual incluye:
1. Resumen ejecutivo de ingresos totales, egresos totales y utilidad neta del período.
2. Detalle de ingresos por hospedaje (diferenciando ventas logradas por el chatbot de WhatsApp frente a reservas tomadas en recepción).
3. Detalle de ingresos por ventas de la tienda interna.
4. Relación desglosada de todos los gastos y pagos de turnos registrados en el período.
