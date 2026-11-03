# Presupuesto y Modelo Financiero — Torre Satori PMS

Documento ejecutivo de presupuesto, estructura de costos, análisis de retorno de inversión y proyección a tres años para la implementación y operación del sistema de gestión hotelera **Torre Satori PMS**, alineado con el libro financiero oficial [`Presupuesto_SatoriPMS.xlsx`](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto_SatoriPMS.xlsx).

---

## 1. Identificación del Proyecto y Parámetros Base

| Concepto | Detalle |
| :--- | :--- |
| **Proyecto** | Torre Satori PMS — Sistema de gestión hotelera con motor de reservas directas, prevención de sobreventas y asistente conversacional en WhatsApp |
| **Cliente / Organización** | Hotel Torre Satori (Sevilla, Valle del Cauca, Colombia) |
| **Capacidad de referencia** | **9 habitaciones** operativas (estándar, superiores y suites) |
| **Alcance de construcción** | **150 puntos de esfuerzo** distribuidos en **5 etapas quincenales** (10 semanas, 600 horas de ingeniería) más **38 horas** de puesta en marcha, configuración inicial y capacitación presencial en Sevilla |
| **Equipo de ingeniería** | 3 profesionales con dedicación de 20 horas semanales por integrante durante 10 semanas |
| **Tarifa horaria de ingeniería** | `$35.000 COP / hora` (`$140.000 COP` por punto de esfuerzo de 4 horas) |
| **Distribución de calidad por entrega** | 55% construcción funcional, 20% pruebas automatizadas y de concurrencia, 10% revisión y ajustes, 10% documentación y 5% despliegue |
| **Tasa de cambio de referencia (TRM)** | `$4.150 COP / USD` |

---

## 2. Resumen Ejecutivo de Indicadores Presupuestales

| # | Indicador Presupuestal Clave | Valor en COP | Equivalente en USD | % del Total Año 1 | Alcance y Criterio Financiero |
| :-: | :--- | ---: | ---: | ---: | :--- |
| **1** | **Inversión de Implementación (CAPEX)** | **$24.685.000** | **$5.948,19** | **87,65%** | Construcción de 150 puntos (`$21.000.000`) + Puesta en marcha y capacitación en Sevilla (`$1.530.000`) + Reserva para imprevistos (`$2.155.000`) |
| **2** | **Costo Mensual de Operación (OPEX Mensual)** | **$289.842 / mes** | **$69,84 / mes** | — | Infraestructura en la nube y dominio (`$54.642 / mes`) + Mensajería WhatsApp, inteligencia artificial y línea móvil (`$55.200 / mes`) + Soporte y mantenimiento técnico (`$180.000 / mes`) |
| **3** | **Costo Anual de Operación (OPEX 12 meses)** | **$3.478.100 / año** | **$838,10 / año** | **12,35%** | Sostenimiento continuo en producción durante los primeros 12 meses tras la entrega |
| **4** | **Costo Total del Primer Año (TCO Año 1)** | **$28.163.100** | **$6.786,29** | **100,00%** | Inversión inicial completa más 12 meses de operación y soporte técnico garantizado |

---

## 3. Desglose Detallado de Costos de Implementación (CAPEX)

### 3.1 Construcción de la Solución (Etapas 1 a 5 — 600 horas)

| Código | Actividad de Ingeniería | Cantidad | Unidad | Costo Unitario (COP) | Costo Total (COP) |
| :-: | :--- | ---: | :---: | ---: | ---: |
| **01** | Construcción y programación de servicios centrales, paneles web y flujos en WhatsApp (55%) | 330 | horas | $35.000 | $11.550.000 |
| **02** | Pruebas unitarias, de integración y de concurrencia contra sobreventa (20%) | 120 | horas | $35.000 | $4.200.000 |
| **03** | Correcciones tras revisión técnica y validación con el cliente (10%) | 60 | horas | $35.000 | $2.100.000 |
| **04** | Documentación funcional, manuales operativos y diagramas (10%) | 60 | horas | $35.000 | $2.100.000 |
| **05** | Despliegue en entorno de validación y contenedores de prueba (5%) | 30 | horas | $35.000 | $1.050.000 |
| **06** | Equipos de cómputo y herramientas de desarrollo del equipo | 3 | entornos | $0 | $0 |
| **07** | Consumo de mensajería de WhatsApp en entorno de prueba (cuota gratuita) | 1.000 | mensajes | $0 | $0 |
| **08** | Consultas de prueba al modelo de inteligencia artificial en desarrollo | 500 | consultas | $0 | $0 |
| **09** | Entorno de pruebas de pasarela de pagos | 1 | entorno | $0 | $0 |
| — | **Subtotal Construcción de la Solución (150 puntos)** | **600** | **horas** | — | **$21.000.000** |

### 3.2 Puesta en Operación, Configuración y Capacitación en Sevilla

| Código | Actividad de Puesta en Marcha | Cantidad | Unidad | Costo Unitario (COP) | Costo Total (COP) |
| :-: | :--- | ---: | :---: | ---: | ---: |
| **10** | Configuración de servidor en la nube de producción, contenedores y túnel seguro | 10 | horas | $35.000 | $350.000 |
| **11** | Gestión y verificación de cuenta comercial oficial en Meta para el número del hotel | 4 | horas | $35.000 | $140.000 |
| **12** | Configuración inicial de las **9 habitaciones**, tarifas, recargos, eventos especiales e inventario | 8 | horas | $35.000 | $280.000 |
| **13** | Capacitación presencial al Administrador y Recepcionistas en el hotel en Sevilla | 16 | horas | $35.000 | $560.000 |
| **14** | Transporte intermunicipal Cali – Sevilla – Cali y alimentación para jornada presencial | 1 | global | $200.000 | $200.000 |
| — | **Subtotal Puesta en Operación y Capacitación en Sevilla** | **38** | **horas + viáticos** | — | **$1.530.000** |

### 3.3 Reserva de Contingencia Calculada por Riesgos

El proyecto contempla una reserva técnica de **`$2.155.000 COP`** (equivalente al **9,56%** de la inversión directa), calculada mediante el método de Valor Monetario Esperado sobre seis riesgos identificados:

| Código | Riesgo Identificado | Causa Potencial | Impacto Estimado (COP) | Probabilidad | Reserva Asignada (COP) | Medida de Mitigación |
| :-: | :--- | :--- | ---: | :-: | ---: | :--- |
| **R-01** | Subida de la tasa de cambio (TRM) | Fluctuación del dólar por encima de `$4.500 COP` en cobros de servidor y servicios en la nube | $700.000 | 30% | $210.000 | Cobertura cambiaria anual sobre servicios cotizados en dólares |
| **R-02** | Demoras en verificación de cuenta en Meta | Trámite extendido de validación comercial del número oficial de WhatsApp del hotel | $900.000 | 25% | $225.000 | Inicio temprano del trámite con la documentación legal del hotel |
| **R-03** | Picos de tráfico de mensajes e inteligencia artificial | Aumento de consultas en temporadas altas de Sevilla (Fiestas del Café, Semana Santa) | $600.000 | 30% | $180.000 | Optimización de instrucciones al modelo de inteligencia artificial y filtros previos |
| **R-04** | Ajustes en reglas de negocio del hotel | Cambios tardíos en parámetros de liquidación de turnos, recargos o descuentos por eventos especiales | $2.000.000 | 35% | $700.000 | Manejo de tarifas, recargos y descuentos mediante parámetros editables por el Administrador |
| **R-05** | Casos límite de concurrencia simultánea | Solicitudes simultáneas sobre las mismas fechas y habitaciones en horas pico | $1.800.000 | 25% | $450.000 | Pruebas automatizadas de estrés, bloqueos atómicos y liberación inmediata de habitaciones |
| **R-06** | Ajustes de usabilidad tras capacitación | Mejoras visuales solicitadas por el personal de recepción durante la puesta en marcha | $1.300.000 | 30% | $390.000 | Validación continua de pantallas y flujos con el cliente en cada etapa |
| — | **Subtotal Reserva de Contingencia** | **Respaldo sujeto a autorización formal del cliente** | — | — | **$2.155.000** | **9,56% sobre la implementación directa** |

---

## 4. Costos Recurrentes de Operación y Mantenimiento (OPEX — 12 Meses)

### 4.1 Infraestructura en la Nube y Dominio

| Código | Servicio / Recurso Operativo | Cantidad | Unidad | Costo Mensual (COP) | Costo Anual (COP) |
| :-: | :--- | ---: | :---: | ---: | ---: |
| **15** | Servidor privado virtual en la nube (Linux, 4 GB RAM, 2 procesadores virtuales, 80 GB disco sólido) | 12 | meses | $49.800 | $597.600 |
| **16** | Dominio web oficial del hotel y gestión de nombres de dominio | 1 | año | $4.842 | $58.100 |
| **17** | Alojamiento de la aplicación web en red de distribución global (Cloudflare Pages) | 12 | meses | $0 | $0 |
| **18** | Almacenamiento en la nube para comprobantes y respaldos hasta 10 GB (Cloudflare R2) | 12 | meses | $0 | $0 |
| — | **Subtotal Infraestructura en la Nube y Dominio** | — | — | **$54.642** | **$655.700** |

### 4.2 Mensajería de WhatsApp, Inteligencia Artificial y Conectividad

| Código | Servicio / Recurso Operativo | Cantidad | Unidad | Costo Mensual (COP) | Costo Anual (COP) |
| :-: | :--- | ---: | :---: | ---: | ---: |
| **19** | Servicio oficial de mensajería Meta WhatsApp Cloud API (primeras 1.000 conversaciones de servicio gratuitas al mes + bolsa de plantillas) | 12 | meses | $24.900 | $298.800 |
| **20** | Servicio de inteligencia artificial Google Gemini Flash Lite para atención en lenguaje natural | 12 | meses | $8.300 | $99.600 |
| **21** | Línea móvil dedicada exclusivamente para el número oficial de WhatsApp del hotel | 12 | meses | $22.000 | $264.000 |
| **22** | Pasarela de pagos en línea (sin cargo fijo mensual; comisión transaccional descontada por operación) | 12 | meses | $0 | $0 |
| — | **Subtotal Mensajería, Inteligencia Artificial y Línea Móvil** | — | — | **$55.200** | **$662.400** |

### 4.3 Soporte y Mantenimiento Técnico Post-Entrega

| Código | Servicio / Recurso Operativo | Cantidad | Unidad | Costo Mensual (COP) | Costo Anual (COP) |
| :-: | :--- | ---: | :---: | ---: | ---: |
| **23** | Bolsa de mantenimiento preventivo, actualizaciones de seguridad y soporte a recepción (4,5 horas/mes a `$36.000 COP/h`) | 54 | horas/año | $162.000 | $1.944.000 |
| **24** | Verificación mensual de copias de seguridad y prueba de restauración de base de datos (0,5 horas/mes a `$36.000 COP/h`) | 6 | horas/año | $18.000 | $216.000 |
| — | **Subtotal Soporte y Mantenimiento Técnico (5 horas/mes)** | **60** | **horas/año** | **$180.000** | **$2.160.000** |

> **Total OPEX Mensual:** **`$289.842 COP / mes`** (`$109.842 COP / mes` en servicios tecnológicos puros + `$180.000 COP / mes` en bolsa de soporte técnico).
> **Total OPEX Anual (12 meses):** **`$3.478.100 COP / año`**.

---

## 5. Planificación por Etapas Quincenales y Estructura de Trabajo

### 5.1 Distribución en 5 Etapas Quincenales (Sprints)

| Etapa | Fechas Programadas | Alcance Funcional Principal | Puntos | Horas | Presupuesto (COP) |
| :--- | :---: | :--- | :-: | :-: | ---: |
| **Etapa 1** | 14 sep – 25 sep 2026 | Estructura central del sistema, contenedores, base de datos, memoria rápida, seguridad y doble candado contra sobreventa | 30 | 120 | $4.200.000 |
| **Etapa 2** | 28 sep – 09 oct 2026 | Asistente en WhatsApp V8, reserva guiada, aviso de privacidad, abono del 50% o 100%, cancelaciones y reembolso sobre lo pagado | 30 | 120 | $4.200.000 |
| **Etapa 3** | 12 oct – 23 oct 2026 | Asistente con inteligencia artificial, panel web, administración de las **9 habitaciones**, eventos especiales, registro de llegada, salida y reserva manual | 30 | 120 | $4.200.000 |
| **Etapa 4** | 26 oct – 06 nov 2026 | Tienda e inventario con historial inmutable, finanzas, gastos operativos, liquidación de turnos e informe contable en Excel | 30 | 120 | $4.200.000 |
| **Etapa 5** | 09 nov – 20 nov 2026 | Reseñas de huéspedes, programa de fidelización, control de permisos por rol, auditoría de operaciones y pruebas de concurrencia | 30 | 120 | $4.200.000 |
| **Total** | **10 semanas** | **Construcción completa del alcance (32 requerimientos funcionales)** | **150** | **600** | **$21.000.000** |

### 5.2 Cruce con la Estructura de Desglose de Trabajo (EDT)

| Fase EDT | Nombre de la Fase | Requerimientos Asociados | Puntos | Horas | Costo Directo (COP) |
| :-: | :--- | :--- | :-: | :-: | ---: |
| **1.0** | Gestión y Coordinación del Proyecto | Seguimiento quincenal, planificación y control de riesgos | — | — | Incluido transversalmente |
| **2.0** | Arquitectura, Base de Datos y Doble Candado | `REQ-01`, `REQ-02`, `REQ-04`, `REQ-05`, `REQ-06` | 23 | 92 | $3.220.000 |
| **3.0** | Módulo 1: Reservas y Asistente en WhatsApp | `REQ-08` a `REQ-14` | 37 | 148 | $5.180.000 |
| **4.0** | Módulo 2: Recepción Web, 9 Habitaciones y Eventos Especiales | `REQ-07`, `REQ-15` a `REQ-18` | 26 | 104 | $3.640.000 |
| **5.0** | Módulo 3: Facturación, Finanzas y Turnos | `REQ-22` a `REQ-25` | 18 | 72 | $2.520.000 |
| **6.0** | Módulo 4: Tienda Interna e Inventario | `REQ-19` a `REQ-21` | 14 | 56 | $1.960.000 |
| **7.0** | Módulo 5: Reseñas y Fidelización de Clientes | `REQ-26` a `REQ-29` | 12 | 48 | $1.680.000 |
| **8.0** | Módulo 6: Seguridad por Roles y Auditoría | `REQ-03`, `REQ-30` | 8 | 32 | $1.120.000 |
| **9.0** | Pruebas de Concurrencia y Aseguramiento de Calidad | `REQ-31` | 6 | 24 | $840.000 |
| **10.0** | Despliegue en Producción y Capacitación en Sevilla | `REQ-32` + Puesta en marcha y viáticos | 6 | 62 | $2.370.000 |
| **11.0** | Documentación Funcional, Manuales y Cierre | Transversal en los criterios de entrega | — | — | Incluido en fases 2.0 a 10.0 |
| — | **Total Implementación Directa (Sin Contingencia)** | **Fases 1.0 a 11.0** | **150** | **638** | **$22.530.000** |

---

## 6. Retorno de Inversión (ROI), Punto de Equilibrio y Proyección a 3 Años

### 6.1 Impacto Económico para el Hotel Torre Satori

Tomando como base las **9 habitaciones** del hotel, una tarifa promedio ponderada de **`$180.000 COP / noche`** y un volumen conservador de **40 reservas mensuales**:

1. **Costo tecnológico por reserva procesada:**
   - El gasto tecnológico puro (`$1.318.100 COP / año` entre servidor, dominio, WhatsApp, inteligencia artificial y línea móvil) dividido entre 480 reservas anuales equivale a **`$2.746 COP por reserva`**, frente a los **`$32.400 COP por noche`** que cobran las agencias externas en comisiones del 18%.
2. **Punto de equilibrio operativo (Break-even):**
   - Con procesar únicamente **3 reservas directas al mes** por WhatsApp (`$97.200 COP` en comisiones evitadas), el hotel cubre prácticamente la totalidad de los costos mensuales de servidor, mensajería e inteligencia artificial (`$109.842 COP / mes`).
3. **Ahorro anual frente a plataformas comerciales de alquiler mensual:**
   - Frente a sistemas hoteleros comerciales cuyo costo ronda los `$330 USD / mes` (`$1.369.500 COP / mes`), el costo operativo total de Torre Satori PMS (`$289.842 COP / mes` incluyendo soporte) genera un ahorro directo de **`$12.955.900 COP al año`**.
4. **Ingresos recuperados por atención automática 24/7:**
   - La captura de al menos **4 reservas mensuales** en horario nocturno o fuera de turno de recepción representa **`$8.640.000 COP anuales`** en ingresos adicionales para el hotel.
5. **Recuperación de la inversión (Payback):**
   - Sumando el ahorro en suscripciones y los ingresos recuperados (`$21.595.900 COP / año` de beneficio neto anual, equivalente a `$1.799.658 COP / mes`), la inversión inicial de `$24.685.000 COP` se recupera en **13,7 meses** de operación.

### 6.2 Proyección del Costo Total de Propiedad (TCO) a 3 Años

Considerando un ajuste anual estimado del 5% en servicios de nube y del 6% (inflación proyectada) en la bolsa de soporte técnico:

| Componente Presupuestal | Año 1 (2026-2027) | Año 2 (2027-2028) | Año 3 (2028-2029) | Total 3 Años (COP) |
| :--- | ---: | ---: | ---: | ---: |
| **Inversión Inicial de Implementación (CAPEX)** | $24.685.000 | $0 | $0 | **$24.685.000** |
| **OPEX: Infraestructura en la Nube y Dominio** | $655.700 | $688.485 | $722.909 | **$2.067.094** |
| **OPEX: Mensajería WhatsApp, IA y Línea Móvil** | $662.400 | $695.520 | $730.296 | **$2.088.216** |
| **OPEX: Bolsa de Soporte y Mantenimiento (5 h/mes)** | $2.160.000 | $2.289.600 | $2.426.976 | **$6.876.576** |
| **Total Gasto Operativo Anual (OPEX)** | **$3.478.100** | **$3.673.605** | **$3.880.181** | **$11.031.886** |
| **Flujo de Caja Anual Total (CAPEX + OPEX)** | **$28.163.100** | **$3.673.605** | **$3.880.181** | **$35.716.886** |
| **Costo Total de Propiedad Acumulado** | **$28.163.100** | **$31.836.705** | **$35.716.886** | — |

---

## 7. Comparativa de Escenarios de Alcance y Respuestas Estratégicas

### 7.1 Comparación de Alternativas de Alcance

| Métrica Presupuestal | Escenario Optimizado (Esencial) | Escenario Base (Recomendado) | Escenario Expandido (Multi-sede) |
| :--- | ---: | ---: | ---: |
| **Alcance funcional** | 135 puntos (540 horas) | **150 puntos (600 horas)** | 195 puntos (780 horas) |
| **Inversión de implementación (CAPEX)** | $21.685.000 COP | **$24.685.000 COP** | $33.450.000 COP |
| **Operación mensual (OPEX Mensual)** | $196.842 COP / mes | **$289.842 COP / mes** | $645.000 COP / mes |
| **Operación anual (OPEX 12 meses)** | $2.362.100 COP / año | **$3.478.100 COP / año** | $7.740.000 COP / año |
| **Costo Total Primer Año (TCO Año 1)** | $24.047.100 COP (-14,6%) | **$28.163.100 COP (Base)** | $41.190.000 COP (+46,2%) |
| **Tiempo de recuperación (Payback)** | 12,1 meses | **13,7 meses** | 18,9 meses |

### 7.2 Preguntas Estratégicas de Viabilidad

1. **¿El alcance actual del sistema es coherente con el costo estimado?**
   Sí. La inversión inicial de **`$24.685.000 COP`** y el costo mensual de sostenimiento de **`$289.842 COP / mes`** cubren íntegramente las necesidades operativas del Hotel Torre Satori: atención y reservas automáticas las 24 horas por WhatsApp, cobro de anticipos del 50% o 100%, reembolsos calculados de forma transparente sobre el monto realmente pagado, panel web de recepción con administración de las **9 habitaciones** y programación de **eventos especiales y descuentos**, y un sistema de doble candado que impide por completo la sobreventa.
2. **¿Qué componente representa el mayor costo y por qué?**
   La construcción e ingeniería del software (**`$21.000.000 COP`**, equivalente al **74,57%** del costo total del primer año). Se justifica porque corresponde a **600 horas de trabajo especializado** para construir, probar y documentar los servicios centrales, el asistente conversacional, la base de datos y los paneles administrativos. En contraste, la infraestructura en la nube y la inteligencia artificial cuestan apenas **`$109.842 COP / mes`**, garantizando que el hotel sea dueño de su plataforma con un costo fijo mensual mínimo.
3. **¿Qué se ajustaría si fuera necesario reducir el presupuesto sin perder el valor principal?**
   En un escenario de ajuste moderado (Escenario Optimizado), se pospondrían para una segunda etapa las funciones administrativas que el hotel puede llevar inicialmente de forma manual (cálculo automático de turnos de recepción, programa de fidelización y moderación web de reseñas), junto con un esquema semipresencial de capacitación y una bolsa de soporte de 2,5 horas al mes. Esto ahorra de inmediato **`$3.000.000 COP`** en la implementación y **`$4.116.000 COP`** en el primer año, manteniendo intactos el asistente de reservas en WhatsApp, el doble candado contra sobreventa, la recepción y el control de tienda y caja.
