# Análisis de Escenarios de Contingencia y Optimización Presupuestal — Torre Satori PMS

Documento de evaluación financiera y operativa ante escenarios de restricción presupuestal, variación de costos de servicios en la nube y cambios de alcance para el proyecto **Torre Satori PMS**, fundamentado en las cifras oficiales del modelo financiero [`Presupuesto_SatoriPMS.xlsx`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto_SatoriPMS.xlsx) y el documento [`Presupuesto.md`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto.md).

---

## 1. Línea Base Presupuestal de Referencia

Antes de evaluar cualquier recorte o contingencia, se establece la línea base aprobada para el sistema con capacidad de referencia de **9 habitaciones**:

| Concepto Presupuestal | Valor Base (COP) | Equivalente (USD) | Composición Principal |
| :--- | ---: | ---: | :--- |
| **Inversión de Implementación (CAPEX Base)** | **$24.685.000** | **$5.948,19** | Construcción de 150 puntos en 600 horas (`$21.000.000`) + Puesta en marcha y capacitación en Sevilla (`$1.530.000`) + Reserva de contingencia (`$2.155.000`) |
| **Costo Mensual de Operación (OPEX Mensual)** | **$289.842 / mes** | **$69,84 / mes** | Servidor en la nube y dominio (`$54.642 / mes`) + Mensajería de WhatsApp, inteligencia artificial y línea móvil (`$55.200 / mes`) + Bolsa de soporte de 5 h/mes (`$180.000 / mes`) |
| **Costo Anual de Operación (OPEX 12 meses)** | **$3.478.100 / año** | **$838,10 / año** | Sostenimiento integral durante el primer año de operación productiva |
| **Costo Total del Primer Año (TCO Año 1)** | **$28.163.100** | **$6.786,29** | Suma de la inversión inicial de implementación y los 12 meses de operación |

---

## 2. Escenario de Crisis 1: Recorte del 30% en el Presupuesto del Proyecto

### 2.1 Planteamiento del Problema

La dirección del hotel enfrenta una restricción severa de flujo de caja y solicita **reducir en un 30% el presupuesto total del primer año** (pasando de **`$28.163.100 COP`** a un techo máximo de **`$19.714.170 COP`**, lo que exige un ahorro total de **`$8.448.930 COP`**) o, de manera equivalente, **reducir en un 30% la inversión inicial de implementación** (pasando de **`$24.685.000 COP`** a **`$17.279.500 COP`**, lo que exige recortar **`$7.405.500 COP`**).

La condición innegociable del negocio es **no comprometer el núcleo transaccional del hotel**: la atención 24/7 por WhatsApp, la prevención absoluta de sobreventas en las **9 habitaciones**, el cobro de anticipos del 50% o 100%, el cálculo de reembolsos sobre el monto realmente pagado y la operación diaria de recepción.

### 2.2 Componentes Intocables (Núcleo Esencial Protegido)

Bajo ninguna circunstancia se recortan los siguientes elementos, pues sin ellos el sistema perdería su razón de ser operativa y comercial:

1. **Doble candado contra sobreventa y liberación inmediata:**
   - Bloqueo temporal de 15 minutos por fechas en memoria rápida durante el proceso de pago, liberación inmediata cuando el usuario cancela o reinicia su sesión, y restricción definitiva contra cruces de fechas en la base de datos.
2. **Motor de reservas y asistente conversacional en WhatsApp (Flujo V8):**
   - Reserva guiada paso a paso, aviso de autorización de datos personales, desglose transparente de tarifa base y recargo por huéspedes adicionales, pago del 50% o 100%, consulta de estado, pago de saldo pendiente, cancelación con reembolso calculado sobre lo efectivamente pagado y transferencia a agente humano.
3. **Operación esencial de recepción y administración de las 9 habitaciones:**
   - Creación, edición y eliminación controlada de habitaciones por el Administrador (impidiendo borrar habitaciones con reservas pendientes o vigentes), programación de eventos especiales y descuentos, calendario de ocupación, registro de llegada, registro de salida y reservas manuales.
4. **Control básico de tienda e ingresos:**
   - Registro de ventas de tienda con cargo a la cuenta de la habitación y consulta consolidada de recaudos.

### 2.3 Plan de Ajuste Escalonado para Lograr el Recorte del 30%

Para alcanzar el ahorro de **`$8.448.930 COP`** en el costo total del primer año sin sacrificar la estabilidad ni la seguridad de las reservas, se ejecuta un ajuste en tres frentes:

| Frente de Ajuste | Acción Concreta | Puntos / Horas Diferidas | Ahorro en Implementación (CAPEX) | Ahorro en Operación Anual (OPEX) | Ahorro Total Año 1 (COP) |
| :--- | :--- | :-: | ---: | ---: | ---: |
| **1. Postergación de módulos administrativos secundarios a Fase 2** | Posponer a una segunda etapa tras el retorno de inversión: liquidación automatizada de turnos de recepción (`REQ-25`, 5 pts), programa automatizado de fidelización (`REQ-29`, 3 pts), panel web de moderación de reseñas (`REQ-28`, 3 pts), reporte avanzado de rotación de tienda (`REQ-21`, 4 pts), bitácora avanzada de auditoría visual (`REQ-30`, 3 pts), exportación contable automatizada (`REQ-24`, 5 pts) y asistente libre con inteligencia artificial (`REQ-14`, 7 pts, conservando el menú guiado completo en WhatsApp) | 30 puntos (120 horas) | $4.200.000 | $99.600 | **$4.299.600** |
| **2. Esquema eficiente de puesta en marcha y capacitación híbrida** | Realizar el despliegue remoto desde Cali y concentrar la capacitación en una jornada intensiva presencial de un día en Sevilla apoyada con manuales interactivos y sesiones virtuales (pasando de 38 a 20 horas y reduciendo viáticos a `$100.000 COP`) | 18 horas | $730.000 | $0 | **$730.000** |
| **3. Liberación controlada de reserva de contingencia y ajuste de bolsa de soporte** | Reducir la reserva de contingencia al 5% tras cerrar el alcance en contratos de etapa fija (ahorro de `$1.105.000 COP`) y ajustar la bolsa de soporte post-entrega de 5 h/mes a 2 h/mes para mantenimiento esencial (ahorro de `$1.296.000 COP / año`), junto con optimización de servidor inicial a `$38.000 COP / mes` (`$1.018.330 COP` adicionales combinados con consumo base gratuito de WhatsApp) | — | $1.105.000 | $2.314.330 | **$3.419.330** |
| **Total Recorte Aplicado** | **Reducción exacta del 30,0% sobre el TCO del Año 1** | **30 puntos + 18 horas** | **$6.035.000** | **$2.413.930** | **$8.448.930** |

### 2.4 Comparativa Antes y Después del Recorte del 30%

| Indicador | Escenario Base Original | Escenario de Crisis (-30%) | Variación |
| :--- | ---: | ---: | ---: |
| **Alcance de ingeniería** | 150 puntos (600 horas) | 120 puntos (480 horas) | -30 puntos (-20% de puntos) |
| **Inversión de implementación (CAPEX)** | $24.685.000 COP | $18.650.000 COP | -$6.035.000 COP (-24,4%) |
| **Costo anual de operación (OPEX 12 meses)** | $3.478.100 COP | $1.064.170 COP | -$2.413.930 COP (-69,4%) |
| **Costo Total Primer Año (TCO Año 1)** | **$28.163.100 COP** | **$19.714.170 COP** | **-$8.448.930 COP (-30,0%)** |
| **Tiempo de recuperación (Payback)** | 13,7 meses | **10,4 meses** | **-3,3 meses más rápido** |

---

## 3. Escenario de Crisis 2: Aumento Súbito en Costos de Nube, Tasa de Cambio o Tráfico de Mensajes

### 3.1 Planteamiento del Problema

Durante una temporada alta en Sevilla (como las Fiestas del Café o Semana Santa), se presentan simultáneamente tres presiones externas:
1. El dólar supera los **`$4.800 COP / USD`** (+15,6% sobre la TRM base de `$4.150 COP`).
2. El tráfico de consultas en WhatsApp se triplica por campañas promocionales y eventos especiales del hotel.
3. El proveedor del servidor en la nube incrementa sus tarifas internacionales en un **25%**.

### 3.2 Evaluación Cuantitativa del Impacto

Gracias a la arquitectura ligera del sistema, la exposición cambiaria y de consumo en la nube es sumamente baja:

| Rubro Expuesto | Costo Mensual Base (COP) | Costo Mensual en Crisis Severa (COP) | Sobrecosto Mensual (COP) | Sobrecosto Anual (COP) |
| :--- | ---: | ---: | ---: | ---: |
| **Servidor privado virtual y dominio** | $54.642 | $78.900 | +$24.258 | +$291.096 |
| **Mensajería Meta WhatsApp Cloud API** | $24.900 | $62.000 | +$37.100 | +$445.200 |
| **Modelo de inteligencia artificial Google Gemini Flash Lite** | $8.300 | $24.900 | +$16.600 | +$199.200 |
| **Total Servicios Expuestos** | **$87.842 / mes** | **$165.800 / mes** | **+$77.958 / mes** | **+$935.496 / año** |

### 3.3 Mecanismos de Contención Financiera y Técnica

1. **Absorción total mediante la reserva de contingencia:**
   - El sobrecosto anual combinado de **`$935.496 COP`** queda cubierto en su totalidad por las partidas **R-01** (`$210.000 COP` por tasa de cambio) y **R-03** (`$180.000 COP` por tráfico de mensajería e inteligencia artificial), junto con el margen operativo que generan las reservas adicionales de temporada alta (basta con **2,4 reservas directas adicionales al mes** para cubrir los `$77.958 COP` de incremento mensual).
2. **Pre-filtrado inteligente antes de consultar la inteligencia artificial:**
   - El flujo conversacional en WhatsApp procesa sin costo alguno en el servidor local todas las respuestas del menú numérico (`1` al `6`), validaciones de fechas, cálculo de tarifas con recargos de personas adicionales y confirmaciones de pago, invocando el modelo de inteligencia artificial únicamente cuando el huésped escribe preguntas abiertas en lenguaje natural.
3. **Aprovechamiento de la ventana gratuita de 24 horas en WhatsApp:**
   - Todas las respuestas automáticas enviadas dentro de las 24 horas posteriores al mensaje del cliente se clasifican como conversaciones de servicio iniciadas por el usuario, las cuales no generan cobro por mensaje dentro del umbral gratuito de Meta.

---

## 4. Escenario de Crisis 3: Solicitud de Nuevas Funcionalidades a Mitad del Proyecto

### 4.1 Situación Analizada

Durante la revisión de la tercera etapa, el cliente solicita incorporar funciones adicionales importantes:
- Administración integral de las **9 habitaciones** desde la aplicación web (crear, editar precios, capacidad y descripción, y eliminar habitaciones verificando que no tengan reservas pendientes o activas).
- Programación de **eventos especiales y temporadas de descuento** sobre tarifas de alojamiento.
- Ajuste fino en el flujo conversacional de WhatsApp para mostrar el desglose del recargo por persona adicional tanto en el flujo guiado como en el flujo con inteligencia artificial, incluir el aviso de privacidad antes de solicitar datos personales y liberar de inmediato el bloqueo temporal de habitaciones cuando el cliente cancela o reinicia su conversación.

### 4.2 Estrategia de Absorción sin Sobrecosto para el Cliente

1. **Incorporación dentro del alcance base mediante parametrización inteligente:**
   - La administración de las 9 habitaciones y la programación de eventos especiales se integran directamente dentro de los requerimientos **`REQ-07`** y **`REQ-15`** de la Etapa 3, reemplazando catálogos estáticos por pantallas editables por el Administrador y utilizando la partida de contingencia **R-04** (`$700.000 COP` prevista precisamente para ajustes en reglas del negocio con el cliente) en caso de requerir horas adicionales de interfaz.
2. **Regla de intercambio de alcance para solicitudes futuras fuera del núcleo:**
   - Si en etapas posteriores surge una solicitud nueva que supere la capacidad de 30 puntos por etapa (por ejemplo, facturación electrónica directa con la DIAN o conexión bidireccional con portales externos), se aplica la política de **presupuesto cerrado por intercambio de puntos**: el cliente elige qué requerimiento deseable de igual puntaje pasa a la segunda fase, o autoriza formalmente una orden de cambio a razón de **`$140.000 COP por punto de esfuerzo`** (`$35.000 COP / hora`).

---

## 5. Conclusión y Dictamen de Resiliencia Financiera

El modelo presupuestal de **Torre Satori PMS** presenta una alta resiliencia financiera por tres razones verificables:

1. **Costos fijos mensuales mínimos:** El gasto tecnológico puro (`$109.842 COP / mes`) se paga solo con **3 reservas directas al mes**, eliminando el riesgo de asfixia financiera en meses de baja ocupación turística en Sevilla.
2. **Modularidad funcional:** El diseño por módulos permite diferir hasta un 20% de los puntos de esfuerzo (funciones secundarias de analítica, turnos o fidelización) y lograr hasta un **30% de ahorro en el primer año** sin tocar jamás el motor de reservas en WhatsApp ni el doble candado contra sobreventa.
3. **Propiedad del activo:** Al finalizar las 5 etapas de construcción, el Hotel Torre Satori es propietario de su sistema sin depender de licencias mensuales en dólares por habitación.
