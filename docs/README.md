# Documentación del Proyecto — SatoriPMS

Bienvenido al centro de documentación de **SatoriPMS**, el sistema de gestión hotelera y reservas automatizadas para **Torre Satori** (Sevilla, Valle del Cauca).

Esta carpeta reúne la especificación completa del proyecto: cómo funciona el negocio, qué compone cada módulo del sistema, cómo interactúan sus servicios mediante diagramas visuales, cuál es su modelo financiero y cuál es el estado actual de construcción.

---

## Propósito y Cómo Utilizar esta Documentación

La documentación está organizada para cumplir dos funciones claramente diferenciadas:

1. **Especificación Funcional y de Diseño del Proyecto (`modulos/`, `Diagramas/`, `Presupuesto/`, `Reuniones/`):**
   Explica con claridad qué debe hacer el sistema, cómo funcionan sus flujos operativos y cuáles son las reglas acordadas para el hotel. Cualquier persona, cliente o integrante del equipo que lea estos documentos comprenderá qué compone el proyecto y cómo debe operar en su totalidad.
2. **Seguimiento de Avance y Control de Cambios (`EstadoActual.md` y `CambiosPendientes.md`):**
   Concentra exclusivamente el estado real de implementación, las decisiones técnicas adoptadas, el historial de modificaciones y los cambios pendientes de envío al repositorio remoto.

---

## Estructura de la Carpeta `docs/`

### 1. Módulos del Sistema (`docs/modulos/`)
Cada documento describe el funcionamiento previsto, las reglas de negocio y el diseño de un área específica de la plataforma:

- [Generalidades y Núcleo del Negocio](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/GeneralidadesNucleo.md): Contexto de Torre Satori, problemáticas que resuelve el sistema, catálogo de capacidades y reglas fundamentales del hotel (tarifas, prevención de sobreventa, reembolsos, inventario, eventos especiales y administración de habitaciones).
- [Chatbot y Atención por WhatsApp](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Chatbot.md): Flujos conversacionales del asistente virtual, reserva guiada paso a paso, asistente con inteligencia artificial en lenguaje natural, pagos del 50% o 100%, consulta y cancelación de reservas, reseñas y transferencia a un recepcionista humano.
- [Aplicación Web (Recepción y Administración)](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/AplicacionWeb.md): Panel interactivo del hotel, calendario de ocupación, registro de llegada y salida de huéspedes, reservas manuales, bandeja de conversaciones de WhatsApp, gestión completa de habitaciones (crear, editar y eliminar) y programación de eventos especiales y descuentos.
- [Servicios del Servidor Central (Backend API)](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/BackendAPI.md): Descripción de las operaciones que ofrece el servidor central para reservas, habitaciones, bloqueos temporales, pagos, cancelaciones, tienda, finanzas y reseñas, explicadas tanto en lenguaje de negocio como con sus rutas de comunicación.
- [Estructura de Datos (Base de Datos)](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Database.md): Organización de la información almacenada en el sistema (habitaciones, eventos tarifarios, huéspedes, reservas, productos, consumos, movimientos financieros, reseñas y usuarios del personal).
- [Tienda e Inventario](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/TiendaInventario.md): Administración de la vitrina de productos del hotel, cargos a la cuenta de la habitación o ventas de contado, alertas de existencias bajas y reglas de trazabilidad.
- [Facturación y Finanzas](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/FacturacionFinanzas.md): Liquidación de estadías, recargos por personas adicionales, descuentos por temporadas o eventos especiales, abonos parciales, política de reembolso sobre lo abonado, gastos operativos, cálculo de turnos y exportación contable en Excel.
- [Reseñas y Fidelización](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/ResenasFidelizacion.md): Captura de calificaciones de los huéspedes, impulso al posicionamiento en Google Maps, reconocimiento de clientes frecuentes y moderación administrativa.
- [Seguridad y Protección de Datos](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Seguridad.md): Control de acceso por roles (Administrador y Recepcionista), protección de credenciales, auditoría de acciones críticas y cumplimiento de la Ley 1581 de 2012 de protección de datos personales.
- [Infraestructura y Despliegue](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/Infraestructura.md): Organización de los servicios locales y en la nube, requisitos de operación, copias de seguridad automáticas y procedimiento de recuperación.
- [Diseño Visual y Experiencia de Usuario (UX/UI)](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/DiseñoUXUI.md): Identidad visual inspirada en la cultura cafetera de Sevilla, paleta de colores, tipografía y principios de usabilidad del panel web.
- [Gestión del Proyecto](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/GestionProyecto.md): Alcance general, desglose de etapas de trabajo, conformación del equipo, cronograma de entregas y matriz de gestión de riesgos.

### 2. Seguimiento del Proyecto (`docs/modulos/EstadoActual.md` y `docs/CambiosPendientes.md`)
- [Estado Actual del Proyecto](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/EstadoActual.md): Único documento oficial de seguimiento técnico y administrativo. Contiene el resumen ejecutivo, el estado verificado de cada componente y documento, las discrepancias identificadas, los trabajos pendientes, el historial de cambios y el registro de decisiones.
- [Cambios Pendientes de Envío](file:///home/guarinve/Documentos/SatoriPMS/docs/CambiosPendientes.md): Registro organizado por commit de todas las modificaciones realizadas localmente desde la última sincronización con el repositorio remoto.

### 3. Diagramas del Sistema (`docs/Diagramas/`)
- [Índice de Diagramas](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/README.md): Guía de las representaciones visuales del proyecto:
  1. [Infraestructura y Servicios](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/01_Infraestructura_Servicios.md)
  2. [Flujo de Reserva por WhatsApp](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/02_Flujo_Reserva_WhatsApp.md)
  3. [Prevención de Sobreventa (Doble Candado)](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/03_Concurrencia_Doble_Candado.md)
  4. [Gestión Operativa en Recepción](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/04_Gestion_Operativa_Recepcion.md)
  5. [Ciclo de Vida de una Reserva](file:///home/guarinve/Documentos/SatoriPMS/docs/Diagramas/05_Ciclo_Vida_Reserva.md)

### 4. Presupuesto y Viabilidad Financiera (`docs/Presupuesto/`)
- [Presupuesto General del Proyecto](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto.md): Análisis detallado de los costos de construcción, puesta en marcha en Sevilla, operación mensual en producción y retorno de inversión para las 9 habitaciones de referencia del hotel.
- [Libro Financiero en Excel (`Presupuesto_SatoriPMS.xlsx`)](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Presupuesto_SatoriPMS.xlsx): Modelo financiero dinámico con cinco hojas vinculadas mediante fórmulas (Resumen Ejecutivo, Matriz de Costos, Catálogo de Requerimientos, Escenarios Financieros y Supuestos Validados).
- [Análisis de Escenarios de Crisis Presupuestal](file:///home/guarinve/Documentos/SatoriPMS/docs/Presupuesto/Actividad4_Crisis_Presupuestal.md): Evaluación de planes de contingencia ante un recorte financiero, un cambio regulatorio de privacidad y la salida imprevista de un integrante técnico.

### 5. Actas y Actividades de Referencia (`docs/Reuniones/` y `docs/Actividades/`)
- [Acta de Reunión con el Cliente](file:///home/guarinve/Documentos/SatoriPMS/docs/Reuniones/ReunionCliente.md): Minuta ejecutiva y transcripción íntegra de la sesión de levantamiento de requerimientos con el propietario del hotel, Frank Arias Salgado.
- [Enunciado de Escenarios de Crisis Presupuestal (PDF)](file:///home/guarinve/Documentos/SatoriPMS/docs/Actividades/ACTIVIDAD%204%20(Escenarios%20de%20Crisis%20Presupuestal).pdf): Documento académico de referencia para la simulación financiera.
