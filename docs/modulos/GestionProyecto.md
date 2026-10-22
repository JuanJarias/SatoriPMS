# Módulo 11 — Gestión del Proyecto

## 11.1 Metodología y Herramientas

El proyecto se gestiona con Scrum en cinco sprints de dos semanas. El seguimiento se hace en GitHub Projects, con un Milestone por épica y el backlog organizado por historias de usuario y casos de uso. Al cierre de cada sprint se realiza una revisión con el Product Owner y el stakeholder para validar los entregables y reordenar el backlog.

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

## 11.3 Cronograma Scrum

| Sprint | Fechas | Contenido |
|---|---|---|
| 1 | 14/09 al 25/09/2026 | Arquitectura y base de datos, mockups UX/UI y backlog inicial |
| 2 | 28/09 al 09/10/2026 | WhatsApp API, motor de reserva con IA y cancelaciones |
| 3 | 12/10 al 23/10/2026 | Panel de la app web, check-in y check-out, finanzas y sueldos |
| 4 | 26/10 al 06/11/2026 | Módulo de tienda, reseñas y fidelización, y gestión de roles |
| 5 | 09/11 al 20/11/2026 | Pruebas de QA, despliegue en producción, capacitación y cierre |

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
