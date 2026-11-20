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
  - **Juan Felipe Garzón** — *Development Team* (Arquitectura de Software, Candado Atómico Concurrente, Módulos de Operación y Pruebas Técnicas)

---

## Componente 1. Definición del Servicio y Alcance de la Entrega

### 1.1 Nombre y Propósito del Servicio

- **Nombre Oficial del Servicio:** Plataforma Integral de Gestión Hotelera, Automatización Conversacional y Experiencia Torre Satori PMS.
- **Propósito Estratégico:** Proporcionar una solución tecnológica unificada de alto rendimiento que digitalice y automatice de extremo a extremo las operaciones de Torre Satori Hotel Boutique (9 habitaciones). El servicio articula la atención ininterrumpida 24/7 y la reserva multicanal vía WhatsApp sin riesgo de sobreventa mediante candados relacionales atómicos, junto a un panel web moderno con autenticación segura en dos niveles (Administrador y Recepción), administración dinámica del inventario de habitaciones, integración completa de la cafetería y restaurante (*Salgados Café*) con pedidos cargados a la cuenta del huésped, y un motor de eventos y temporadas con tarifas dinámicas.

### 1.2 Necesidad de Negocio y Problemas Resueltos

1. **Atención Descentralizada y Pérdida de Clientes Nocturnos:**
   - *Situación previa:* La atención al cliente y la cotización dependían de teléfonos personales de recepción o atención física en mostrador, perdiendo ventas de viajeros que consultaban de noche o durante fines de semana.
   - *Solución entregada:* Motor conversacional automatizado 24/7 sobre WhatsApp Cloud API orquestado con n8n y asistido por inteligencia artificial en lenguaje natural, capaz de consultar disponibilidad en tiempo real, cotizar con exactitud y formalizar reservas al instante.
2. **Riesgo Crítico de Sobreventa (Overbooking):**
   - *Situación previa:* El control manual de habitaciones en libretas o planillas de cálculo causaba asignaciones duplicadas ante reservas simultáneas por distintos canales.
   - *Solución entregada:* Arquitectura de candado relacional atómico en PostgreSQL 16 con extensión `btree_gist`: restricción matemática de exclusión temporal (`EXCLUDE USING gist`) combinada con expiración automática de 15 minutos (`expires_at`) e *inline filtering* en tiempo real, erradicando por completo la necesidad de cachés volátiles externas y garantizando consistencia ACID estricta.
3. **Rigidez en la Gestión del Inventario de Habitaciones:**
   - *Situación previa:* El hotel no podía ajustar precios base, alterar cargos por huésped adicional o incorporar nuevas habitaciones sin requerir cambios en el código fuente o asistencia técnica.
   - *Solución entregada:* Módulo administrativo dinámico de habitaciones que permite crear, editar y consultar habitaciones en tiempo real, blindado contra eliminaciones accidentales si existen reservas activas asociadas.
4. **Fuga de Ingresos en Servicios de Restaurante y Cafetería:**
   - *Situación previa:* Los consumos en *Salgados Café* (desayunos, cafés especiales de origen, catas de barismo y repostería) se cobraban de forma aislada en caja menor, generando inconsistencias y fugas financieras.
   - *Solución entregada:* Módulo de Restaurante y pedidos con capacidad de facturar de contado o cargar consumos directamente al folio de la habitación (`charged_to_room`), consolidando una factura única al momento del check-out.
5. **Incertidumbre en Temporadas y Tarifas Estacionales:**
   - *Situación previa:* Falta de dinamismo tarifario para aprovechar picos de demanda turística en Sevilla (ej. Festival Bandola, puentes festivos o fin de año) o para dinamizar la ocupación entre semana.
   - *Solución entregada:* Motor de Eventos Especiales que aplica reglas porcentuales automáticas de recargo o descuento sobre el valor liquidado tanto en la web como en el flujo conversacional.
6. **Barrera Económica de PMS Comerciales:**
   - *Situación previa:* Los sistemas comerciales tradicionales (Opera, Cloudbeds) imponen costos mensuales y comisiones por transacción incompatibles con la estructura financiera de un hotel boutique independiente.
   - *Solución entregada:* Sistema propietario contenerizado sobre stack moderno de código abierto (Python 3.12, FastAPI, PostgreSQL 16, React 18) con costos de infraestructura mínimos y soberanía total sobre los datos del negocio.

### 1.3 Beneficiarios y Usuarios del Servicio

| Perfil de Usuario | Tipo de Acceso | Beneficios Tangibles Recibidos |
| :--- | :--- | :--- |
| **Huéspedes y Viajeros** | Externo (WhatsApp) | Autoservicio 24/7 sin descargar aplicaciones adicionales, cotizaciones transparentes, reserva garantizada, opciones de abono parcial (50%) o total (100%), y políticas claras de cancelación y reembolso. |
| **Personal de Recepción** | Interno (Panel Web) | Operación ágil del mostrador: consulta instantánea de códigos `SAT-XXXX`, validación de llegadas (check-in) y salidas (check-out), registro de pedidos de restaurante y tienda, y panel sincronizado en tiempo real. |
| **Administración y Gerencia** | Interno (Panel Web Admin) | Control exhaustivo de inventario de habitaciones, configuración de eventos y precios dinámicos, supervisión de ingresos consolidados, auditoría cronológica inmutable y reportes operacionales. |

### 1.4 Funcionalidades Implementadas y Disponibles en el Entregable Final

- **Módulo de Autenticación y Control de Acceso (RBAC):** Control de acceso basado en tokens seguros JWT (JSON Web Tokens) con roles diferenciados (`Administrador` y `Recepcionista`). Cifrado robusto de contraseñas mediante algoritmos seguros (Argon2 / bcrypt) y auditoría inmutable de accesos.
- **Gestión Dinámica de Habitaciones (CRUD Administrativo):** Creación de nuevas habitaciones, edición de números, tipo, capacidad máxima, precio base por noche, recargo por huésped adicional (RN-01) y política pet-friendly. Incluye candado lógico que rechaza la eliminación de habitaciones con compromisos de reserva vigentes.
- **Módulo de Salgados Café y Restaurante:** Catálogo de productos y servicios gastronómicos clasificados por categoría, emisión de pedidos, soporte de pago inmediato en caja o cargo a habitación (`charged_to_room`) y sincronización automática con la cuenta de la reserva.
- **Motor de Eventos y Tarifas Dinámicas:** Creación de eventos especiales con rango de fechas y porcentaje de ajuste (descuentos promocionales para estancias entre semana o recargos para ferias y temporadas altas).
- **Motor de Reservas Conversacional (WhatsApp):** Consulta interactiva de fechas y tipos de habitación, verificación atómica de disponibilidad sin solapamiento (RN-02), reserva guiada, comprobación de consentimiento y aviso de privacidad legal (Ley 1581 de 2012), y gestión de cancelaciones con reembolso proporcional sobre el dinero efectivamente pagado (RN-03).
- **Recepción Operativa:** Registro ágil de check-in con asignación de llaves físicas, reloj sincronizado con la zona horaria del hotel (`America/Bogota`), consulta de estados canónicos (`BLOQUEADA_TEMPORAL`, `CONFIRMADA`, `EN_CURSO`, `EXPIRADA`, `CANCELADA`) y liquidación de saldos en check-out.
- **Finanzas y Auditoría Inmutable:** Registro secuencial de transacciones, desglose de ingresos por concepto de hospedaje, tienda y restaurante, y bitácora de auditoría inalterable (`audit_log`) para trazabilidad legal de operaciones críticas.

### 1.5 Funcionalidades Excluidas de esta Entrega

- Integración directa con dispersión bancaria automática (en esta versión se opera mediante webhook con validación criptográfica HMAC `X-Hub-Signature-256` en entorno sandbox y confirmación manual autorizada en recepción).
- Facturación electrónica directa ante la DIAN, programada para el siguiente ciclo evolutivo contable (versión 1.2.0).
- Liberación automática de reservas por No-Show a las 12:00 m (descartada formalmente para evitar perjuicios a huéspedes demorados en carretera).

### 1.6 Versión y Entorno de Entrega

- **Versión Entregada:** `1.0.0-FINAL`
- **Ambiente de Disponibilidad:** Servidor de Piloto Controlado (Ambiente contenerizado Docker Compose con backend FastAPI Python 3.12, base de datos PostgreSQL 16 con extensión `btree_gist`, frontend React 18 servido con Vite, y orquestador n8n expuesto mediante canal seguro HTTPS / TLS 1.3).

### 1.7 ¿Qué Recibirá Realmente el Cliente al Autorizar la Entrega?

El cliente Hotel Boutique Torre Satori recibe:
1. La plataforma de software completamente instalada, configurada y operativa en su infraestructura de servidor.
2. La base de datos relacional PostgreSQL 16 inicializada con las 9 habitaciones, el menú del restaurante y los usuarios administrativos.
3. El webhook de WhatsApp Cloud API enlazado en n8n y respondiendo en el número corporativo de pruebas del hotel.
4. El paquete documental integral compuesto por el Manual de Operación para Recepción, la Guía Técnica de Despliegue, las Políticas de Respaldo y la Bitácora de Pruebas.
5. El acta de transferencia segura de credenciales maestras y el plan de acompañamiento para la fase de marcha blanca.

---

## Componente 2. Plan de Despliegue e Implementación

### 2.1 Arquitectura y Componentes a Desplegar

La solución adopta una arquitectura monolítica modular hexagonal de alto rendimiento, empaquetada íntegramente en contenedores Docker coordinados a través de Docker Compose:

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
        |  |  (Flujos & Gemini IA) |     |  (Vite + TypeScript)    |  |
        |  +-----------------------+     +-------------------------+  |
        |                 \                           /               |
        |                  \                         /                |
        |                   v                       v                 |
        |          +-----------------------------------------+        |
        |          |     Backend API REST FastAPI (Python)   |        |
        |          |     (Uvicorn ASGI Server - Puerto 8080) |        |
        |          +-----------------------------------------+        |
        |                                 |                           |
        |                                 v                           |
        |                    +-------------------------+              |
        |                    |  PostgreSQL 16 Alpine   |              |
        |                    |  (Extensión btree_gist) |              |
        |                    |  (EXCLUDE Constraint)   |              |
        |                    +-------------------------+              |
        +-------------------------------------------------------------+
```

Componentes tecnológicos principales:
1. **Base de Datos Relacional (`postgres:16-alpine`):** Motor relacional ACID con extensión `btree_gist` habilitada para la restricción de exclusión temporal anti-sobreventa (`EXCLUDE USING gist`) sobre `room_id + daterange`.
2. **Lógica de Negocio Central (`apps/api`):** Servicio monolítico modular en Python 3.12 y FastAPI sobre servidor ASGI Uvicorn, con validación de esquemas mediante Pydantic y acceso asíncrono a datos mediante SQLAlchemy 2.0.
3. **Interfaz Operativa Web (`apps/web`):** Aplicación SPA en React 18 con Vite, TypeScript y Tailwind CSS, consumiendo la API de FastAPI mediante clientes REST tipados y TanStack Query.
4. **Orquestación Conversacional (`n8n`):** Gateway de eventos de WhatsApp Cloud API, normalización de mensajes entrantes y enrutamiento hacia los endpoints de FastAPI con autenticación de servicio.

### 2.2 Requisitos de Infraestructura Tecnológica

| Elemento | Requisito Mínimo | Configuración Recomendada |
| :--- | :--- | :--- |
| **Servidor Host** | VPS o Servidor Local x86_64 / ARM64 | Servidor Dedicado Cloud o VPS Linux (Ubuntu Server 22.04 LTS) |
| **Procesador (CPU)** | 2 Núcleos vCPU (2.0 GHz) | 4 Núcleos vCPU |
| **Memoria RAM** | 4 GB RAM física | 8 GB RAM física |
| **Almacenamiento** | 20 GB SSD | 40 GB NVMe SSD con volumen persistente para base de datos |
| **Conectividad de Red** | 20 Mbps simétricos | Enlace con IP pública o túnel seguro HTTPS con certificado TLS 1.3 |
| **Motor de Contenedores** | Docker Engine 24.0+ y Compose 2.20+ | Docker Engine estable con reinicio automático (`restart: unless-stopped`) |

### 2.3 Base de Datos y Procedimientos de Instalación y Migración

La creación, evolución y versionamiento inmutable del esquema de base de datos se realiza automáticamente mediante **Alembic**, garantizando reproducibilidad y control de versiones transparente:
- `alembic upgrade head`: Aplica todas las migraciones pendientes al arrancar el contenedor o servicio.
- `001_initial_schema.py`: Creación de la extensión `btree_gist`, tablas principales (`room`, `guest`, `booking`, `audit_log`, `special_events`, `restaurant_order`, `system_users`), índices GiST y restricción matemática contra colisión de reservas.
- Restricción DDL anti-sobreventa:
  ```sql
  CONSTRAINT no_overlapping_active_bookings 
  EXCLUDE USING gist (
      room_id WITH =, 
      daterange(check_in, check_out, '[)') WITH &&
  ) 
  WHERE (status IN ('BLOQUEADA_TEMPORAL', 'CONFIRMADA', 'EN_CURSO'));
  ```
- `dev_seed.sql`: Carga del inventario oficial de las 9 habitaciones del hotel con capacidades, tarifas, usuarios del sistema y productos iniciales de Salgados Café.

### 2.4 Configuraciones Necesarias

Las configuraciones sensibles se inyectan estrictamente mediante variables de entorno en el archivo `.env` del servidor anfitrión, el cual se mantiene fuera de los repositorios de código:
- Credenciales de PostgreSQL (`DATABASE_URL`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`).
- Claves criptográficas de autenticación JWT (`JWT_SECRET`, `JWT_EXPIRES_IN=8h`).
- Secretos de pasarela de pago para verificación de firma HMAC (`PAYMENT_WEBHOOK_SECRET`).
- Tokens y secretos de WhatsApp Cloud API (`WHATSAPP_TOKEN`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_PHONE_ID`).
- Llave de acceso a Google Gemini API (`GEMINI_API_KEY`).
- URLs públicas de integración (`VITE_API_URL`, `N8N_PUBLIC_URL`).

### 2.5 Secuencia de Actividades de Despliegue

```
  [1. Validar .env y Puertos del Sistema] 
                     |
                     v
  [2. Backup Preventivo de Base de Datos]
                     |
                     v
  [3. Arranque de Motor PostgreSQL 16 con Extensión btree_gist]
                     |
                     v
  [4. Ejecución Automática de Migraciones Alembic (upgrade head)]
                     |
                     v
  [5. Despliegue de Backend FastAPI y Frontend Web React]
                     |
                     v
  [6. Inicialización de n8n y Enlace de Webhook WhatsApp]
                     |
                     v
  [7. Ejecución de Pruebas de Humo (Healthcheck /api/v1/health)]
```

| Paso | Actividad Específica | Responsable Técnico | Criterio de Aceptación |
| :---: | :--- | :--- | :--- |
| **1** | Verificación de variables en `.env` y disponibilidad de puertos | Esteban Guarín V | Sin colisiones en puertos 80, 443, 5432, 8080 y 5678. |
| **2** | Generación de copia de seguridad previa de bases de datos | Juan Felipe Garzón | Archivo de respaldo `backup_pre_deploy.sql` generado y validado. |
| **3** | Arranque del contenedor PostgreSQL 16 | Juan Felipe Garzón | Servicio en estado *healthy* respondiendo en puerto 5432. |
| **4** | Ejecución de migraciones Alembic | Esteban Guarín V | Tablas y restricción `EXCLUDE USING gist` creadas con 0 fallas. |
| **5** | Despliegue de FastAPI y Frontend Web | Juan Felipe Garzón | Endpoint `/api/v1/health` retornando HTTP 200 y UI accesible. |
| **6** | Enlace del webhook de WhatsApp en n8n | Juan José Arias | Handshake verificado con Meta Cloud API (`hub.challenge`). |
| **7** | Ejecución de suite de pruebas de humo operacionales | Equipo Completo | 100% de escenarios operativos básicos aprobados. |

### 2.6 Plan de Reversión (Rollback)

- **Criterio de Activación:** Detección de incompatibilidad crítica en la base de datos, falla irrecuperable en el inicio del backend o indisponibilidad del servicio superior a 15 minutos durante la ventana de despliegue.
- **Procedimiento de Reversión:**
  1. Detención inmediata de los servicios activos mediante `docker compose down`.
  2. Ejecución de reversión de esquema con `alembic downgrade -1` o restauración del volcado `backup_pre_deploy.sql`.
  3. Relanzamiento de las imágenes estables del release anterior.
  4. Reactivación y verificación de enlaces webhooks y comprobación de `/api/v1/health`.
- **Tiempo Objetivo de Recuperación (RTO):** Menor a 5 minutos.
- **Punto Objetivo de Recuperación (RPO):** Menor a 3 minutos (cero pérdida de reservas confirmadas).

---

## Componente 3. Gestión y Autorización de Cambios

### 3.1 Registro de Cambios Significativos Implementados en la Versión Final

| Código | Descripción del Cambio | Justificación de Negocio | Impacto en Funcionalidad y Datos | Mitigación y Control de Riesgo |
| :---: | :--- | :--- | :--- | :--- |
| **CHG-01** | **Cálculo de Reembolso sobre Dinero Abonado** | Aplicar retenciones de cancelación estrictamente sobre el dinero real pagado por el huésped (RN-03) y no sobre el total contractual. | Modificación en la lógica de cálculo en el servicio de reservas y ajuste de columnas de auditoría financiera. | Rigor legal y protección de flujo de caja frente a cancelaciones imprevistas. |
| **CHG-02** | **Candado Relacional Atómico con Expiración Inline** | Migrar los bloqueos temporales de 15 min a la tabla `booking` de PostgreSQL con `expires_at`, filtrando expirados en tiempo real (`inline filtering`) y eliminando Redis. | Elimina la dependencia de Redis y el riesgo de inconsistencia *split-brain*; la disponibilidad ignora candados vencidos sin depender de jobs externos. | Restricción nativa `EXCLUDE USING gist` que serializa atómicamente la reserva en el motor de base de datos. |
| **CHG-03** | **Edición Dinámica y Adición de Habitaciones** | Permitir a la administración modificar tarifas, capacidades y registrar nuevas habitaciones sin intervención técnica. | Endpoints administrativos en FastAPI y migración Alembic para catálogo de 9 habitaciones. | Restricción de integridad: no es posible eliminar habitaciones que cuenten con reservas vigentes. |
| **CHG-04** | **Módulo de Salgados Café y Restaurante** | Integrar los consumos gastronómicos y catas de café a la cuenta unificada de la habitación o pago de mostrador. | Tablas `restaurant_order` y liquidación acumulada en el check-out de la habitación. | Validación de folio activo antes de permitir la imputación de cargos a habitación. |
| **CHG-05** | **Motor de Eventos y Tarifas Dinámicas** | Habilitar promociones y recargos automáticos por temporadas festivas o días de baja demanda. | Tabla `special_events` y recálculo dinámico del total cotizado en web y WhatsApp. | Reglas de precedencia de fechas que evitan solapamiento incoherente de promociones. |
| **CHG-06** | **Autenticación Institucional JWT y RBAC** | Proteger el panel web con login formal, tokens JWT firmados criptográficamente y roles Administrador/Recepcionista. | Protección de endpoints de FastAPI con dependencias `require_role` y almacenamiento seguro en memoria. | Expiración de tokens a las 8 horas y hashing robusto de contraseñas. |

### 3.2 Comité y Autorización Formal de la Versión Final

- **Evaluación Técnica de Arquitectura:** Aprobada por Juan Felipe Garzón (*Development Team*) y Esteban Guarín Valencia (*Scrum Master*).
- **Aprobación de Negocio y Criterios de Aceptación:** Autorizada por Juan José Arias Gallego (*Product Owner*).
- **Dictamen del Comité de Cambios:** Aprobado por unanimidad. Los cambios eliminan deuda técnica, suprimen servicios innecesarios (Redis), garantizan consistencia ACID absoluta y blindan la operación del hotel.

---

## Componente 4. Validación y Pruebas del Servicio

### 4.1 Matriz Consolidada de Pruebas de Utilidad y Garantía

| Tipo de Prueba | Escenario Evaluado | Resultado Esperado | Resultado Obtenido | Evidencia Registrada | Estado | Responsable |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **Funcional** | Reserva completa vía WhatsApp con abono del 50%. | Creación de reserva con código `SAT-XXXX`, abono registrado y reflejo en web. | Código `SAT-XXXX` emitido en 1.1s; reserva visible en recepción. | Registro en base de datos PostgreSQL y log de n8n. | **Aprobado** | Juan Felipe Garzón |
| **Funcional** | Creación y modificación dinámica de habitaciones por Administrador. | Habitación creada y modificable; impedimento de eliminar si tiene reservas activas. | Datos actualizados en catálogo; bloqueo referencial efectivo ante reservas activas. | Respuesta HTTP 200 en edición; HTTP 409 al intentar borrar habitación ocupada. | **Aprobado** | Juan Felipe Garzón |
| **Funcional** | Pedido de Salgados Café con cargo directo a habitación. | Ítems agregados al saldo de la habitación y consolidados para liquidación final. | Cargo reflejado en detalle de folio de habitación; balance actualizado al instante. | Orden de restaurante vinculada a ID de reserva en base de datos. | **Aprobado** | Juan José Arias |
| **Funcional** | Cotización con tarifa dinámica por evento especial de temporada. | Aplicación de descuento del 10% o recargo del 15% según rango de fechas. | Descuento aplicado matemáticamente en cotización web y conversacional. | Facturación detallada con desglose de evento aplicado. | **Aprobado** | Juan José Arias |
| **Integración** | Sincronización bidireccional Panel Web y Chatbot WhatsApp. | La confirmación de pago o check-in en web actualiza el estado visible en WhatsApp y viceversa. | Sincronización reactiva en tiempo real inferior a 2 segundos entre ambos canales. | Actualización en panel web mediante TanStack Query y eventos API. | **Aprobado** | Esteban Guarín V |
| **Seguridad** | Intento de sobreventa concurrente en la misma habitación y fechas. | El primer cliente adquiere el bloqueo; el segundo recibe rechazo atómico por base de datos. | Restricción PostgreSQL `EXCLUDE USING gist` aborta la segunda transacción con `ExclusionViolation`. | Log de excepción `409 Conflict` controlado y mensaje claro en chat. | **Aprobado** | Juan Felipe Garzón |
| **Seguridad** | Verificación de firma criptográfica en webhook de pagos. | Solo se procesan webhooks con firma HMAC SHA-256 válida provenientes de la pasarela. | Webhook con firma alterada retorna HTTP 401; webhook auténtico confirma la reserva. | Validación con `hmac.compare_digest` y verificación de idempotencia. | **Aprobado** | Juan Felipe Garzón |
| **Rendimiento** | Prueba de carga con 50 peticiones simultáneas de cotización. | Tiempos de respuesta inferiores a 1.5 segundos sin degradación del servicio. | Tiempo promedio de 620 ms en FastAPI Uvicorn gracias a sockets no bloqueantes. | Métricas registradas en benchmark de pruebas asíncronas. | **Aprobado** | Esteban Guarín V |
| **Recuperación** | Simulación de caída abrupta del contenedor de base de datos. | Restablecimiento de servicios y datos intactos a partir del volumen persistente. | Recuperación completa en 1 minuto y 30 segundos sin pérdida de registros. | Logs de arranque de PostgreSQL y verificación de tablas con Alembic. | **Aprobado** | Juan Felipe Garzón |
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
         |  - Mantenimiento y optimización de Postgres |
         |  - Soporte de webhooks y tokens de Meta/API |
         |  - Despliegue de parches con Alembic        |
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
- **Tasa de Sobreventas (*Overbooking Rate*):** Meta 0.0% estricto garantizado por la restricción GiST de PostgreSQL.
- **Tiempo Promedio de Respuesta en WhatsApp:** Meta < 2.0 segundos por interacción.
- **Tiempo de Respuesta API (/api/v1/health):** Meta < 50 milisegundos.

### 5.4 Procedimientos de Respaldo y Continuidad del Negocio

- **Respaldos Automáticos Diarios:** Ejecución programada vía cronjob a las 03:00 AM de volcado completo de PostgreSQL comprimido y cifrado.
- **Retención:** 30 copias de seguridad diarias, 12 mensuales y almacenamiento secundario en volumen independiente.
- **Prueba Periódica de Restauración:** Validación mensual de restauración en ambiente de pruebas para comprobar la consistencia de los datos.

### 5.5 Dependencias Externas y Gestión de Proveedores

- **Meta Cloud API (WhatsApp Business Platform):** Requiere vigencia del token permanente (System User) y saldo de conversaciones corporativas. En caso de interrupción de Meta, la operación conmuta al teléfono de soporte y atención directa en el panel web.
- **Google Cloud Platform (Gemini AI API):** Asistencia en lenguaje natural para consultas turísticas y amenidades. En caso de indisponibilidad de la IA, n8n conmuta automáticamente al flujo estructurado de menús deterministas.

---

## Componente 6. Gestión del Conocimiento y Transferencia

### 6.1 Documentación Técnica y Operativa Entregada

1. **Manual de Operación para Recepción:** Documento web interactivo con flujos visuales para búsqueda de códigos de reserva, check-in, check-out, registro de pedidos de Salgados Café y resolución de incidencias comunes.
2. **Guía Técnica de Despliegue y Administración:** Manual con especificaciones de Docker Compose, variables de entorno, comandos de control (`alembic upgrade head`), y procedimientos de respaldo.
3. **Catálogo de Arquitectura y Especificación de Endpoints:** Documentación OpenAPI interactiva generada en tiempo real en `/docs` (Swagger UI), con detalle de modelos Pydantic, restricciones GiST y contratos REST.
4. **Guía de Solución Rápida de Problemas (*Troubleshooting Guide*):** Árbol de diagnóstico para reinicio de servicios, verificación de conectividad a PostgreSQL y revalidación de webhooks.

### 6.2 Entrega Segura de Credenciales y Accesos

En estricto cumplimiento de las políticas de seguridad y la norma ITIL 4:
- Se prohíbe de manera tajante incluir contraseñas en texto claro dentro de la documentación.
- Las credenciales iniciales de acceso para el usuario Administrador (`admin@satoripms.com`) y el personal de Recepción (`recepcion@satoripms.com`) se entregaron en sobre cerrado al representante legal del hotel y a través de un canal criptográfico seguro efímero.
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
| **Huéspedes con Reservas Previas** | Notificación oficial vía WhatsApp | Mensaje de cortesía con su código de reserva `SAT-XXXX` y confirmación de servicios garantizados. | 48 horas antes de la transición |
| **Público General y Clientes Potenciales** | Redes sociales y señalética en el hotel | Anuncio del canal de reservas 24/7 en WhatsApp y código QR para cotización inmediata. | Día de apertura oficial del piloto |

### 7.2 Condiciones y Reglas de la Fase de Marcha Blanca (Piloto Controlado)

- **Duración del Piloto Controlado:** Quince (15) días calendario a partir de la fecha de autorización formal.
- **Alcance Operativo:** Operación integral sobre la totalidad de 9 habitaciones del hotel, servicios de Salgados Café y motor conversacional de reservas.
- **Acompañamiento Técnico Activo:** Presencia y monitoreo continuo del equipo de desarrollo durante las primeras 72 horas para calibración de respuestas y verificación de transacciones.
- **Canal de Reporte Inmediato de Incidentes:** Línea directa de mensajería y enlace dedicado con el equipo de soporte técnico para atención de novedades operativas.

---

## Componente 8. Aceptación y Cierre de la Transición

### 8.1 Evaluación de Criterios de Aceptación Final

- [x] **Arquitectura Anti-Sobreventa:** Cero casos de doble reserva verificados bajo pruebas de estrés concurrente con restricción nativa PostgreSQL 16 `EXCLUDE USING gist`.
- [x] **Panel Web Funcional y Seguro:** Login institucional con JWT, gestión dinámica de habitaciones (CRUD de Administrador), módulo de Salgados Café con pedidos y motor de eventos estacionales.
- [x] **Sincronización Transaccional:** Integración entre el panel web de recepción y el flujo de WhatsApp con códigos únicos `SAT-XXXX`.
- [x] **Personal Operativo Capacitado:** 100% del personal de recepción y administración capacitado y evaluado satisfactoriamente.
- [x] **Respaldo y Seguridad de la Información:** Rutinas automatizadas de copia de seguridad activas y probadas.
- [x] **Documentación Entregada:** Manuales de usuario, arquitectura OpenAPI y guías técnicas debidamente transferidas.

### 8.2 Defectos Conocidos y Riesgos Residuales Aceptados

- **Dependencia de la Disponibilidad Global de Meta:** Ante interrupciones de la infraestructura de WhatsApp, la recepción opera de forma autónoma mediante llamadas telefónicas y registro directo en el panel web.
- **Curva de Adaptación del Huésped:** Algunos usuarios mayores prefieren asistencia telefónica directa; el sistema contempla el botón de derivación a recepcionista humano en WhatsApp.

### 8.3 Dictamen Formal de Puesta en Servicio

Habiéndose demostrado de forma rigurosa la utilidad funcional de la solución tecnológica y satisfecho cabalmente todas las condiciones de garantía, rendimiento, seguridad y continuidad bajo las buenas prácticas del marco ITIL 4:

**DICTAMEN FINAL:** **AUTORIZADO PARA PUESTA EN SERVICIO EN MODALIDAD DE PILOTO CONTROLADO (MARCHA BLANCA).**

Firmado y aprobado por el Equipo de Dirección del Proyecto:
- **Esteban Guarín Valencia** — *Scrum Master*
- **Juan José Arias Gallego** — *Product Owner*
- **Juan Felipe Garzón** — *Development Team*
