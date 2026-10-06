# Módulo — Facturación y Finanzas

### 1. Requerimientos y Casos de Uso

* **CU-06 (Consultar ingresos y egresos):** Vista consolidada de entradas (hospedaje + tienda) y salidas de dinero por rangos de fecha.
* **HU-01 (Exportar informe a Excel):** Generación y descarga de archivos con la relación contable para declaraciones y balances.
* **HU-07 (Cálculo de sueldo de recepción):** Cálculo automático de la compensación mensual o quincenal según la fórmula pactada por el hotel.
* **HU-13 (Registrar egresos operativos):** Registro de gastos menores (mantenimiento, aseo, compras de inventario) con soporte digital.

---

### 2. Reglas de Negocio

* **RN-05 (Generación de recibos):** Todo pago confirmado por concepto de hospedaje genera un comprobante de recibo inmutable asociado a la reserva.
* **Cálculo de estadía:** El valor total se compone de la suma del valor por noche de las habitaciones seleccionadas, multiplicado por las noches, más los recargos por huéspedes adicionales calculados según RN-01.
