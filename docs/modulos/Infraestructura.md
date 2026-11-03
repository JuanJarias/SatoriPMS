# Infraestructura y Despliegue — SatoriPMS

## 1. Propósito del Módulo

El documento de **Infraestructura y Despliegue** describe cómo se organizan, conectan y mantienen en funcionamiento los servicios tecnológicos que componen **SatoriPMS**, tanto cuando se ejecutan en un computador local para desarrollo y pruebas como cuando se despliegan en el servidor de producción para la operación continua de **Torre Satori**.

---

## 2. Componentes de la Infraestructura

La plataforma está diseñada bajo un esquema modular de contenedores mediante **Docker Compose** ([docker-compose.yml](file:///home/guarinve/Documentos/SatoriPMS/docker-compose.yml)), lo que garantiza que el sistema funcione de manera idéntica en cualquier servidor Linux sin configuraciones manuales complejas:

| Servicio | Nombre del Contenedor | Tecnología | Puerto Local | Función en el Sistema |
|---|---|---|---|---|
| **Base de Datos Principal** | `satori-postgres` | PostgreSQL 16 | `5433` (hacia `5432` interno) | Almacenamiento permanente de habitaciones, huéspedes, reservas, pagos, tienda, finanzas y reseñas. |
| **Memoria de Bloqueos y Sesiones** | `satori-redis` | Redis 7 | `6379` | Gestión de bloqueos temporales de habitaciones por 15 minutos y estado de las conversaciones activas de WhatsApp. |
| **Orquestador del Chatbot** | `satori-n8n` | n8n | `5678` | Ejecución del flujo conversacional de WhatsApp ([V8_ChatbotReservas.json](file:///home/guarinve/Documentos/SatoriPMS/flows/n8n/V8_ChatbotReservas.json)) y conexión con inteligencia artificial. |
| **Servidor Central (API)** | `satori-api` | Java 21 / Spring Boot 3.3 | `8080` | Lógica de negocio, reglas de tarifas, control de concurrencia y servicios para el chatbot y la web. |
| **Aplicación Web** | Ejecución en navegador / Servidor web | React 18 / TypeScript / Vite | `5173` (desarrollo) | Panel visual para recepción y administración del hotel. |

### Orden de Arranque y Verificación de Salud
El servidor central (`satori-api`) y el orquestador del chatbot (`satori-n8n`) están configurados para esperar automáticamente a que la base de datos (`satori-postgres`) y la memoria rápida (`satori-redis`) confirmen que están listas y saludables antes de iniciar, evitando errores de conexión durante el encendido del servidor.

---

## 3. Persistencia de Datos y Volúmenes

Para asegurar que ninguna información del hotel se pierda al reiniciar o actualizar el sistema, Docker mantiene tres espacios de almacenamiento permanente en disco:
1. `Volumen de base de datos : "postgres_data"`: Conserva todas las tablas y registros históricos de PostgreSQL.
2. `Volumen de memoria rápida : "redis_data"`: Resguarda los estados de sesión y bloqueos activos en Redis.
3. `Volumen del orquestador : "n8n_data"`: Conserva los flujos importados, credenciales e historial de ejecuciones de n8n.

---

## 4. Parámetros de Configuración (`.env`)

El sistema se configura a través de un archivo `.env` en la raíz del proyecto (generado a partir de la plantilla [.env.example](file:///home/guarinve/Documentos/SatoriPMS/.env.example)):

- **Base de datos:** `Usuario de base de datos : "POSTGRES_USER"`, `Contraseña de base de datos : "POSTGRES_PASSWORD"`, `Nombre de base de datos : "POSTGRES_DB"` y `Puerto local de base de datos : "POSTGRES_PORT"`.
- **Memoria rápida:** `Contraseña de Redis : "REDIS_PASSWORD"`, `Puerto de Redis : "REDIS_PORT"` y `Tiempo de bloqueo en segundos : "REDIS_LOCK_TTL"` (por defecto `900`, equivalente a 15 minutos).
- **Seguridad del servidor:** `Clave secreta de sesiones web : "JWT_SECRET"` y `Tiempo de vigencia de sesión : "JWT_EXPIRATION"`.
- **Orquestador y canales externos:** `Usuario de n8n : "N8N_BASIC_AUTH_USER"`, `Contraseña de n8n : "N8N_BASIC_AUTH_PASSWORD"`, `Clave de Google Gemini : "GEMINI_API_KEY"`, `Identificador de Google Maps : "GOOGLE_PLACE_ID"` y credenciales de conexión con WhatsApp y pasarela de pagos.

---

## 5. Puesta en Marcha Automatizada

El repositorio incluye el asistente de inicio [start-dev.sh](file:///home/guarinve/Documentos/SatoriPMS/start-dev.sh), el cual automatiza la puesta a punto del entorno:
1. Verifica que exista el archivo `.env` (creándolo desde `.env.example` si aún no existe).
2. Construye y levanta los contenedores en segundo plano.
3. Espera a que la base de datos y el servidor central respondan satisfactoriamente.
4. Importa y activa el flujo conversacional [V8_ChatbotReservas.json](file:///home/guarinve/Documentos/SatoriPMS/flows/n8n/V8_ChatbotReservas.json) dentro del contenedor de n8n, dejando el webhook listo para recibir mensajes.

---

## 6. Despliegue en Producción y Copias de Seguridad

Para la operación real de **Torre Satori** en producción:
- **Servidor en la nube (VPS):** Los contenedores se ejecutan en un servidor privado virtual Linux (4 GB de memoria RAM, 2 procesadores virtuales y disco de estado sólido), acompañado de túnel seguro y certificado digital administrado mediante Cloudflare para recibir los mensajes oficiales de Meta WhatsApp Cloud API.
- **Copias de seguridad automáticas:** Se programa una tarea diaria en horario de madrugada que genera un respaldo comprimido de la base de datos PostgreSQL y lo sincroniza con almacenamiento seguro en la nube (Cloudflare R2), garantizando que el hotel pueda restaurar la totalidad de su información en pocos minutos ante cualquier eventualidad física del servidor.
