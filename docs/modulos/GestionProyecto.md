# Módulo 11 — Gestión del Proyecto

## 11.1 Metodología y Herramientas

El proyecto se gestiona bajo el marco ágil Scrum en cinco sprints. El seguimiento en tiempo real y la gestión del backlog se realiza oficialmente en **GitHub Projects**:
* **Tablero Oficial:** [GitHub Projects — SatoriPMS (Project #2)](https://github.com/users/JuanJarias/projects/2)
* **Repositorio y Rama de Trabajo:** [`JuanJarias/SatoriPMS` (rama `feat/database-redis-setup`)](https://github.com/JuanJarias/SatoriPMS/tree/feat/database-redis-setup)

El tablero cuenta con 3 vistas principales:
1. **Backlog y planificación** (Table layout agrupado por Sprint).
2. **Tablero de Progreso** (Board layout por estados: *Backlog*, *In Progress*, *Review*, *Done*).
3. **Cronograma Sprints** (Roadmap layout por fechas de inicio y duración).

Al cierre de cada sprint se realiza una sesión de Sprint Review con el Product Owner y el stakeholder para validar los entregables contra la Definición de Hecho (DoD) y repriorizar el backlog.

## 11.2 Estructura de Desglose de Trabajo (EDT)

La EDT combina dos criterios de descomposición: las fases del ciclo de vida y, dentro de la fase de desarrollo, las seis épicas de los requerimientos.

| # | Fase | Propósito |
|---|---|---|
| 1 | Gestión del Proyecto | Dirigir, planificar y controlar el proyecto de principio a fin |
| 2 | Análisis y Diseño | Traducir los requerimientos en una solución técnica: arquitectura, modelo de datos, flujos conversacionales y mockups |
| 3 | Desarrollo, Épica 1 | Reservas con Chatbot |
| 4 | Desarrollo, Épica 2 | Gestión Operativa (App Web) |
| 5 | Desarrollo, Épica 3 | Facturación y Finanzas |
| 6 | Desarrollo, Épica 4 | Tienda y Ventas |
| 7 | Desarrollo, Épica 5 | Reseñas y Fidelización |
| 8 | Desarrollo, Épica 6 | Administración de Roles |
| 9 | Pruebas y Aseguramiento de Calidad | Verificar el cumplimiento de los requerimientos funcionales y no funcionales |
| 10 | Despliegue e Implementación | Poner el sistema en producción y capacitar al personal |
| 11 | Documentación y Cierre | Dejar el conocimiento documentado y formalizar la entrega |

## 11.3 Cronograma Scrum Oficial (Reorganizado en GitHub Projects)

| Sprint | Fechas Oficiales | Duración | Estado GitHub | Foco Técnico e Issues Clave Asociadas |
|---|---|---|---|---|
| **Sprint 1** | 23/09/2026 al 02/10/2026 | 10 días | **Done** | **Diseño y Arquitectura de la Solución (7 issues):** DU-01 (Arquitectura), HU-00.1 (Conexión WhatsApp-n8n), DU-02 (Mockups UX/UI), DU-03 (Modelo BD relacional), DU-04 (Estrategia de concurrencia), DU-05 (Flujos chatbot), DU-06 (Seguridad y datos). |
| **Sprint 2** | 03/10/2026 al 16/10/2026 | 14 días | **Done** | **Core de Reservas Chatbot WhatsApp (6 issues):** CU-01 (Reservar habitación), CU-01.1 (Disponibilidad por fechas), CU-01.2 (Bloqueo temporal 15 min RN-02), CU-01.4 (Precio total y confirmar), CU-02 (Cancelar en chatbot), HU-08 (Confirmación automática WhatsApp). |
| **Sprint 3** | 17/10/2026 al 30/10/2026 | 14 días | **In Progress** | **Gestión Operativa Web y Asistente IA (11 issues):** CU-03 (Check-in), CU-04 (Check-out consumos), HU-03 (Calendario en tiempo real), HU-03.1 (Reconexión socket y sincronización), CU-08 (Reserva manual), CU-02 (Cancelar reserva web), HU-05 (Rol Recepcionista), HU-11 (Credenciales), HU-06 (Escalamiento a humano), HU-09 (Recomendación IA Gemini), CU-01.3 (Validar capacidad y cargo extra RN-01). |
| **Sprint 4** | 31/10/2026 al 13/11/2026 | 14 días | **Backlog** | **Finanzas, Tienda, Reseñas, Pasarela y Auditoría (13 issues):** CU-01.5 (Pasarela de pago pruebas Colombia), HU-01 (Informe mensual Excel), CU-06 (Ingresos y egresos), HU-07 (Sueldo recepcionista), HU-13 (Egresos operativos), CU-05 (Vender producto tienda), CU-07 (Catálogo inventario), HU-14 (Rotación de stock), HU-02 (Consultar reseñas bot), HU-04 (Dejar reseña post check-out), HU-10 (Panel web reseñas), HU-12 (Huéspedes recurrentes), HU-15 (Log de auditoría). |
| **Sprint 5** | 14/11/2026 al 27/11/2026 | 14 días | **Backlog** | **Aseguramiento de Calidad y Pruebas Transversales (7 issues):** QA-01 (Pruebas unitarias RN-01 a RN-04), QA-02 (Integración chatbot-API-BD-pagos), QA-03 (Pruebas funcionales CU-01 a CU-08), QA-04 (Rendimiento <3s), QA-05 (Concurrencia dos reservas simultáneas), QA-06 (Responsive móvil/escritorio), QA-07 (Usabilidad con usuarios reales). |

## 11.4 Equipo y Roles

| Persona | Rol Scrum | Responsabilidad técnica |
|---|---|---|
| Esteban Guarín Valencia | Scrum Master | Arquitectura del backend, base de datos, infraestructura y gestión de riesgos del equipo |
| Juan José Arias Gallego | Product Owner | Levantamiento y priorización de requerimientos, validación de reglas de negocio y relación con el stakeholder |
| Juan Felipe Garzón Trejos | Development Team | Aplicación web, flujos conversacionales en n8n e integración con el backend |

El stakeholder principal es el propietario del hotel Torre Satori. La definición de reglas de negocio pendientes se acuerda con el Product Owner y el stakeholder, y queda registrada en el módulo de Decisiones Pendientes.

## 11.5 Matriz de Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Baja adopción del personal por resistencia al cambio frente al proceso manual | Media | Alto | Capacitación práctica previa al despliegue e interfaz intuitiva enfocada en usabilidad |
| Dobles reservas simultáneas por concurrencia entre la web y el bot | Baja | Alto | Bloqueo temporal de 15 minutos, validación de inventario en tiempo real en todos los canales y restricción de exclusión en PostgreSQL |
| Fallas en la API de WhatsApp por caídas del servicio externo | Baja | Alto | Escalamiento directo e inmediato a un recepcionista humano |
| Protección de datos sensibles de los huéspedes | Baja | Alto | Cumplimiento de la Ley 1581 de 2012, roles y permisos diferenciados y auditoría de acciones |
| Interpretación incorrecta de respuestas en lenguaje libre | Media | Medio | Uso de Gemini Flash Lite para normalizar respuestas, validación posterior en el backend y posibilidad de corregir en cualquier punto |
| Bloqueo de habitación que no se libera, o que se libera por error | Baja | Alto | Verificación cuidadosa del fin del flujo antes de liberar y bloqueo permanente una vez confirmada la reserva |
| Dependencia de un único proveedor de pasarela de pagos | Baja | Medio | Contrato de integración documentado para facilitar un cambio de proveedor |
| Cambios en las reglas de negocio durante el desarrollo | Alta | Alto | Registro de decisiones pendientes con el stakeholder y revisión en cada sprint |
