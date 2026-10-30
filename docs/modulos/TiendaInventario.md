# Módulo — Tienda e Inventario

## 1. Propósito

La tienda del hotel vende snacks, bebidas y souvenirs, tanto a huéspedes alojados como a clientes de mostrador. El módulo gestiona el catálogo, las existencias, las ventas y los consumos cargados a las habitaciones, y entrega reportes de rotación para decidir qué reabastecer.

## 2. Requerimientos y Casos de Uso

**CU-05, Vender producto.** Venta en mostrador de productos del hotel. El pago puede hacerse de inmediato en efectivo o con tarjeta, o cargarse a la cuenta de la habitación reservada para liquidarse en el check-out.

**CU-07, Administrar catálogo.** Creación de productos, edición de precio y descripción, y reabastecimiento de existencias.

**HU-14, Rotación de productos.** Reporte de rotación e inventario que identifica los productos de mayor y menor salida en periodos específicos.

## 3. Flujos Funcionales

**Alta de producto.** La recepcionista o el administrador ingresa nombre, descripción, precio, categoría, foto de la factura de compra y cantidad inicial de stock. El sistema valida que no exista un producto duplicado con el mismo nombre y que el precio y el stock sean valores numéricos válidos.

**Edición y reabastecimiento.** Se puede modificar el precio, la descripción y la categoría de un producto, y sumar unidades al stock cuando llega mercancía. Cada reabastecimiento suma sobre el stock actual, nunca lo reemplaza.

**Desactivación.** Un producto se retira del catálogo cambiando `active` a falso. Un producto desactivado no aparece en las ventas, pero conserva su historial.

**Venta directa.** La recepcionista selecciona los productos y las cantidades. El sistema valida que haya existencias suficientes, descuenta las unidades vendidas del inventario y registra la venta como pagada.

**Cargo a habitación.** Durante una estadía en curso, la recepcionista selecciona la reserva y registra el consumo con `paid = false`. El sistema valida el stock, descuenta las unidades y deja el consumo asociado a la reserva. En el check-out, los consumos pendientes se consolidan en la cuenta final del huésped.

**Rotación de productos (HU-14).** El reporte lista los productos por cantidad vendida en un rango de fechas, con orden ascendente para ver los de menor salida y descendente para los de mayor salida, junto con el stock disponible de cada uno.

## 4. Reglas de Negocio

**RN-04, inmutabilidad histórica.** Un producto que posea registros de ventas o consumos asociados no puede eliminarse físicamente de la base de datos; únicamente puede desactivarse (`active = false`), para evitar inconsistencias contables.

**Validación de stock.** Toda venta o cargo a habitación valida que haya existencias suficientes en inventario antes de descontar unidades. Si no las hay, la operación se rechaza e informa el stock disponible.

**Precio histórico.** Cada consumo guarda el `unit_price` vigente al momento de la venta, de modo que un cambio posterior de precio no altera los registros anteriores.

## 5. Datos Involucrados

El catálogo vive en la tabla `product` y las ventas y cargos en la tabla `consumption`, ligada a la reserva mediante `booking_id`. El booleano `paid` distingue el consumo pagado de contado del que se liquida en el check-out. Los ingresos de tienda alimentan el módulo de Facturación y Finanzas.
