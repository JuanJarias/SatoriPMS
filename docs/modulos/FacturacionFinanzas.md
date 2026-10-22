# Módulo — Facturación y Finanzas

## 1. Requerimientos y Casos de Uso

**CU-06, Consultar ingresos y egresos.** Vista consolidada de las entradas (hospedaje y tienda) y las salidas de dinero por rangos de fecha.

**HU-01, Exportar informe a Excel.** Generación y descarga de un archivo con la relación contable mensual, para declaraciones y balances.

**HU-07, Cálculo de sueldo de recepción.** Cálculo automático de la compensación mensual o quincenal de la recepcionista, según la fórmula que defina el administrador.

**HU-13, Registrar egresos operativos.** Registro de gastos menores (mantenimiento, aseo, compras de inventario) con soporte digital.

## 2. Reglas de Negocio

**Cálculo de estadía.** El valor total se compone de la suma del precio por noche de las habitaciones seleccionadas, multiplicado por el número de noches, más los recargos por huéspedes adicionales calculados según RN-01.

**Modalidades de cobro del hospedaje.** El huésped puede pagar el 100 % al reservar o abonar el 50 % como anticipo. El sistema registra cuánto se pagó en `paid_amount` y mantiene el saldo pendiente como la diferencia con el total. El saldo se puede liquidar después desde el chatbot, con la opción de revisar la reserva, hasta quedar la reserva como pagada.

**Reembolsos.** Una cancelación genera un reembolso calculado sobre el monto efectivamente pagado, con el porcentaje de RN-03 según las horas restantes hasta el check-in: 100 % con más de 72 horas, 50 % entre 24 y 72 horas y 0 % con menos de 24 horas o no-show. La reserva cancelada se conserva como historial.

**RN-05, recibos.** Todo pago confirmado por concepto de hospedaje genera un comprobante de recibo inmutable asociado a la reserva, con fecha de emisión, monto y referencia.

## 3. Origen de los Datos Financieros

| Concepto | Origen |
|---|---|
| Ingresos por hospedaje | `booking.paid_amount` de las reservas, menos los reembolsos aplicados |
| Ingresos por tienda | `consumption.quantity` por `consumption.unit_price` de los consumos y ventas pagados |
| Reembolsos | Reservas canceladas, con el monto calculado según RN-03 |
| Egresos | Gastos operativos registrados con HU-13 |

## 4. Funcionalidades

**Consulta consolidada (CU-06).** El administrador elige un rango de fechas y ve el total de ingresos separado por hospedaje y tienda, el total de egresos y el balance del período. Puede filtrar por categoría de egreso y por tipo de ingreso.

**Registro de egresos (HU-13).** Cada egreso guarda categoría, fecha, valor y un soporte digital (factura o recibo) cuyo archivo se almacena fuera de la base de datos, que solo conserva la referencia y los metadatos. Editar o eliminar un egreso queda registrado en la auditoría con el usuario que hizo el cambio.

**Informe mensual (HU-01).** Exporta a Excel la relación de ingresos y egresos del mes, con el detalle por concepto, apta para declaraciones y balances.

**Sueldo de recepción (HU-07).** El administrador define el modelo de compensación y el sistema calcula automáticamente el valor para el período indicado.

## 5. Acceso

Los reportes financieros consolidados, los egresos, el informe mensual y el sueldo son exclusivos del rol Administrador. La recepcionista no tiene acceso a la información financiera global.
