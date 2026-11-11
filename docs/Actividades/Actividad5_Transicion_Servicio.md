# Plan de Transición y Alistamiento Operativo del Servicio — Torre Satori PMS
## Informe Ejecutivo de Entrega y Puesta en Servicio (Marco ITIL 4 — Entregable Final)

---

## 1. Información General y Control del Documento

- **Proyecto:** Torre Satori PMS (Property Management System Integral, Motor Conversacional de Reservas y Gestión Operativa)
- **Organización Beneficiaria / Cliente:** Hotel Boutique Torre Satori (Sevilla, Valle del Cauca, Colombia)
- **Versión de Entrega:** 1.0.0 (Producto Final Integral — Listo para Operación)
- **Fase del Ciclo de Vida ITIL 4:** Diseño y Transición del Servicio (*Service Design & Transition*)
- **Estado de la Entrega:** Autorizado para Puesta en Servicio en Modalidad de Piloto Controlado (Marcha Blanca)
- **Fecha de Emisión:** Noviembre de 2026
- **Equipo de Dirección e Ingeniería:**
  - **Esteban Guarín Valencia** — *Scrum Master* (Dirección de Gobernanza, Gestión de Cambios, Plan de Despliegue y Pruebas de Recuperación)
  - **Juan José Arias Gallego** — *Product Owner* (Definición del Alcance de Negocio, Criterios de Aceptación, Validación de Usuario y Cierre Operativo)
  - **Juan Felipe Garzón** — *Development Team* (Arquitectura de Software, Doble Candado Concurrente, Módulos de Operación y Pruebas Técnicas)

---

## Componente 1. Definición del Servicio y Alcance de la Entrega

### 1.1 Nombre y Propósito del Servicio

- **Nombre Oficial del Servicio:** Plataforma Integral de Gestión Hotelera, Automatización Conversacional y Experiencia Torre Satori PMS.
- **Propósito Estratégico:** Proporcionar una solución tecnológica unificada de alto rendimiento que digitalice y automatice de extremo a extremo las operaciones de Torre Satori Hotel Boutique. El servicio articula la atención ininterrumpida 24/7 y la reserva multicanal vía WhatsApp sin riesgo de sobreventa, junto a un panel web moderno con autenticación segura en dos niveles (Administrador y Recepción), administración dinámica del inventario de habitaciones, integración completa de la cafetería y restaurante (*Salgados Café*) con pedidos cargadas a la cuenta del huésped, y un motor de eventos y temporadas con tarifas dinámicas.

### 1.2 Necesidad de Negocio y Problemas Resueltos

1. **Atención Descentralizada y Pérdida de Clientes Nocturnos:**
   - *Situación previa:* La atención al cliente y la cotización dependían de teléfonos personales de recepción o atención física en mostrador, perdiendo ventas de viajeros que consultaban de noche o durante fines de semana.
   - *Solución entregada:* Motor conversacional automatizado 24/7 sobre WhatsApp Cloud API asistido por inteligencia artificial en lenguaje natural, capaz de consultar disponibilidad en tiempo real, cotizar con exactitud y formalizar reservas al instante.
2. **Riesgo Crítico de Sobreventa (Overbooking):**
   - *Situación previa:* El control manual de habitaciones en libretas o planillas de cálculo causaba asignaciones duplicadas ante reservas simultáneas por distintos canales.
   - *Solución entregada:* Arquitectura de doble candado concurrente: un candado preventivo de memoria rápida en Redis (15 minutos con liberación inmediata) y un candado definitivo en PostgreSQL mediante restricciones de exclusión temporal (`EXCLUDE USING gist`).
3. **Rigidez en la Gestión del Inventario de Habitaciones:**
   - *Situación previa:* El hotel no podía ajustar precios base, alterar cargos por huésped adicional o incorporar nuevas habitaciones sin requerir cambios en el código fuente o asistencia técnica.
   - *Solución entregada:* Módulo administrativo dinámico de habitaciones que permite crear, editar y consultar habitaciones en tiempo real, blindado contra eliminaciones accidentales si existen reservas activas asociadas.
4. **Fuga de Ingresos en Servicios de Restaurante y Cafetería:**
   - *Situación previa:* Los consumos en *Salgados Café* (desayunos, cafés especiales de origen, catas de barismo y repostería) se cobraban de forma aislada en caja menor, generando inconsistencias y fugas financieras.
   - *Solución entregada:* Módulo de Restaurante y pedidos con capacidad de facturar de contado o cargar consumos directamente al folio de la habitación (`charged_to_room`), consolidando una factura única al momento del check-out.
5. **Incertidumbre en Temporadas y Tarifas Estacionales:**
   - *Situación previa:* Falta de dinamismo tarifario para aprovechar picos de demanda turística en Sevilla (ej. Festival del Café, puentes festivos o fin de año) o para dinamizar la ocupación entre semana.
   - *Solución entregada:* Motor de Eventos Especiales que aplica reglas porcentuales automáticas de recargo o descuento sobre el valor liquidado tanto en la web como en el flujo conversacional.
6. **Barrera Económica de PMS Comerciales:**
   - *Situación previa:* Los sistemas comerciales tradicionales (Opera, Cloudbeds) imponen costos mensuales y comisiones por transacción incompatibles con la estructura financiera de un hotel boutique independiente.
   - *Solución entregada:* Sistema propietario contenerizado con costos de infraestructura previsibles y soberanía total sobre los datos del negocio.

### 1.3 Beneficiarios y Usuarios del Servicio

| Perfil de Usuario | Tipo de Acceso | Beneficios Tangibles Recibidos |
| :--- | :--- | :--- |
| **Huéspedes y Viajeros** | Externo (WhatsApp) | Autoservicio 24/7 sin descargar aplicaciones adicionales, cotizaciones transparentes, reserva garantizada, opciones de abono parcial (50%) o total (100%), y políticas claras de cancelación y reembolso. |
| **Personal de Recepción** | Interno (Panel Web) | Operación ágil del mostrador: consulta instantánea de códigos `TS-XXXX`, validación de llegadas (check-in) y salidas (check-out), registro de pedidos de restaurante y tienda, y panel sincronizado en tiempo real. |
| **Administración y Gerencia** | Interno (Panel Web Admin) | Control exhaustivo de inventario de habitaciones, configuración de eventos y precios dinámicos, supervisión de ingresos consolidados, auditoría cronológica inmutable y reportes operacionales. |

### 1.4 Funcionalidades Implementadas y Disponibles en el Entregable Final

- **Módulo de Autenticación y Perfil Institucional:** Control de acceso basado en credenciales cifradas con roles diferenciados (Administrador y Recepción). Panel de perfil de usuario con cambio seguro de contraseña (con validación de clave anterior) y carga de fotografía de perfil.
- **Gestión Dinámica de Habitaciones (CRUD Administrativo):** Creación de nuevas habitaciones, edición de números, tipo, capacidad máxima, precio base por noche, recargo por huésped adicional y política pet-friendly. Incluye candado lógico que rechaza la eliminación de habitaciones con compromisos de reserva vigentes.
- **Módulo de Salgados Café y Restaurante:** Catálogo de productos y servicios gastronómicos clasificados por categoría, emisión de pedidos, soporte de pago inmediato en caja o cargo a habitación (`charged_to_room`) y sincronización automática con la cuenta de la reserva.
- **Motor de Eventos y Tarifas Dinámicas:** Creación de eventos especiales con rango de fechas y porcentaje de ajuste (descuentos promocionales para estancias entre semana o recargos para ferias y temporadas altas).
- **Motor de Reservas Conversacional (WhatsApp):** Consulta interactiva de fechas y tipos de habitación, verificación atómica de disponibilidad, reserva guiada, comprobación de consentimiento y aviso de privacidad legal (Ley 1581 de 2012), y gestión de cancelaciones con reembolso proporcional sobre el dinero efectivamente pagado.
- **Recepción Operativa:** Registro ágil de check-in con asignación de llaves físicas, reloj sincronizado con la zona horaria del hotel, consulta de estados (confirmada, en estancia, finalizada, cancelada) y liquidación de saldos en check-out.
- **Finanzas y Auditoría Inmutable:** Registro secuencial de transacciones, desglose de ingresos por concepto de hospedaje, tienda y restaurante, y bitácora de auditoría inalterable para trazabilidad de operaciones.

### 1.5 Funcionalidades Excluidas de esta Entrega

- Integración directa con pasarelas bancarias con dispersión de fondos automática (en esta versión se opera mediante registro de transferencias verificadas y webhook seguro de simulación para pruebas operativas).
- Facturación electrónica directa ante la autoridad tributaria nacional (DIAN), programada para el siguiente ciclo evolutivo contable (versión 1.2.0).
- Motor de recomendación de actividades turísticas externas con compras de terceros.

### 1.6 Versión y Entorno de Entrega

- **Versión Entregada:** `1.0.0-FINAL`
- **Ambiente de Disponibilidad:** Servidor de Piloto Controlado (Staging / Producción en VPS Linux x86_64 con aislamiento total mediante Docker Compose, persistencia en volúmenes protegidos y canal cifrado TLS 1.3).

### 1.7 ¿Qué Recibirá Realmente el Cliente al Autorizar la Entrega?

El cliente Hotel Boutique Torre Satori recibe:
1. La plataforma de software completamente instalada, configurada y operativa en su infraestructura de servidor.
2. La base de datos relacional inicializada con las habitaciones, el menú del restaurante y los usuarios administrativos.
3. El webhook de WhatsApp Cloud API enlazado y respondiendo en el número corporativo del hotel.
4. El paquete documental integral compuesto por el Manual de Operación para Recepción, la Guía Técnica de Despliegue, las Políticas de Respaldo y la Bitácora de Pruebas.
5. El acta de transferencia segura de credenciales maestras y el plan de acompañamiento presencial para la fase de marcha blanca.

---

## Componente 2. Plan de Despliegue e Implementación

### 2.1 Arquitectura y Componentes a Desplegar

La solución adopta una arquitectura de monolito modular desacoplado, empaquetada íntegramente en contenedores Docker organizados a través de Docker Compose:

```
        +-------------------------------------------------------------+
        |                 CANALES DE ENTRADA CLIENTE                  |
        |                                                             |
        |    [ Huéspedes en WhatsApp ]         [ Personal Recepción ] |
        |                 |                               |           |
        |        (Meta Cloud API Webhook)           (Web Navegador)   |
        +-----------------|-------------------------------|-----------+
                          |                               |
                          v                               v
        +-------------------------------------------------------------+
        |             INFRAESTRUCTURA TORRE SATORI PMS                |
        |                                                             |
        |  +-----------------------+     +-------------------------+  |
        |  |  Orquestador n8n      |     |  Frontend Web React 18  |  |
        |  |  (Flujos & Gemini IA) |     |  (Vite + Tailwind CSS)  |  |
        |  +-----------------------+     +-------------------------+  |
        |                 \                           /               |
        |                  \                         /                |
        |                   v                       v                 |
        |          +-----------------------------------------+        |
        |          |     Backend API REST Spring Boot 3.3.5  |        |
        |          |     (Java 21 - Compilación Multi-Stage) |        |
        |          +-----------------------------------------+        |
        |                     /                    \                  |
        |                    v                      v                 |
        |       +-----------------------+  +-----------------------+  |
        |       |   Redis 7 Alpine      |  |  PostgreSQL 16 Alpine |  |
        |       | (Bloqueos TTL 15 min) |  | (Exclusión GIST DDL)  |  |
        |       +-----------------------+  +-----------------------+  |
        +-------------------------------------------------------------+
```

Componentes tecnológicos principales:
1. **Base de Datos Relacional (`postgres:16-alpine`):** Manejador transaccional con extensiones de rango (`btree_gist`) para exclusión temporal anti-sobreventa.
2. **Memoria Rápida y Candados (`redis:7-alpine`):** Repositorio en memoria de estados conversacionales y candados efímeros con expiración y liberación proactiva.
3. **Lógica de Negocio (`apps/api`):** Servicio Java 21 / Spring Boot 3.3.5 compilado mediante Dockerfile Multi-Stage con Maven empaquetado (sin dependencias de JDK en el sistema operativo anfitrión).
4. **Interfaz Operativa (`apps/web`):** Aplicación SPA en React 18, TypeScript y Tailwind CSS servida sobre contenedor ligero optimizado.
5. **Orquestación Conversacional (`n8n:1.81.4`):** Motor de integración de eventos WhatsApp, lógica de menús deterministas y escalamiento a IA.

### 2.2 Requisitos de Infraestructura Tecnológica

| Elemento | Requisito Mínimo | Configuración Recomendada |
| :--- | :--- | :--- |
| **Servidor Host** | VPS o Servidor Local x86_64 | Servidor Dedicado Cloud o VPS Linux (Ubuntu Server 22.04 LTS / EndeavourOS) |
| **Procesador (CPU)** | 2 Núcleos vCPU (2.0 GHz) | 4 Núcleos vCPU |
| **Memoria RAM** | 4 GB RAM física | 8 GB RAM física |
| **Almacenamiento** | 20 GB SSD | 40 GB NVMe SSD con volumen persistente para datos |
| **Conectividad de Red** | 20 Mbps simétricos | Enlace de fibra óptica con IP pública fija o túnel seguro Cloudflare |
| **Motor de Contenedores** | Docker Engine 24.0+ y Compose 2.20+ | Docker Engine última versión estable con reinicio automático (`restart: unless-stopped`) |

### 2.3 Base de Datos y Procedimientos de Instalación y Migración

La creación y evolución de la base de datos se realiza automáticamente mediante **Flyway** al inicializar el contenedor del backend, garantizando reproducibilidad absoluta:
- `V1__init_schema.sql`: Creación de entidades esenciales (habitaciones, huéspedes, reservas, productos de tienda y usuarios del sistema).
- `V3__fix_ids.sql`: Normalización de tipos de datos, identificadores secuenciales y restricciones de clave primaria.
- `V4__multi_room.sql`: Incorporación de identificadores de grupo para reservas multi-habitación y documento de identidad del huésped.
- `V5__paid_amount.sql`: Soporte para montos abonados (`paid_amount`) y estructura de reseñas de satisfacción.
- `V6__create_special_events_table.sql`: Creación de la tabla `special_events` para recargos y descuentos de temporada.
- `V7__create_restaurant_tables.sql`: Creación de las tablas `restaurant_menu_item`, `restaurant_order` y `restaurant_order_item`.
- `dev_seed.sql`: Carga del inventario inicial de habitaciones, productos de *Salgados Café*, eventos promocionales y usuarios preconfigurados.

### 2.4 Configuraciones Necesarias

Las configuraciones sensibles se inyectan estrictamente mediante variables de entorno en el archivo `.env` del servidor anfitrión, el cual se mantiene fuera de los repositorios de código:
- Credenciales de PostgreSQL (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`).
- Puerto y host de Redis (`REDIS_HOST`, `REDIS_PORT`).
- Tokens y secretos de WhatsApp Cloud API (`WHATSAPP_TOKEN`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_PHONE_ID`).
- Llave de acceso a Google Gemini API (`GEMINI_API_KEY`).
- Secretos criptográficos para generación de tokens de sesión JWT.

### 2.5 Secuencia de Actividades de Despliegue

```
  [1. Validar .env y Puertos] 
             |
             v
  [2. Backup Preventivo de Datos]
             |
             v
  [3. Construcción Multi-Stage de Imágenes]
             |
             v
  [4. Arranque de Contenedores de Persistencia (DB & Redis)]
             |
             v
  [5. Ejecución Automática de Migraciones Flyway (V1 - V7)]
             |
             v
  [6. Despliegue de Backend API y Frontend Web]
             |
             v
  [7. Inicialización de n8n y Activación de Webhook WhatsApp]
             |
             v
  [8. Ejecución de Pruebas de Humo (Smoke Tests)]
```

| Paso | Actividad Específica | Responsable Técnico | Criterio de Aceptación |
| :---: | :--- | :--- | :--- |
| **1** | Verificación de variables en `.env` y disponibilidad de puertos | Esteban Guarín V | Sin colisiones en puertos 80, 443, 5432, 6379 y 5678. |
| **2** | Generación de copia de seguridad previa de bases de datos | Juan Felipe Garzón | Archivo de respaldo `backup_pre_deploy.sql` generado y validado. |
| **3** | Compilación de imágenes Multi-Stage de backend y frontend | Juan Felipe Garzón | Imágenes generadas sin errores de compilación ni advertencias críticas. |
| **4** | Despliegue de PostgreSQL y Redis con healthcheck activo | Juan Felipe Garzón | Servicios en estado *healthy* en Docker. |
| **5** | Validación de ejecución de scripts Flyway V1 a V7 | Esteban Guarín V | Esquema de base de datos verificado con 0 fallas. |
| **6** | Despliegue de servicios de aplicación (API y Web) | Juan Felipe Garzón | Endpoints respondiendo código 200 en `/actuator/health`. |
| **7** | Enlace del webhook de WhatsApp en n8n | Juan José Arias | Handshake verificado con Meta Cloud API. |
| **8** | Ejecución de suite de pruebas de humo operacionales | Equipo Completo | 100% de escenarios operativos básicos aprobados. |

### 2.6 Plan de Reversión (Rollback)

- **Criterio de Activación:** Detección de incompatibilidad crítica en la base de datos, falla irrecuperable en el inicio del backend o indisponibilidad del servicio superior a 15 minutos durante la ventana de despliegue.
- **Procedimiento de Reversión:**
  1. Detención inmediata de los servicios activos mediante el comando `./scripts/start-dev.sh -d` o `docker compose down`.
  2. Restauración de la base de datos a partir del volcado de seguridad `backup_pre_deploy.sql`.
  3. Reetiquetado y relanzamiento de las imágenes del release anterior catalogadas como estables.
  4. Reactivación y verificación de enlaces webhooks.
- **Tiempo Objetivo de Recuperación (RTO):** Menor a 8 minutos.
- **Punto Objetivo de Recuperación (RPO):** Menor a 5 minutos (datos de reservas sincronizados).

---

## Componente 3. Gestión y Autorización de Cambios

### 3.1 Registro de Cambios Significativos Implementados en la Versión Final

| Código | Descripción del Cambio | Justificación de Negocio | Impacto en Funcionalidad y Datos | Mitigación y Control de Riesgo |
| :---: | :--- | :--- | :--- | :--- |
| **CHG-01** | **Cálculo de Reembolso sobre Dinero Abonado** | Aplicar retenciones de cancelación estrictamente sobre el dinero real pagado por el huésped y no sobre el total contractual. | Modificación en la lógica de cálculo en el servicio de reservas y ajuste de columnas de auditoría financiera. | Rigor legal y protección de flujo de caja frente a cancelaciones imprevistas. |
| **CHG-02** | **Liberación Inmediata de Candados de Memoria** | Liberar el bloqueo de la habitación en Redis al momento en que el usuario escribe "menu" o cancela en WhatsApp. | Mayor rotación del inventario; elimina la espera forzada de 15 minutos cuando el cliente desiste. | Operación atómica en Redis sin riesgo de carreras concurrentes. |
| **CHG-03** | **Edición Dinámica y Adición de Habitaciones** | Permitir a la administración modificar tarifas, capacidades y registrar nuevas habitaciones sin intervención técnica. | Nuevos endpoints administrativos (`RoomController`) y migración para actualización de atributos de catálogo. | Restricción de integridad: no es posible eliminar habitaciones que cuenten con reservas vigentes. |
| **CHG-04** | **Módulo de Salgados Café y Restaurante** | Integrar los consumos gastronómicos y catas de café a la cuenta unificada de la habitación o pago de mostrador. | Tablas `restaurant_menu_item`, `restaurant_order` y liquidación acumulada en el check-out de la habitación. | Validación de folio activo antes de permitir la imputación de cargos a habitación. |
| **CHG-05** | **Motor de Eventos y Tarifas Dinámicas** | Habilitar promociones y recargos automáticos por temporadas festivas o días de baja demanda. | Tabla `special_events` y recalculo dinámico del total cotizado en web y WhatsApp. | Reglas de precedencia de fechas que evitan solapamiento incoherente de promociones. |
| **CHG-06** | **Autenticación Institucional y Perfil de Usuario** | Proteger el panel web con login formal, cambio seguro de contraseña y administración de foto de perfil. | Protección de rutas en frontend y endpoints de API con tokens de sesión y hashing criptográfico. | Validación estricta que exige la clave anterior para cualquier cambio de credenciales. |

### 3.2 Comité y Autorización Formal de la Versión Final

- **Evaluación Técnica de Arquitectura:** Aprobada por Juan Felipe Garzón (*Development Team*) y Esteban Guarín Valencia (*Scrum Master*).
- **Aprobación de Negocio y Criterios de Aceptación:** Autorizada por Juan José Arias Gallego (*Product Owner*).
- **Dictamen del Comité de Cambios:** Aprobado por unanimidad. Los cambios incorporan las funciones solicitadas por la gerencia, respetan la integridad referencial y eliminan fricciones operativas.

---

## Componente 4. Validación y Pruebas del Servicio

### 4.1 Matriz Consolidada de Pruebas de Utilidad y Garantía

| Tipo de Prueba | Escenario Evaluado | Resultado Esperado | Resultado Obtenido | Evidencia Registrada | Estado | Responsable |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **Funcional** | Reserva completa vía WhatsApp con abono del 50%. | Creación de reserva con código `TS-XXXX`, abono registrado y reflejo en web. | Código `TS-XXXX` emitido en 1.2s; reserva visible en recepción. | Registro en base de datos y log de n8n. | **Aprobado** | Juan Felipe Garzón |
| **Funcional** | Creación y modificación dinámica de habitaciones por Administrador. | Habitación creada y modificable; impedimento de eliminar si tiene reservas activas. | Datos actualizados en catálogo; bloqueo referencial efectivo ante reservas activas. | Respuesta HTTP 200 en edición; HTTP 409 al intentar borrar habitación ocupada. | **Aprobado** | Juan Felipe Garzón |
| **Funcional** | pedido de Salgados Café con cargo directo a habitación. | Ítems agregados al saldo de la habitación y consolidados para liquidación final. | Cargo reflejado en detalle de folio de habitación; balance actualizado al instante. | Orden de restaurante vinculada a ID de reserva en base de datos. | **Aprobado** | Juan José Arias |
| **Funcional** | Cotización con tarifa dinámica por evento especial de temporada. | Aplicación de descuento del 10% o recargo del 15% según rango de fechas. | Descuento aplicado matemáticamente en cotización web y conversacional. | Facturación detallada con desglose de evento aplicado. | **Aprobado** | Juan José Arias |
| **Integración** | Sincronización bidireccional Panel Web y Chatbot WhatsApp. | La cancelación o check-in en web actualiza el estado visible en WhatsApp y viceversa. | Sincronización en tiempo real inferior a 3 segundos entre ambos canales. | Actualización reactiva en panel web sin recargar la página. | **Aprobado** | Esteban Guarín V |
| **Seguridad** | Intento de sobreventa concurrente en la misma habitación y fechas. | El primer cliente adquiere el bloqueo; el segundo recibe rechazo atómico y alternativas. | Bloqueo en Redis previene colisión; restricción PostgreSQL GIST protege datos. | Log de excepción `409 Conflict` controlado y mensaje amigable en chat. | **Aprobado** | Juan Felipe Garzón |
| **Seguridad** | Autenticación y cambio de clave en el perfil de usuario. | Acceso permitido solo a credenciales válidas; cambio de clave exige ingresar la anterior. | Clave actualizada tras verificación exitosa; clave errónea rechazada. | Hashing BCrypt verificado y sesión renovada. | **Aprobado** | Esteban Guarín V |
| **Rendimiento** | Prueba de carga con 50 peticiones simultáneas de cotización. | Tiempos de respuesta inferiores a 2.0 segundos sin degradación del servicio. | Tiempo promedio de 850 ms en API y 1.4s en flujo de WhatsApp. | Métricas registradas en benchmark de pruebas de carga. | **Aprobado** | Esteban Guarín V |
| **Recuperación** | Simulación de caída abrupta del contenedor de base de datos. | Restablecimiento de servicios y datos intactos a partir del volumen persistente. | Recuperación completa en 2 minutos y 15 segundos sin pérdida de registros. | Logs de arranque y verificación de integridad de tablas. | **Aprobado** | Juan Felipe Garzón |
| **Aceptación (UAT)** | Simulación de turno completo de recepción (check-in, pedidos y check-out). | El personal de recepción opera la plataforma de forma autónoma y sin errores. | Flujo operacional completado satisfactoriamente por el personal del hotel. | Acta de pruebas de aceptación firmada por el operador. | **Aprobado** | Juan José Arias |

---

## Componente 5. Preparación de la Operación y Soporte

### 5.1 Estructura Operativa y Niveles de Soporte Técnico

```
   [ Huésped en WhatsApp ]             [ Huésped en Mostrador ]
              \                                   /
               \                                 /
                v                               v
         +---------------------------------------------+
         |               SOPORTE NIVEL 1               |
         |         Equipo de Recepción del Hotel       |
         |  - Atención a clientes y resolución de dudas|
         |  - Check-in, check-out y llaves físicas     |
         |  - Registro de consumos de café/restaurante |
         |  - Escalamiento de incidentes técnicos      |
         +---------------------------------------------+
                                |
             (Falla Técnica / Caída de Servicio)
                                v
         +---------------------------------------------+
         |               SOPORTE NIVEL 2               |
         |         Equipo de Ingeniería Satori PMS     |
         |  - Monitoreo de contenedores e infraestructura
         |  - Mantenimiento de PostgreSQL y Redis      |
         |  - Soporte de webhooks y tokens de Meta/API |
         |  - Despliegue de parches y optimizaciones   |
         +---------------------------------------------+
```

### 5.2 Acuerdos de Nivel de Servicio (SLA)

| Nivel de Severidad | Criterio de Clasificación | Ejemplo Operativo | Tiempo Máximo de Respuesta | Tiempo Máximo de Solución |
| :---: | :--- | :--- | :---: | :---: |
| **P1 — Crítico** | Indisponibilidad total del servicio o bloqueo de reservas. | Caída del motor de base de datos o fallo masivo de la API. | < 15 minutos | < 2 horas |
| **P2 — Alto** | Degradación funcional mayor con alternativa manual disponible. | Interrupción en el canal de WhatsApp; recepción opera vía web. | < 45 minutos | < 6 horas |
| **P3 — Medio** | Incidencia funcional moderada sin impacto en reservas. | Desfase en reporte gráfico de auditoría o lentitud puntual. | < 3 horas | < 24 horas |
| **P4 — Bajo** | Consultas operativas o solicitudes de ajuste cosmético. | Modificación de textos descriptivos en productos de café. | < 6 horas | < 48 horas |

### 5.3 Indicadores de Monitoreo y Calidad del Servicio (KPIs)

- **Disponibilidad Global del Servicio (*Uptime*):** Meta >= 99.5% mensual.
- **Tasa de Sobreventas (*Overbooking Rate*):** Meta 0.0% estricto garantizado por arquitectura.
- **Tiempo Promedio de Respuesta en WhatsApp:** Meta < 2.5 segundos por interacción.
- **Tasa de Conversión de Cotizaciones:** Medición de reservas formalizadas sobre el total de consultas.

### 5.4 Procedimientos de Respaldo y Continuidad del Negocio

- **Respaldos Automáticos Diarios:** Ejecución programada vía cronjob a las 02:00 AM de volcado completo de PostgreSQL comprimido y cifrado.
- **Retención:** 30 copias de seguridad diarias, 12 mensuales y almacenamiento secundario en volumen independiente.
- **Prueba Periódica de Restauración:** Validación mensual de restauración en ambiente de pruebas para comprobar la consistencia de los datos.

### 5.5 Dependencias Externas y Gestión de Proveedores

- **Meta Cloud API (WhatsApp Business Platform):** Requiere vigencia del token de acceso y saldo de conversaciones corporativas. En caso de corte masivo de Meta, la operación conmuta al teléfono de soporte y atención directa en el panel web.
- **Google Cloud Platform (Gemini AI API):** Motor de lenguaje natural para intenciones conversacionales complejas. En caso de indisponibilidad de la IA, el orquestador n8n activa automáticamente el menú guiado por opciones numéricas deterministas.

---

## Componente 6. Gestión del Conocimiento y Transferencia

### 6.1 Documentación Técnica y Operativa Entregada

1. **Manual de Operación para Recepción:** Documento y guía visual con flujos para búsqueda de códigos de reserva `TS-XXXX`, check-in, check-out, registro de consumos y pedidos de Salgados Café con cargo al folio, y resolución de incidencias comunes.
2. **Guía Técnica de Despliegue y Administración:** Manual con especificaciones de contenedores, variables de entorno, scripts de control (`./start-dev.sh` y `./scripts/start-dev.sh`), procedimientos de respaldo y actualización.
3. **Catálogo de Arquitectura y Especificación de Endpoints:** Documentación detallada de entidades relacionales, restricciones temporales GIST (0% sobreventas), contratos de API REST y flujos de automatización en n8n.
4. **Guía de Solución Rápida de Problemas (*Troubleshooting Guide*):** Árbol de diagnóstico para reinicio de servicios, verificación de salud de Redis y reautorización de webhooks.
5. **Presentación Ejecutiva Oficial de Transición del Servicio (36 Láminas):** Plataforma interactiva en línea disponible en [Canva — Presentación Ejecutiva Torre Satori PMS (ITIL 4)](https://canva.link/xjx14rgw1d1zdmq), sustentando formalmente los 8 componentes de entrega y puesta en marcha para clientes, directivos y equipo técnico.

### 6.2 Entrega Segura de Credenciales y Accesos

En estricto cumplimiento de las políticas de seguridad y la norma ITIL 4:
- Se prohíbe de manera tajante incluir contraseñas en texto claro dentro de la documentación.
- Las credenciales iniciales de acceso para el usuario Administrador (`admin@gmail.com`) y el personal de Recepción (`recepcion@satoripms.com`) se entregaron en sobre cerrado al representante legal del hotel y a través de un canal criptográfico seguro efímero.
- Se configuró la política obligatoria de cambio de contraseña en el primer inicio de sesión mediante el panel de perfil de usuario.

### 6.3 Plan de Capacitación y Transferencia

- **Taller Presencial para Recepción (4 horas):** Simulación de flujos de alta demanda, check-in rápido, registro de pedidos de cafetería, atención de incidentes y uso del panel web.
- **Sesión Directiva para Gerencia (2 horas):** Parametrización de habitaciones, fijación de precios, creación de eventos promocionales de temporada, lectura de métricas financieras y auditoría.
- **Evaluación Práctica:** Todo el personal operativo completó una evaluación práctica demostrando autonomía en la operación diaria sin requerir asistencia del equipo de desarrollo.

---

## Componente 7. Comunicación y Puesta en Servicio

### 7.1 Plan de Comunicación a Partes Interesadas

| Audiencia Interesada | Canal de Comunicación | Mensaje Clave | Cronograma de Entrega |
| :--- | :--- | :--- | :--- |
| **Personal Operativo del Hotel** | Reunión presencial y circular informativa | Presentación del nuevo sistema, asignación de turnos, canales de soporte y procedimientos de contingencia. | 5 días antes del inicio del piloto |
| **Huéspedes con Reservas Previas** | Notificación oficial vía WhatsApp | Mensaje de cortesía con su código de reserva `TS-XXXX` y confirmación de servicios garantizados. | 48 horas antes de la transición |
| **Público General y Clientes Potenciales** | Redes sociales y señalética en el hotel | Anuncio del canal de reservas 24/7 en WhatsApp y código QR para cotización inmediata. | Día de apertura oficial del piloto |

### 7.2 Condiciones y Reglas de la Fase de Marcha Blanca (Piloto Controlado)

- **Duración del Piloto Controlado:** Quince (15) días calendario a partir de la fecha de autorización formal.
- **Alcance Operativo:** Operación integral sobre la totalidad de habitaciones del hotel, servicios de Salgados Café y motor conversacional de reservas.
- **Acompañamiento Técnico Activo:** Presencia y monitoreo continuo del equipo de desarrollo durante las primeras 72 horas para calibración de respuestas y verificación de transacciones.
- **Canal de Reporte Inmediato de Incidentes:** Línea directa de mensajería y enlace dedicado con el equipo de soporte técnico para atención de novedades operativas.

---

## Componente 8. Aceptación y Cierre de la Transición

### 8.1 Evaluación de Criterios de Aceptación Final

- [x] **Arquitectura Anti-Sobreventa:** Cero casos de doble reserva verificados bajo pruebas de estrés concurrente con doble candado (Redis y PostgreSQL GIST).
- [x] **Panel Web Funcional y Seguro:** Login institucional, gestión dinámica de habitaciones (CRUD de Administrador), módulo de Salgados Café con pedidos y motor de eventos estacionales.
- [x] **Sincronización Transaccional:** Integración perfecta entre el panel web de recepción y el flujo de WhatsApp con códigos únicos `TS-XXXX`.
- [x] **Personal Operativo Capacitado:** 100% del personal de recepción y administración capacitado y evaluado satisfactoriamente.
- [x] **Respaldo y Seguridad de la Información:** Rutinas automatizadas de copia de seguridad activas y probadas.
- [x] **Documentación Entregada:** Manuales de usuario, arquitectura y guías técnicas debidamente transferidas.

### 8.2 Defectos Conocidos y Riesgos Residuales Aceptados

- **Dependencia de la Disponibilidad Global de Meta:** Ante interrupciones mundiales de la infraestructura de WhatsApp, la recepción opera de forma autónoma mediante llamadas telefónicas y registro directo en el panel web.
- **Curva de Adaptación del Huésped:** Algunos usuarios mayores prefieren asistencia telefónica directa; el sistema contempla el botón de derivación a recepcionista humano en WhatsApp.

### 8.3 Dictamen Formal de Puesta en Servicio

Habiéndose demostrado de forma rigurosa la utilidad funcional de la solución tecnológica y satisfecho cabalmente todas las condiciones de garantía, rendimiento, seguridad y continuidad bajo las buenas prácticas del marco ITIL 4:

**DICTAMEN FINAL:** **AUTORIZADO PARA PUESTA EN SERVICIO EN MODALIDAD DE PILOTO CONTROLADO (MARCHA BLANCA).**

Firmado y aprobado por el Equipo de Dirección del Proyecto:
- **Esteban Guarín Valencia** — *Scrum Master*
- **Juan José Arias Gallego** — *Product Owner*
- **Juan Felipe Garzón** — *Development Team*