# Módulo — Infraestructura y Despliegue

## 1. Servicios en Contenedores

| Servicio | Contenedor | Puerto expuesto | Rol |
|---|---|---|---|
| PostgreSQL 16 | `satori_postgres` | `127.0.0.1:5432` (solo local) | Fuente de verdad; restricción anti-doble-reserva |
| Redis 7 | `satori_redis` | `127.0.0.1:6379` (solo local) | Sesión conversacional del chatbot y bloqueos temporales de habitaciones |
| n8n | `satori_n8n` | `5678` | Orquestación del chatbot de WhatsApp |
| Backend API | `satori_api` | `8080` | Dueño único de las reglas de negocio; emite eventos en tiempo real |
| App Web | Sin contenedor | `5173` (Vite, en desarrollo) | Panel de recepcionista y administrador |

Los servicios se definen en Docker Compose y se comunican por la red interna de Docker. n8n invoca al backend con la dirección interna configurada en `API_BASE_URL`, por ejemplo `http://api:8080`. Solo PostgreSQL y Redis quedan restringidos a la interfaz local del host. En producción, el webhook de WhatsApp, el backend y la aplicación web se publican detrás de HTTPS.

## 2. Imagen del Backend

La imagen usa un enfoque de compilación en dos etapas.

1. **Compilación en el host.** El JAR se genera con Maven local en la máquina del desarrollador, no dentro de Docker, lo que reduce el tiempo de recompilación a unos 3 segundos.
2. **Runtime en contenedor.** El contenedor usa únicamente una imagen `eclipse-temurin:21-jre`, sin Maven ni JDK, donde se monta o copia el JAR ya compilado. Así la imagen final se mantiene pequeña.

## 3. Persistencia de Datos

Docker Compose define volúmenes nombrados para conservar los datos entre reinicios.

| Volumen | Ruta en el contenedor | Contenido |
|---|---|---|
| `postgres_data` | `/var/lib/postgresql/data` | Datos de la base de datos |
| `redis_data` | `/data` | Datos de Redis |
| `n8n_data` | `/home/node/.n8n` | Configuración y flujos de n8n |

## 4. Script de Arranque

El script de desarrollo `start-dev.sh` levanta el entorno completo en este orden.

1. Compila el JAR con Maven local (`mvn package -DskipTests`).
2. Levanta todos los servicios de Docker Compose (PostgreSQL, Redis, n8n y API), según los perfiles definidos en `COMPOSE_PROFILES`.
3. Inicia el servidor de desarrollo del frontend (Vite).

El script no incluye ninguna automatización de túneles. Para exponer n8n a internet, requisito de los webhooks de WhatsApp de Meta, se usa un servicio de túnel externo de forma manual, sin que esté integrado en el flujo de arranque. En desarrollo, `N8N_PUBLIC_URL` debe apuntar a la URL del túnel activo.

## 5. Variables de Entorno

| Grupo | Variables |
|---|---|
| Base de datos | `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` |
| Redis | `REDIS_HOST`, `REDIS_PORT` |
| Backend | `PORT`, `JWT_SECRET`, `JWT_EXPIRES_IN`, `BOOKING_TEST_PAYMENT_ENABLED` |
| WhatsApp y Meta | `META_APP_ID`, `META_APP_SECRET`, `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID`, `WHATSAPP_ACCOUNT_ID`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_GRAPH_VERSION` |
| IA | `GEMINI_API_KEY` |
| Google Reviews | `GOOGLE_PLACE_ID` |
| Pasarela de pago | `MERCADOPAGO_ACCESS_TOKEN`, `MERCADOPAGO_WEBHOOK_SECRET` |
| n8n | `COMPOSE_PROFILES`, `N8N_PUBLIC_URL`, `N8N_BASIC_AUTH_USER`, `N8N_BASIC_AUTH_PASSWORD`, `N8N_BLOCK_ENV_ACCESS_IN_NODE`, `API_BASE_URL` |
| Frontend | `VITE_API_URL`, `VITE_WS_URL` |

`N8N_BLOCK_ENV_ACCESS_IN_NODE=false` es requerido para que los nodos de n8n puedan leer `$env.*`, como los tokens de WhatsApp y Gemini y el `GOOGLE_PLACE_ID` del enlace de reseñas. `N8N_PUBLIC_URL` es la dirección pública que usa n8n para registrar sus webhooks con Meta. `WHATSAPP_GRAPH_VERSION` fija la versión de la Graph API de Meta que usa el flujo. `BOOKING_TEST_PAYMENT_ENABLED` habilita el modo de prueba de pagos del backend.

## 6. Patrón de Archivos Sensibles

El archivo `.env`, con los valores reales, nunca se sube al repositorio; solo se versiona una plantilla `.env.example` con los nombres de las variables. El mismo patrón aplica a los archivos reales de semilla de base de datos (`V*__seed_*.sql`), que quedan fuera del control de versiones, mientras que sus plantillas (`.sql.example`) sí se versionan.
