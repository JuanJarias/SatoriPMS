# Documentación del Proyecto — SatoriPMS

Bienvenido al centro de documentación de **SatoriPMS**, el sistema de gestión hotelera y reservas automatizadas para **Torre Satori** (Sevilla, Valle del Cauca).

Esta carpeta reúne la especificación completa del proyecto: cómo funciona el negocio, qué compone cada módulo del sistema, cómo interactúan sus servicios mediante diagramas visuales y cuál es su modelo financiero.

---

## Propósito y Cómo Utilizar esta Documentación

Esta carpeta reúne la **especificación funcional y de diseño del proyecto** (`modulos/`, `Diagramas/`, `Presupuesto/`, `Reuniones/` y `Actividades/`). Explica con claridad qué debe hacer el sistema, cómo funcionan sus flujos operativos y cuáles son las reglas acordadas para el hotel. Cualquier persona, cliente o integrante del equipo que lea estos documentos comprenderá qué compone el proyecto y cómo debe operar en su totalidad.

El historial de cambios del código se consulta directamente en el registro de versiones del repositorio.

---

## Estructura de la Carpeta `docs/`

### 1. Módulos del Sistema (`docs/modulos/`)
Cada documento describe el funcionamiento previsto, las reglas de negocio y el diseño de un área específica de la plataforma:

- [Generalidades y Núcleo del Negocio](modulos/GeneralidadesNucleo.md): Contexto de Torre Satori, problemáticas que resuelve el sistema, catálogo de capacidades y reglas fundamentales del hotel (tarifas, prevención de sobreventa, reembolsos, inventario, eventos especiales y administración de habitaciones).
- [Chatbot y Atención por WhatsApp](modulos/Chatbot.md): Flujos conversacionales del asistente virtual, reserva guiada paso a paso, asistente con inteligencia artificial en lenguaje natural, pagos del 50% o 100%, consulta y cancelación de reservas, reseñas y transferencia a un recepcionista humano.
- [Aplicación Web (Recepción y Administración)](modulos/AplicacionWeb.md): Panel interactivo del hotel, calendario de ocupación, registro de llegada y salida de huéspedes, reservas manuales, bandeja de conversaciones de WhatsApp, gestión completa de habitaciones (crear, editar y eliminar) y programación de eventos especiales y descuentos.
- [Servicios del Servidor Central (Backend API)](modulos/BackendAPI.md): Descripción de las operaciones que ofrece el servidor central para reservas, habitaciones, bloqueos temporales, pagos, cancelaciones, tienda, finanzas y reseñas, explicadas tanto en lenguaje de negocio como con sus rutas de comunicación.
- [Estructura de Datos (Base de Datos)](modulos/Database.md): Organización de la información almacenada en el sistema (habitaciones, eventos tarifarios, huéspedes, reservas, productos, consumos, movimientos financieros, reseñas y usuarios del personal).
- [Tienda e Inventario](modulos/TiendaInventario.md): Administración de la vitrina de productos del hotel, cargos a la cuenta de la habitación o ventas de contado, alertas de existencias bajas y reglas de trazabilidad.
- [Facturación y Finanzas](modulos/FacturacionFinanzas.md): Liquidación de estadías, recargos por personas adicionales, descuentos por temporadas o eventos especiales, abonos parciales, política de reembolso sobre lo abonado, gastos operativos, cálculo de turnos y exportación contable en Excel.
- [Reseñas y Fidelización](modulos/ResenasFidelizacion.md): Gestión de opiniones de huéspedes mediante redirección oficial y transparente a Google Reviews, reconocimiento de clientes frecuentes y fidelización comercial.
- [Seguridad y Protección de Datos](modulos/Seguridad.md): Control de acceso por roles (Administrador y Recepcionista), protección de credenciales, auditoría de acciones críticas y cumplimiento de la Ley 1581 de 2012 de protección de datos personales.
- [Infraestructura y Despliegue](modulos/Infraestructura.md): Organización de los servicios locales y en la nube, requisitos de operación, copias de seguridad automáticas y procedimiento de recuperación.
- [Diseño Visual y Experiencia de Usuario (UX/UI)](modulos/DiseñoUXUI.md): Identidad visual inspirada en la cultura cafetera de Sevilla, paleta de colores, tipografía y principios de usabilidad del panel web.
- [Gestión del Proyecto](modulos/GestionProyecto.md): Alcance general, desglose de etapas de trabajo, conformación del equipo, cronograma de entregas y matriz de gestión de riesgos.

### 2. Diagramas del Sistema (`docs/Diagramas/`)
- [Índice de Diagramas](Diagramas/README.md): Guía de las representaciones visuales del proyecto:
  1. [Infraestructura y Servicios](Diagramas/01_Infraestructura_Servicios.md)
  2. [Flujo de Reserva por WhatsApp](Diagramas/02_Flujo_Reserva_WhatsApp.md)
  3. [Prevención de Sobreventa (Doble Candado en PostgreSQL)](Diagramas/03_Concurrencia_Doble_Candado.md)
  4. [Gestión Operativa en Recepción](Diagramas/04_Gestion_Operativa_Recepcion.md)
  5. [Ciclo de Vida de una Reserva](Diagramas/05_Ciclo_Vida_Reserva.md)

### 3. Presupuesto y Viabilidad Financiera (`docs/Presupuesto/`)
- [Presupuesto General del Proyecto](Presupuesto/Presupuesto.md): Análisis detallado de los costos de construcción, puesta en marcha en Sevilla, operación mensual en producción y retorno de inversión para las 9 habitaciones de referencia del hotel.
- [Libro Financiero en Excel (`Presupuesto_SatoriPMS.xlsx`)](Presupuesto/Presupuesto_SatoriPMS.xlsx): Modelo financiero dinámico con cinco hojas vinculadas mediante fórmulas (Resumen Ejecutivo, Matriz de Costos, Catálogo de Requerimientos, Escenarios Financieros y Supuestos Validados).
- [Análisis de Escenarios de Crisis Presupuestal](Presupuesto/Actividad4_Crisis_Presupuestal.md): Evaluación de planes de contingencia ante un recorte financiero, un cambio regulatorio de privacidad y la salida imprevista de un integrante técnico.

### 4. Actas y Actividades de Referencia (`docs/Reuniones/` y `docs/Actividades/`)
- [Acta de Reunión con el Cliente](Reuniones/ReunionCliente.md): Minuta ejecutiva y transcripción íntegra de la sesión de levantamiento de requerimientos con el propietario del hotel, Frank Arias Salgado.
- [Enunciado de Escenarios de Crisis Presupuestal (PDF)](<Actividades/ACTIVIDAD 4 (Escenarios de Crisis Presupuestal).pdf>): Documento académico de referencia para la simulación financiera.
- [Plan de Transición y Alistamiento Operativo del Servicio](Actividades/Actividad5_Transicion_Servicio.md): Entregable de la transición del servicio a operación bajo el marco ITIL 4 (versión actualizada al servidor FastAPI, el 11 de noviembre).
- [Entregable en PDF](Actividades/Actividad5_Transicion_Servicio.pdf), [presentación en PDF](Actividades/SatoriPMS_Actividad5_Presentacion.pdf) y [presentación HTML](Actividades/index.html): Materiales de la sustentación.
- [Enunciado de la Transición del Servicio (PDF)](<Actividades/ACTIVIDAD 5. Entregable transición del servicio (Operaciones).pdf>): Documento académico de referencia para el plan de transición.

### 5. Guías de Despliegue y Configuración
- [Guía de Configuración de Variables de Entorno (.env)](Guia_Configuracion_Entorno.md): Manual detallado paso a paso para obtener y configurar cada una de las claves de acceso, identificadores de WhatsApp (Meta for Developers), Inteligencia Artificial (Google AI Studio), pasarela de pagos (Wompi), seguridad del servidor central y credenciales de infraestructura local.

### 6. Planificación y Aprendizaje del Equipo
Material generado durante la migración del servidor central a Python/FastAPI:
- [Roadmap del Sprint 5](ROADMAP.md): Cronograma del 11 al 20 de noviembre de 2026 (plan original; el despliegue en la nube y el flujo sin Redis siguen pendientes).
- [Notas de aprendizaje por lote](aprendizaje/M0.md): Un documento por lote de trabajo (`M0`–`M4` y `P0`–`P6`) con qué hace el cambio, por qué se diseñó así, cómo probarlo y preguntas de defensa.
- [Auditoría y plan de migración](audit/05-plan-migracion.md): Documentos `audit/01` a `audit/12` con el diagnóstico del repositorio Java, el plan de migración y el estado de despliegue. Son registros históricos del momento en que se escribieron.
- [Guía de dominio técnico](GUIA_TELEMATICA.md) y [contexto para consultar una IA externa](CONTEXTO_PARA_IA_EXTERNA.md): Guías de estudio y de contexto del equipo.
- [Referencias del servidor Java anterior](legacy-ref/README.md): Migraciones SQL, contratos de endpoints y el flujo V8 del backend previo, conservados solo como consulta (el código Java está en el tag `legacy-java-backup`).

