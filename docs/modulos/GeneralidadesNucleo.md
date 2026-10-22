# Módulo 1 — Generalidades y Núcleo del Proyecto

## 1.1 Contexto del Sistema

Torre Satori es un hotel familiar pequeño ubicado en Sevilla (Valle del Cauca). Su operación completa (reservas, control de habitaciones, tienda y finanzas) se gestionaba de forma manual: las reservas se coordinaban por WhatsApp o presencialmente, sin registro estructurado de huéspedes, sin control confiable del estado de las habitaciones y sin visibilidad operativa consolidada del negocio.

Los problemas que SatoriPMS resuelve son cuatro: tiempo perdido en tareas repetitivas que pueden automatizarse, riesgo de dobles reservas y de habitaciones no liberadas a tiempo, ausencia de trazabilidad histórica de clientes (lo que impide fidelizar o analizar consumo) y falta de visibilidad sobre el estado real del negocio (ocupación, temporadas, rotación de productos).

Las alternativas comerciales existentes (Oracle Hospitality OPERA Cloud, Cloudbeds, Mews) están pensadas para hoteles medianos o grandes y no ofrecen un flujo centrado en WhatsApp, que es el canal real de llegada de reservas de este hotel.

**SatoriPMS** es un *Property Management System* que centraliza y automatiza la operación diaria del hotel a través de dos canales: un **chatbot de WhatsApp**, canal principal de los huéspedes, y una **aplicación web** para recepción y administración. Ambos se apoyan en un único backend que concentra las reglas de negocio y es la fuente de verdad de disponibilidad, precios y estados.

## 1.2 Objetivos del Proyecto

**Objetivo general.** Automatizar y centralizar la operación diaria de Torre Satori (reservas, check-in y check-out, tienda y reseñas) mediante un canal conversacional en WhatsApp y una aplicación web que compartan una única fuente de disponibilidad y de reglas de negocio, reduciendo el trabajo manual repetitivo y el riesgo de errores operativos.

**Objetivos específicos.**

1. Automatizar el ciclo reserva, check-in y check-out, con validación de disponibilidad en tiempo real desde ambos canales.
2. Prevenir dobles reservas mediante bloqueo temporal y restricciones transaccionales a nivel de base de datos.
3. Ofrecer atención conversacional disponible las 24 horas sin exigir al huésped instalar una aplicación adicional.
4. Diferenciar roles operativos (Administrador y Recepcionista) con trazabilidad completa de las acciones ejecutadas.
5. Construir un histórico propio de datos operativos (ocupación, huéspedes, consumo de tienda) como insumo para decisiones de operación y servicio.
6. Habilitar reseñas de huéspedes y reconocimiento de huéspedes recurrentes para apoyar la fidelización.
7. Permitir el escalamiento fluido de la conversación del chatbot hacia un recepcionista humano cuando el caso lo requiera.

## 1.3 Alcance

**Dentro del alcance (v1).**

- Chatbot de WhatsApp: consulta de disponibilidad, reserva guiada paso a paso, reserva asistida por IA, bloqueo temporal de habitaciones, abono del 50 % o pago total, consulta de reserva por código, pago del saldo pendiente, cancelación con reembolso según política, escalamiento a agente humano y reseñas (consulta y captura con redirección a Google).
- Aplicación web: panel de habitaciones y calendario, check-in y check-out, reservas manuales (crear, modificar y cancelar), centro de conversaciones, tienda (catálogo, ventas e inventario), finanzas (ingresos, egresos e informes), reseñas, administración de usuarios y roles, y auditoría.
- Backend único (monolito modular con arquitectura hexagonal) como fuente de verdad de reglas y datos para ambos canales.
- Base de datos relacional transaccional (PostgreSQL) y Redis para sesiones conversacionales y bloqueos temporales.

**Fuera del alcance de la primera versión.**

- Arquitectura de microservicios.
- Operación multi-hotel o multi-tenant (posibilidad futura).
- Formularios nativos de WhatsApp Flows con selector de calendario (idea a futuro).

## 1.4 Stakeholders y Usuarios

| Actor | Rol en el sistema |
|---|---|
| Hotel familiar Torre Satori (propietario) | Stakeholder principal; define los requerimientos del negocio |
| Otros hoteles pequeños | Stakeholders secundarios; adopción potencial futura del producto |
| Administrador | Usuario de la app web con visibilidad global: usuarios, precios y políticas, auditoría y reportes financieros |
| Recepcionista | Usuario operativo diario de la app web: reservas, check-in y check-out, tienda y conversaciones escaladas |
| Huésped | Usuario final del canal WhatsApp |

## 1.5 Épicas, Casos de Uso e Historias de Usuario

| Épica | Casos de uso e historias de usuario |
|---|---|
| 1. Reservas con Chatbot | CU-01 Reservar habitación; CU-02 Revisar o cancelar reserva; HU-06 Escalar a agente; HU-08 Confirmación automática por WhatsApp tras el pago; HU-09 Reserva asistida por IA |
| 2. Gestión Operativa (App Web) | CU-03 Check-in; CU-04 Check-out; CU-08 Reserva manual; HU-03 Calendario en tiempo real |
| 3. Facturación y Finanzas | CU-06 Consultar ingresos y egresos; HU-01 Exportar informe; HU-07 Cálculo de sueldo; HU-13 Registrar egresos |
| 4. Tienda y Ventas | CU-05 Vender producto; CU-07 Administrar catálogo; HU-14 Rotación de productos |
| 5. Reseñas y Fidelización | HU-02 Consultar reseñas; HU-04 Dejar reseña; HU-10 Panel de reseñas; HU-12 Huésped recurrente |
| 6. Administración de Roles | HU-05 Roles y permisos; HU-11 Recuperación de contraseña; HU-15 Auditoría |

## 1.6 Requerimientos No Funcionales

| RNF | Definición |
|---|---|
| Disponibilidad | El sistema está disponible las 24 horas, porque las reservas llegan en cualquier momento por WhatsApp |
| Seguridad y protección de datos | Cumplimiento de la Ley 1581 de 2012 de Colombia, detallado en el módulo de Seguridad |
| Usabilidad | La interacción por chatbot se completa sin instalar una aplicación adicional |
| Rendimiento | La validación de disponibilidad responde en menos de 3 segundos |
| Concurrencia | Se evita la doble reserva simultánea mediante bloqueo temporal (RN-02) y restricción en base de datos |
| Compatibilidad | La app web funciona en navegadores de escritorio y en dispositivos móviles |
| Mantenibilidad | Agregar nuevos tipos de habitación o reglas de precio no exige cambios estructurales mayores |

## 1.7 Reglas de Negocio Consolidadas

**RN-01. Capacidad y cobro extra.** La capacidad se valida con un tope combinado: la suma de adultos y niños no puede superar la capacidad máxima total de las habitaciones seleccionadas, en cuyo caso la reserva se rechaza. Si la suma supera la capacidad base pero no la máxima, se cobra automáticamente un cargo adicional por huésped extra por noche, calculado con el valor `extra_guest_price` de cada habitación.

**RN-02. Bloqueo temporal.** Al elegir una o más habitaciones se bloquean temporalmente por 15 minutos mientras el huésped completa sus datos y el pago. Al confirmarse la reserva, el bloqueo temporal desaparece y la habitación queda reservada durante toda la estadía mediante la restricción de exclusión de PostgreSQL. Si el flujo se interrumpe sin llegar a la confirmación (por inactividad, porque el huésped termina la conversación o porque elige no reservar), el bloqueo se libera. Antes de liberar se verifica que el flujo realmente terminó, para no liberar por error una reserva en curso. La implementación usa Redis con scripts Lua (`RedisLockService`) y un TTL de 900 segundos.

**RN-03. Cancelación y reembolso escalonado.** El reembolso se calcula sobre el monto efectivamente pagado (`paid_amount`) según las horas restantes hasta el check-in, fijado a las 15:00 del día de llegada. Con más de 72 horas de anticipación se reembolsa el 100 %; entre 24 y 72 horas, el 50 %; con menos de 24 horas o en caso de no-show, el 0 %. La cancelación no elimina la reserva: cambia su estado a `cancelled` y libera las habitaciones.

**RN-04. Inmutabilidad de productos con historia.** Un producto con ventas o consumos históricos asociados no puede eliminarse; solo puede desactivarse.

**RN-05. Recibo.** Toda reserva pagada genera un recibo inmutable almacenado en el sistema y asociado a la reserva. Toda reserva confirmada genera además un código de grupo único que identifica la reserva ante el huésped.

**RN-06. Duración de la estadía.** Toda estadía respeta una duración mínima y máxima de noches definida por el hotel.

## 1.8 Ecosistema Tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Java 21, Spring Boot (Spring Data JPA, Spring Data Redis, Flyway, springdoc-openapi) |
| Base de datos | PostgreSQL 16 con extensión `btree_gist` |
| Caché, sesión conversacional y bloqueos | Redis 7 |
| Orquestación conversacional | n8n autoalojado |
| Canal de mensajería | WhatsApp Business Cloud API, integración directa con Meta sin intermediario |
| Pasarela de pagos | MercadoPago (Sandbox para desarrollo) |
| IA e interpretación de mensajes | Google Gemini Flash Lite |
| Frontend | React, Vite, TanStack Query, react-router-dom y Tailwind CSS |
| Tiempo real | WebSocket con protocolo STOMP |
| Autenticación | JWT |
| Documentación de API | OpenAPI y Swagger |
| Control de versiones de esquema | Flyway |
| Contenedores | Docker Compose |
| Seguimiento de trabajo | GitHub Projects con Milestones por épica |

**Convención de idioma.** Todo el código del proyecto (variables, funciones, tablas y endpoints) se escribe en inglés. Todo el contenido que ve el usuario final (mensajes del chatbot y textos de la aplicación web) se escribe en español.

## 1.9 Principios de Diseño

El backend es el único dueño de las reglas de negocio: disponibilidad, precios, capacidad, estados de reserva y reembolsos se calculan y validan siempre allí. n8n solo orquesta la conversación y presenta los resultados; la aplicación web solo presenta y captura datos. La IA interpreta lenguaje libre y redacta conversaciones cuando se le asigna ese rol, pero nunca confirma disponibilidad, precios ni reservas por sí misma: toda mutación pasa por el backend y ocurre por una decisión explícita del huésped. Una reserva tiene la misma estructura en la base de datos sin importar su canal de origen (chatbot o app web).

## 1.10 Mapa de la Documentación

| Módulo | Contenido |
|---|---|
| Generalidades y Núcleo | Contexto, objetivos, alcance, reglas de negocio y stack |
| Chatbot de WhatsApp | Flujos conversacionales, sesión, rol de la IA, escalamiento |
| Backend y API | Arquitectura, módulos lógicos, integraciones y contrato REST |
| Base de Datos | Modelo de datos, restricciones y migraciones |
| Aplicación Web | Vistas, roles y operación de recepción y administración |
| Tienda e Inventario | Catálogo, ventas y rotación |
| Facturación y Finanzas | Ingresos, egresos, informes y sueldo |
| Reseñas y Fidelización | Reseñas locales y en Google, huésped recurrente |
| Seguridad | Autenticación, auditoría y protección de datos |
| Infraestructura | Contenedores, variables de entorno y despliegue |
| Diseño UX/UI | Principios de experiencia en WhatsApp y web |
| Gestión del Proyecto | EDT, cronograma, equipo y riesgos |
| Decisiones Pendientes | Definiciones por acordar con el stakeholder |
| Estado Actual | Único módulo con el avance real del proyecto |
