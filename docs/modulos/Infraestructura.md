# Infraestructura y Despliegue — SatoriPMS

## 1. Propósito del Módulo

El documento de **Infraestructura y Despliegue** describe cómo se organizan, conectan y mantienen en funcionamiento los servicios tecnológicos que componen **SatoriPMS**, tanto cuando se ejecutan en un computador local para desarrollo y pruebas como cuando se despliegan en el servidor de producción para la operación continua de **Torre Satori**.

---

## 2. Componentes de la Infraestructura

La plataforma está diseñada bajo un esquema modular de contenedores mediante **Docker Compose** ([docker-compose.yml](../../docker-compose.yml)), lo que garantiza que el sistema funcione de manera idéntica en cualquier servidor Linux sin configuraciones manuales complejas:

| Servicio | Nombre del Contenedor | Tecnología | Puerto Local | Función en el Sistema |
|---|---|---|---|---|
| **Base de Datos Principal** | `satori_postgres` | PostgreSQL 16 | `5432` (solo accesible desde el propio equipo) | Almacenamiento permanente de habitaciones, huéspedes, reservas, pagos, tienda, finanzas y reseñas. |
| **Memoria de Bloqueos y Sesiones** | `satori_redis` | Redis 7 | `6379` (solo accesible desde el propio equipo) | Gestión de bloqueos temporales de habitaciones por 15 minutos y estado de las conversaciones activas de WhatsApp. |
| **Servidor Central (API)** | `satori_api` | Java 21 / Spring Boot 3.3.5 | `8080` | Lógica de negocio, reglas de tarifas, control de concurrencia, control de acceso y servicios para el chatbot y la web. |
| **Orquestador del Chatbot** | `satori_n8n` | n8n 2.47.3 | `5678` | Ejecución del flujo conversacional de WhatsApp ([V9_ChatbotReservas.json](../../flows/n8n/V9_ChatbotReservas.json)), conexión con inteligencia artificial y con la pasarela de pagos Wompi. Se activa con el perfil `n8n`. |

La **Aplicación Web** (React 18 / TypeScript / Vite) no se ejecuta como contenedor en el entorno local: se inicia con el asistente de arranque y queda disponible en el puerto `5173`.

### Orden de Arranque y Verificación de Salud
El servidor central (`satori_api`) espera automáticamente a que la base de datos (`satori_postgres`) y la memoria rápida (`satori_redis`) confirmen que están listas y saludables antes de iniciar. El orquestador del chatbot (`satori_n8n`) espera además a que el servidor central haya iniciado, evitando errores de conexión durante el encendido del servidor.

---

## 3. Persistencia de Datos y Volúmenes

Para asegurar que ninguna información del hotel se pierda al reiniciar o actualizar el sistema, Docker mantiene tres espacios de almacenamiento permanente en disco:
1. `Volumen de base de datos : "postgres_data"`: Conserva todas las tablas y registros históricos de PostgreSQL.
2. `Volumen de memoria rápida : "redis_data"`: Resguarda los estados de sesión y bloqueos activos en Redis.
3. `Volumen del orquestador : "n8n_data"`: Conserva los flujos importados, credenciales e historial de ejecuciones de n8n.

---

## 4. Parámetros de Configuración (`.env`)

El sistema se configura a través de un archivo `.env` en la raíz del proyecto (generado a partir de la plantilla [.env.example](../../.env.example)):

- **Base de datos:** `Usuario de base de datos : "POSTGRES_USER"`, `Contraseña de base de datos : "POSTGRES_PASSWORD"` y `Nombre de base de datos : "POSTGRES_DB"`.
- **Seguridad del servidor:** `Clave secreta de las sesiones del personal : "JWT_SECRET"` (mínimo 32 caracteres), `Vigencia de la sesión : "JWT_EXPIRATION_MS"`, `Llave de servicio del chatbot : "SATORI_SERVICE_KEY"` (compartida por el servidor central y n8n), `Orígenes web autorizados : "CORS_ALLOWED_ORIGINS"` y, de forma opcional, el administrador inicial (`SATORI_ADMIN_USERNAME` y `SATORI_ADMIN_PASSWORD`).
- **Orquestador y canales externos:** `Usuario de n8n : "N8N_BASIC_AUTH_USER"`, `Contraseña de n8n : "N8N_BASIC_AUTH_PASSWORD"`, `Dirección pública de n8n : "N8N_PUBLIC_URL"`, `Clave de Google Gemini : "GEMINI_API_KEY"`, `Identificador del hotel en Google : "GOOGLE_PLACE_ID"`, credenciales de WhatsApp Cloud API y credenciales de la pasarela de pagos Wompi.

El detalle de cada parámetro y cómo obtenerlo se encuentra en la [Guía de Configuración del Entorno](../Guia_Configuracion_Entorno.md).

---

## 5. Puesta en Marcha Automatizada

El repositorio incluye un conjunto de asistentes en la carpeta [scripts/](../../scripts/), cada uno con una sola responsabilidad:

| Asistente | Función |
|---|---|
| [start-dev.sh](../../scripts/start-dev.sh) | Verifica las herramientas y los parámetros obligatorios del archivo `.env`, construye y levanta los contenedores, espera a que la base de datos, la memoria rápida, el servidor central y el orquestador respondan, abre el túnel público del orquestador e inicia la aplicación web. Al terminar presenta los enlaces de acceso. |
| [stop-dev.sh](../../scripts/stop-dev.sh) | Detiene la aplicación web, el túnel y los contenedores sin borrar ninguna información. |
| [reset-dev.sh](../../scripts/reset-dev.sh) | Elimina contenedores e información almacenada para empezar desde cero, previa confirmación expresa. Puede conservar el orquestador del chatbot y volver a cargar datos de prueba. |
| [status-dev.sh](../../scripts/status-dev.sh) | Diagnóstico de solo lectura: estado de los servicios, del túnel público y de la conexión con WhatsApp (vigencia de la credencial y suscripción de la aplicación del hotel). |
| [sync-n8n-flow.sh](../../scripts/sync-n8n-flow.sh) | Publica en el orquestador la versión vigente del flujo conversacional ([V9_ChatbotReservas.json](../../flows/n8n/V9_ChatbotReservas.json)) y lo reinicia para que el cambio quede activo. |

---

## 6. Despliegue en Producción y Copias de Seguridad

Para la operación real de **Torre Satori** en producción:
- **Servidor en la nube (VPS):** Los contenedores se ejecutan en un servidor privado virtual Linux (4 GB de memoria RAM, 2 procesadores virtuales y disco de estado sólido), acompañado de túnel seguro y certificado digital administrado mediante Cloudflare para recibir los mensajes oficiales de Meta WhatsApp Cloud API.
- **Copias de seguridad automáticas:** Se programa una tarea diaria en horario de madrugada que genera un respaldo comprimido de la base de datos PostgreSQL y lo sincroniza con almacenamiento seguro en la nube (Cloudflare R2), garantizando que el hotel pueda restaurar la totalidad de su información en pocos minutos ante cualquier eventualidad física del servidor.
