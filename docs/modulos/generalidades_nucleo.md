# Módulo 1 — Generalidades y Núcleo del Proyecto

### 1.1 Contexto del Sistema

Torre Satori es un hotel familiar pequeño ubicado en Sevilla (Valle del Cauca), cuya operación completa —reservas, control de habitaciones, tienda y finanzas— se gestiona hoy de forma manual: reservas coordinadas por WhatsApp o presencialmente, sin registro estructurado de huéspedes, sin control confiable del estado de las habitaciones y sin visibilidad operativa consolidada del negocio.

Los problemas identificados son:
- Tiempo perdido en tareas repetitivas que podrían automatizarse.
- Riesgo de dobles reservas y habitaciones no liberadas a tiempo.
- Cero trazabilidad histórica de clientes (impide fidelización o análisis de consumo).
- Falta de visibilidad operativa sobre el estado real del negocio (ocupación, temporadas, rotación de productos).

Las alternativas comerciales existentes (Oracle Hospitality OPERA Cloud, Cloudbeds, Mews) están pensadas para hoteles medianos o grandes y no ofrecen un flujo centrado en WhatsApp, que es el canal real de llegada de reservas para este hotel.

**SatoriPMS** es la respuesta propuesta: un *Property Management System* (PMS) que centraliza y automatiza la operación diaria del hotel a través de dos canales —un **chatbot de WhatsApp** (canal principal de huéspedes) y una **aplicación web** (recepción/administración)— apoyados en un backend único que concentra las reglas de negocio.

### 1.2 Objetivos del Proyecto

**Objetivo general:** automatizar y centralizar la operación diaria de Torre Satori (reservas, check-in/check-out, tienda y reseñas) mediante un canal conversacional (WhatsApp) y una aplicación web que compartan una única fuente de disponibilidad y de reglas de negocio, reduciendo el trabajo manual repetitivo y el riesgo de errores operativos.

**Objetivos específicos:**
1. Automatizar el ciclo reserva → check-in → check-out, con validación de disponibilidad en tiempo real desde ambos canales.
2. Prevenir dobles reservas mediante bloqueo temporal transaccional y restricciones a nivel de base de datos.
3. Ofrecer atención conversacional disponible 24/7 sin exigir al huésped instalar una aplicación adicional.
4. Diferenciar roles operativos (Administrador / Recepcionista) con trazabilidad completa de las acciones ejecutadas en el sistema.
5. Construir un histórico propio de datos operativos —ocupación, huéspedes, consumo de tienda— hoy inexistente, como insumo para decisiones de operación y servicio.
6. Habilitar reseñas de huéspedes y reconocimiento de huéspedes recurrentes para apoyar la fidelización.
7. Permitir el escalamiento fluido de la conversación del chatbot hacia un recepcionista humano cuando el caso lo requiera.

### 1.3 Alcance

**Dentro del alcance (v1):**
- Chatbot de WhatsApp: consulta de disponibilidad, reserva guiada, reserva asistida por IA, bloqueo temporal, cancelación con reembolso por política, escalamiento a agente humano, reseñas (consulta y captura).
- Aplicación web: panel de habitaciones/calendario, check-in/check-out, reservas manuales (crear/modificar/cancelar), tienda (catálogo, ventas, inventario), finanzas (ingresos/egresos, informes), reseñas, administración de usuarios/roles, auditoría.
- Backend único (monolito modular, arquitectura hexagonal) como fuente de verdad de reglas y datos para ambos canales.
- Base de datos relacional transaccional (PostgreSQL) + Redis para sesión conversacional.

**Fuera del alcance de la primera versión:**
- Arquitectura de microservicios.
- Operación multi-hotel / multi-tenant (posibilidad futura, no alcance actual).
- Formularios nativos de WhatsApp Flows con selector de calendario (idea a futuro).

### 1.4 Stakeholders

| Stakeholder | Rol |
|---|---|
| Hotel familiar Torre Satori (propietario) | Stakeholder principal — define los requerimientos del negocio |
| Otros hoteles pequeños | Stakeholders secundarios — adopción potencial futura del producto |

### 1.5 Épicas, Casos de Uso e Historias de Usuario

| Épica | Casos de uso / Historias de usuario |
|---|---|
| 1. Reservas con Chatbot | CU-01 Reservar habitación · CU-02 Revisar o Cancelar reserva · HU-06 Escalar a agente · HU-08 Confirmación automática por WhatsApp tras pago · HU-09 Recomendación asistida por IA |
| 2. Gestión Operativa (App Web) | CU-03 Check-in · CU-04 Check-out · CU-08 Reserva manual · HU-03 Calendario en tiempo real |
| 3. Facturación y Finanzas | CU-06 Consultar ingresos/egresos · HU-01 Exportar informe · HU-07 Cálculo de sueldo · HU-13 Registrar egresos |
| 4. Tienda y Ventas | CU-05 Vender producto · CU-07 Administrar catálogo · HU-14 Rotación de productos |
| 5. Reseñas y Fidelización | HU-02 Consultar reseñas · HU-04 Dejar reseña · HU-10 Panel de reseñas · HU-12 Huésped recurrente |
| 6. Administración de Roles | HU-05 Roles y permisos · HU-11 Recuperación de contraseña · HU-15 Auditoría |

### 1.6 Requerimientos No Funcionales (RNF)

| RNF | Definición |
|---|---|
| Disponibilidad | Sistema disponible 24/7 (las reservas llegan en cualquier momento vía WhatsApp) |
| Seguridad y protección de datos | Cumplimiento de la Ley 1581 de 2012 (Colombia) — ver Módulo 6 |
| Usabilidad | La interacción por chatbot debe completarse sin instalar una app adicional |
| Rendimiento | La validación de disponibilidad debe responder en menos de 3 segundos |
| Concurrencia | Debe evitarse la condición de doble reserva simultánea (bloqueo temporal, RN-02) |
| Compatibilidad | La app web debe funcionar en navegadores de escritorio y dispositivos móviles |
| Mantenibilidad | Debe poderse agregar nuevos tipos de habitación o reglas de precio sin cambios estructurales mayores |

### 1.7 Reglas de Negocio Consolidadas

| Regla | Definición |
|---|---|
| **RN-01** | Si el número de personas supera la capacidad máxima de la habitación → se rechaza. Si supera la capacidad base pero no la máxima → se cobra un cargo adicional por persona extra. |
| **RN-02** | Al elegir una o más habitaciones se bloquean temporalmente por 15 minutos mientras se completa el pago. Al confirmarse el pago, el bloqueo deja de ser temporal y la habitación queda reservada durante toda la estadía. Si el flujo de reserva se interrumpe sin llegar al pago (por inactividad o porque el huésped lo corta), el bloqueo temporal debe liberarse — verificando cuidadosamente que el flujo realmente terminó, para no liberar por error una reserva en curso. **Implementación decidida:** Redis con Lua scripts (`RedisLockService`) y TTL de 900 segundos (15 minutos). |
| **RN-03** | Cancelación con reembolso escalonado: más de 72 horas antes → 100 %; entre 24 y 72 horas → 50 %; menos de 24 horas o *no-show* → 0 %. |
| **RN-04** | Un producto con ventas históricas asociadas no puede eliminarse, solo desactivarse. |
| **RN-05** | Toda reserva pagada debe generar un recibo almacenado en el sistema y asociado a la reserva. |
| **RN-06** | Toda estadía debe respetar una duración mínima y máxima de noches definida por el hotel. |

### 1.8 Ecosistema Tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Java 21, Spring Boot (Spring Data JPA, Spring Data Redis, Flyway, springdoc-openapi) |
| Base de datos | PostgreSQL 16 + extensión `btree_gist` |
| Caché / sesión conversacional | Redis 7 |
| Orquestación conversacional | n8n (contenedor autoalojado) |
| Canal de mensajería | WhatsApp Business Cloud API (integración directa con Meta, sin intermediario) |
| Pasarela de pagos | MercadoPago (Sandbox para desarrollo) |
| IA / Interpretación | Google Gemini 2.0 Flash |
| Frontend | React + Vite |
| Autenticación | JWT |
| Documentación de API | OpenAPI/Swagger |
| Control de versiones de esquema | Flyway |
| Seguimiento de trabajo | GitHub Projects / Milestones |

**Convención de idioma:** todo el código del proyecto (nombres de variables, funciones, tablas, endpoints) se escribe en inglés. Todo el contenido que ve el usuario final —mensajes del chatbot, textos de la aplicación web— se escribe en español.
