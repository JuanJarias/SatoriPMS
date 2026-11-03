# Catálogo de Diagramas del Sistema — SatoriPMS

Esta carpeta reúne las representaciones visuales de **SatoriPMS**, diseñadas para explicar con claridad cómo está construido el sistema de **Torre Satori**, cómo fluye la información desde que un viajero escribe por WhatsApp hasta que finaliza su estadía y cómo se protegen las habitaciones contra cualquier intento de sobreventa.

---

## Índice de Diagramas Oficiales

| # | Documento | Propósito Principal | Tipo de Diagrama |
|---|---|---|---|
| **01** | [Infraestructura y Servicios](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/01_Infraestructura_Servicios.md) | Muestra cómo se conectan los contenedores locales y en la nube (Base de Datos, Memoria Rápida, Orquestador del Chatbot, Servidor Central y Aplicación Web) con WhatsApp y la Inteligencia Artificial. | Diagrama de Arquitectura y Red (`flowchart TB`) |
| **02** | [Flujo de Reserva por WhatsApp](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/02_Flujo_Reserva_WhatsApp.md) | Detalla paso a paso la experiencia del viajero en WhatsApp (reserva guiada y asistente con inteligencia artificial), el aviso de privacidad, el desglose de recargos y el pago del 50% o 100%. | Diagrama de Secuencia (`sequenceDiagram`) |
| **03** | [Prevención de Sobreventa (Doble Candado)](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/03_Concurrencia_Doble_Candado.md) | Explica cómo el sistema impide que dos personas reserven la misma habitación al mismo tiempo mediante el bloqueo por intervalos de 15 minutos en memoria rápida y la restricción definitiva en base de datos. | Diagrama de Secuencia y Flujo (`sequenceDiagram` + `flowchart LR`) |
| **04** | [Gestión Operativa y Administrativa en la Web](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/04_Gestion_Operativa_Recepcion.md) | Representa las labores diarias de recepción (llegadas, cargos de tienda y salidas) y las funciones exclusivas del administrador (crear, editar y eliminar habitaciones sin reservas activas, y programar eventos especiales con descuentos). | Diagrama de Procesos por Rol (`flowchart TB`) |
| **05** | [Ciclo de Vida de una Reserva y Reembolsos](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/05_Ciclo_Vida_Reserva.md) | Ilustra todos los estados por los que pasa una reserva desde que se cotiza hasta que finaliza o se cancela, detallando el cálculo del reembolso estrictamente sobre el monto abonado. | Diagrama de Estados y Decisión (`stateDiagram-v2` + `flowchart TD`) |

---

## Convenciones de Lectura

- Todos los diagramas están escritos en formato **Mermaid**, lo que permite visualizarlos directamente en GitHub, en editores compatibles con Markdown o exportarlos a imágenes vectoriales de alta resolución.
- Cuando un diagrama incluye el nombre técnico de una operación o estado del sistema, se acompaña siempre de su concepto en español bajo el formato `Concepto en español : "identificador_tecnico"`, garantizando que sea comprensible tanto para el cliente como para el equipo de desarrollo.
