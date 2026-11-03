# Gestión del Proyecto — SatoriPMS

## 1. Propósito y Alcance General

El proyecto **SatoriPMS** consiste en el diseño, desarrollo, aseguramiento de calidad y puesta en marcha de un sistema integral de gestión hotelera y reservas automatizadas por WhatsApp para el hotel **Torre Satori** (Sevilla, Valle del Cauca).

### A. Qué Incluye el Alcance del Proyecto
1. **Motor de Reservas y Prevención de Sobreventa:** Control de disponibilidad en tiempo real para las **9 habitaciones de referencia** del hotel, con bloqueo temporal de 15 minutos durante el proceso de compra y restricción definitiva contra cruce de fechas en base de datos.
2. **Chatbot de WhatsApp con Inteligencia Artificial (24/7):** Flujo guiado paso a paso, asistente en lenguaje natural impulsado por inteligencia artificial, cobro de anticipo del 50% o pago del 100%, liquidación de saldos pendientes, cancelación con cálculo de reembolso sobre lo abonado, consulta y captura de reseñas con enlace a Google Maps y transferencia a un recepcionista humano.
3. **Aplicación Web para Recepción y Administración:** Calendario visual de ocupación, registro de llegadas (Check-in) y salidas (Check-out), creación de reservas manuales, bandeja de conversaciones escaladas, **administración completa de habitaciones (crear, editar y eliminar sin reservas pendientes)** y **configuración de eventos especiales y descuentos por fechas**.
4. **Módulo de Tienda Interna e Inventario:** Catálogo de productos de vitrina, registro de ventas de contado o con cargo a la habitación, control de existencias y desactivación segura de productos sin afectar la contabilidad histórica.
5. **Módulo de Facturación, Finanzas y Turnos:** Consolidación de ingresos y gastos operativos, cálculo configurable de turnos de recepción y exportación de informes contables en formato Excel.
6. **Seguridad, Roles y Puesta en Marcha:** Control de acceso diferenciado para Administrador y Recepcionista, cumplimiento de la Ley 1581 de 2012 de protección de datos personales y capacitación presencial en el hotel.

### B. Qué Queda Fuera del Alcance Inicial
- Operación simultánea para múltiples hoteles distintos (la plataforma está hecha a la medida de Torre Satori).
- Integración automática bidireccional con portales externos como Booking o Airbnb (el objetivo estratégico del proyecto es fortalecer el canal de venta directa sin comisiones).
- Emisión de facturación electrónica ante la DIAN (el sistema genera soportes de cuenta internos y el consolidado contable en Excel).

---

## 2. Equipo de Trabajo y Responsabilidades

El desarrollo del proyecto está a cargo de un equipo de ingeniería de tres integrantes bajo metodología ágil Scrum:

| Integrante | Rol Principal | Responsabilidades en el Proyecto |
|---|---|---|
| **Juan José Arias Gallego** | Propietario del Producto (Product Owner) y Desarrollador | Enlace directo con la administración de Torre Satori, definición y validación de reglas de negocio, priorización de entregas y apoyo en base de datos y pruebas. |
| **Esteban Guarín Valencia** | Líder Ágil (Scrum Master) y Arquitecto de Servidor | Diseño y construcción del servidor central (Java / Spring Boot), modelo de base de datos (PostgreSQL), sistema de bloqueos temporales (Redis) y aseguramiento de calidad. |
| **Juan Felipe Garzón Trejos** | Especialista en Interfaz Web y Automatización | Construcción de la aplicación web de recepción y administración (React / TypeScript), orquestación de flujos conversacionales en n8n e integración con inteligencia artificial. |

- **Patrocinador y Cliente Principal:** **Frank Arias Salgado** — Propietario y Administrador de Torre Satori (Sevilla, Valle del Cauca).

---

## 3. Estructura de Desglose de Trabajo y Cronograma por Etapas

El plan de ingeniería comprende **10 semanas de ejecución** divididas en **5 iteraciones (Sprints) de dos semanas cada una**, con una dedicación total de **600 horas de ingeniería** (150 puntos de esfuerzo) más **38 horas de puesta en marcha y capacitación presencial en Sevilla**:

| Etapa / Sprint | Fechas Programadas | Esfuerzo | Entregables Principales para el Hotel |
|---|---|---|---|
| **Sprint 1: Base Tecnológica y Prevención de Sobreventa** | 14 sep – 25 sep 2026 | 30 puntos (120 h) | Infraestructura en contenedores Docker, base de datos del hotel, catálogo inicial de las 9 habitaciones de referencia, doble candado contra sobreventa (bloqueo temporal de 15 minutos y restricción de fechas) y esquema de seguridad por roles. |
| **Sprint 2: Chatbot de WhatsApp, Abonos y Cancelaciones** | 28 sep – 09 oct 2026 | 30 puntos (120 h) | Flujo conversacional de reserva guiada paso a paso, confirmación con pago del 100% o anticipo del 50%, consulta de reserva por código, pago de saldo pendiente, cancelación con política de reembolso sobre lo abonado y transferencia a agente humano. |
| **Sprint 3: Inteligencia Artificial y Operación de Recepción en Web** | 12 oct – 23 oct 2026 | 32 puntos (128 h) | Asistente de reservas con inteligencia artificial en lenguaje natural, calendario interactivo de ocupación en la web, registro de llegadas (Check-in), salidas (Check-out), reservas manuales, administración completa de habitaciones (crear, editar, eliminar) y programación de eventos especiales con descuentos. |
| **Sprint 4: Tienda Interna, Finanzas, Turnos y Reportes en Excel** | 26 oct – 06 nov 2026 | 30 puntos (120 h) | Administración de catálogo e inventario de la tienda interna, cargos de consumos a la habitación, registro de ingresos y gastos operativos, calculadora de turnos de recepción y exportación del balance mensual en Excel. |
| **Sprint 5: Reseñas, Fidelización, Auditoría y Puesta en Marcha** | 09 nov – 20 nov 2026 | 28 puntos (112 h) | Consulta y registro de reseñas con redirección a Google Maps, panel de moderación de opiniones, identificación de clientes frecuentes, historial de auditoría, pruebas integrales de concurrencia y capacitación presencial en Sevilla. |

---

## 4. Gestión de Riesgos del Proyecto

El equipo mantiene una matriz preventiva para anticipar y mitigar los riesgos técnicos, operativos y financieros:

| Código | Riesgo Identificado | Nivel | Estrategia de Prevención y Mitigación |
|---|---|---|---|
| **R-01** | Variación en la tasa de cambio del dólar que encarezca el servidor en la nube o el consumo de mensajería. | Bajo | Uso de infraestructura liviana auto-alojada (~18 USD/mes en total) respaldada por una reserva financiera de contingencia. |
| **R-02** | Demoras en los trámites de verificación comercial de la cuenta oficial de WhatsApp ante Meta. | Medio | Inicio temprano del proceso administrativo con la documentación del hotel y uso de entorno de pruebas funcional durante el desarrollo. |
| **R-03** | Aumento inusual de consultas al asistente de inteligencia artificial en temporadas festivas de Sevilla. | Bajo | Pre-filtrado de menús y comandos rápidos antes de invocar al modelo de inteligencia artificial y configuración de límites por conversación. |
| **R-04** | Ajustes o refinamientos en las políticas de tarifas, eventos especiales, reembolsos o turnos solicitados por el cliente. | Alto | Diseño parametrizable en la aplicación web (edición libre de habitaciones, eventos de descuento y tarifas de turnos sin necesidad de reprogramar el sistema). |
| **R-05** | Intentos simultáneos de reserva sobre la última habitación disponible en fechas de alta demanda. | Medio | Implementación del sistema de doble candado (bloqueo atómico de 15 minutos en memoria rápida con liberación inmediata al cancelar, sumado a la restricción en base de datos). |
| **R-06** | Curva de aprendizaje del personal de recepción al adoptar el nuevo panel web. | Medio | Diseño visual limpio e intuitivo acompañado de una jornada presencial de capacitación y entrega de manuales prácticos en el hotel en Sevilla. |
