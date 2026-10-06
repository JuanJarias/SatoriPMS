# Módulo 11 — Gestión del Proyecto

### 11.1 Estructura de Desglose de Trabajo (EDT)

| # | Fase | Propósito |
|---|---|---|
| 1 | Gestión del Proyecto | Dirigir, planificar y controlar el proyecto de principio a fin |
| 2 | Análisis y Diseño | Traducir requerimientos en solución técnica |
| 3 | Desarrollo — Épica 1 | Reservas con Chatbot |
| 4 | Desarrollo — Épica 2 | Gestión Operativa (App Web) |
| 5 | Desarrollo — Épica 3 | Facturación y Finanzas |
| 6 | Desarrollo — Épica 4 | Tienda y Ventas |
| 7 | Desarrollo — Épica 5 | Reseñas y Fidelización |
| 8 | Desarrollo — Épica 6 | Administración de Roles |
| 9 | Pruebas y Aseguramiento de Calidad | Verificar cumplimiento de RF y RNF |
| 10 | Despliegue e Implementación | Poner el sistema en producción |
| 11 | Documentación y Cierre | Dejar el conocimiento documentado y formalizar la entrega |

### 11.2 Cronograma Scrum

| Sprint | Fechas | Contenido |
|---|---|---|
| 1 | 14/09 – 25/09/2026 | Arquitectura y BD, Mockups UX/UI, Backlog inicial |
| 2 | 28/09 – 09/10/2026 | WhatsApp API, Motor IA de reservas, Cancelaciones |
| 3 | 12/10 – 23/10/2026 | Panel App Web, Check-in/Check-out, Finanzas y sueldos |
| 4 | 26/10 – 06/11/2026 | Módulo Tienda, Reseñas y fidelidad, Gestión de roles |
| 5 | 09/11 – 20/11/2026 | Pruebas QA, Despliegue en producción, Capacitación y cierre |

### 11.3 Equipo y Roles Scrum

| Persona | Rol |
|---|---|
| Esteban Guarín V. | Scrum Master |
| Juan José Arias | Product Owner |
| Juan Felipe Garzón | Development Team |

**Herramienta de seguimiento:** GitHub Projects (Milestones por épica).

### 11.4 Matriz de Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Baja adopción del personal (resistencia al cambio manual) | Media | Alto | Capacitación práctica previa al despliegue; interfaz intuitiva enfocada en usabilidad |
| Dobles reservas simultáneas (concurrencia web + bot) | Baja | Alto | Bloqueo temporal de 15 min; validación de inventario en tiempo real en todos los canales |
| Fallas en la API de WhatsApp (caídas de servicio externo) | Baja | Alto | Escalamiento directo e inmediato a recepcionista humano |
| Protección de datos sensibles de huéspedes | Baja | Alto | Cumplimiento estricto de la Ley 1581 de 2012; roles y permisos diferenciados con auditoría |
| Interpretación incorrecta de respuestas en lenguaje libre | Media | Medio | Usar Gemini 2.0 Flash para normalizar respuestas; permitir corrección en cualquier punto |
| Bloqueo de habitación que no se libera, o se libera por error | Baja | Alto | Verificación cuidadosa antes de liberar; bloqueo fijo una vez confirmado el pago |
| Dependencia de un único proveedor de pasarela de pagos | Baja | Medio | Documentar bien el contrato de integración para facilitar un cambio de proveedor |
