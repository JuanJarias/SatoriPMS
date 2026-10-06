# Módulo — Tienda e Inventario

### 1. Requerimientos y Casos de Uso

* **CU-05 (Vender producto):** Venta en mostrador de productos del hotel (snacks, bebidas, souvenirs). Opción de pago inmediato en efectivo/tarjeta o cargo a la cuenta de la habitación reservada para liquidar en el check-out.
* **CU-07 (Administrar catálogo):** Creación, edición de precio, descripción y reabastecimiento de existencias.
* **HU-14 (Rotación de productos):** Reporte de rotación e inventario para identificar productos de mayor y menor salida en periodos específicos.

---

### 2. Reglas de Negocio

* **RN-04 (Inmutabilidad histórica):** Un producto que posea registros de ventas o consumos históricos asociados no puede eliminarse físicamente de la base de datos; únicamente puede ser desactivado (`active = false`) para evitar inconsistencias contables.
* **Validación de stock:** Toda venta o cargo a habitación valida la existencia suficiente en inventario antes de descontar unidades.
