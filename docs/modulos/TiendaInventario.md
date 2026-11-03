# Tienda Interna e Inventario — SatoriPMS

## 1. Propósito del Módulo

El módulo de **Tienda Interna e Inventario** permite administrar la vitrina de productos adicionales que ofrece **Torre Satori** en su recepción (bebidas frías, café especial de Sevilla, mecato, artículos de aseo personal y recuerdos), facilitando tanto el registro de consumos cargados a la cuenta de una habitación como las ventas directas en efectivo o transferencia, y manteniendo el control exacto de las existencias en bodega.

---

## 2. Administración del Catálogo de Productos (Rol Administrador)

El **Administrador** gestiona el catálogo de artículos disponibles desde la aplicación web:

1. **Creación y edición de productos:** Permite registrar cada artículo con su nombre comercial (`Nombre del producto : "name"`), su precio unitario de venta vigente (`Precio de venta : "price"`) y la cantidad de unidades disponibles en inventario (`Existencias en inventario : "stock"`).
2. **Abastecimiento de inventario:** Cuando el hotel compra nueva mercancía a sus proveedores, el administrador incrementa la cantidad de unidades disponibles del producto correspondiente.
3. **Alertas visuales de existencias bajas:** El panel resalta automáticamente aquellos productos cuyas unidades disponibles estén próximas a agotarse (por ejemplo, 5 unidades o menos), permitiendo reabastecer la vitrina a tiempo antes de fines de semana o puentes festivos.

---

## 3. Regla de Protección Contable al Retirar Productos

Para garantizar que los informes financieros y las cuentas históricas de meses anteriores nunca se descuadren ni pierdan información:
- **Desactivación lógica en lugar de borrado físico:** Si el administrador decide retirar un producto que ya cuenta con ventas registradas en el historial del hotel, el sistema no elimina el registro de la base de datos; en su lugar, lo marca como inactivo (`Producto activo : "active = false"`).
- **Efecto inmediato:** Un producto inactivo deja de aparecer en el selector de ventas de recepción para evitar nuevos cobros, pero conserva intacto su nombre y trazabilidad en todas las facturas y reportes contables pasados.
- **Congelamiento del precio unitario en cada venta:** Cada vez que se registra un consumo, el sistema guarda en ese registro el precio exacto que tenía el producto en ese momento (`Precio unitario histórico : "unit_price"`). Así, si el administrador sube el precio de una bebida el mes siguiente, los consumos anteriores conservan el valor real al que fueron vendidos.

---

## 4. Registro de Ventas y Consumos en Recepción

El **Recepcionista** (o el Administrador) puede registrar la salida de un producto bajo dos modalidades operativas:

### A. Consumo con Cargo a la Habitación (Huésped Alojado)
1. El recepcionista selecciona la habitación ocupada (lo cual vincula el consumo con la reserva activa mediante `Identificador de reserva : "booking_id"`), elige el producto y digita la cantidad solicitada (`Cantidad consumida : "quantity"`).
2. El sistema verifica que existan unidades suficientes en inventario y descuenta automáticamente la cantidad entregada.
3. El recepcionista indica si el huésped pagó el producto de inmediato o si desea **cargarlo a la cuenta de su habitación**:
   - **Si queda pendiente de pago (`Consumo pagado : "paid = false"`):** El valor se acumula en el estado de cuenta de la habitación y será exigido automáticamente por el sistema al momento de realizar la salida del huésped (Check-out).
   - **Si se paga en el acto (`Consumo pagado : "paid = true"`):** Queda asentado en la reserva como un consumo ya saldado y se suma de inmediato a los ingresos de caja del día.

### B. Venta Directa de Mostrador (Sin Reserva Asociada)
Si un visitante o un huésped que ya cerró su cuenta compra un producto pagándolo de inmediato en recepción:
1. El recepcionista registra la venta sin vincularla a ninguna habitación (`Identificador de reserva : "booking_id = null"`).
2. El consumo se marca automáticamente como pagado (`Consumo pagado : "paid = true"`), se descuentan las unidades del inventario y el ingreso se registra directamente en la contabilidad del hotel bajo la categoría de tienda.
