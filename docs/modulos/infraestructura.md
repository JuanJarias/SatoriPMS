# Módulo — Infraestructura y Despliegue

### 1. Servicios en Contenedores

| Servicio | Contenedor | Puerto expuesto | Rol |
|---|---|---|---|
| PostgreSQL 16 | `satori_postgres` | `127.0.0.1:5432` (solo local) | Fuente de verdad; restricción anti-doble-reserva |
| Redis 7 | `satori_redis` | `127.0.0.1:6379` (solo local) | Sesión conversacional del chatbot y bloqueos temporales de habitaciones |
| n8n | `satori_n8n` | `5678` | Orquestación del chatbot de WhatsApp |
| Backend API | `satori_api` | `8080` | Dueño único de las reglas de negocio; emite eventos en tiempo real |
| App Web | — | `5173` (Vite, en desarrollo) | Panel de recepcionista/administrador |

---

### 2. Imagen del Backend

La imagen utiliza un enfoque de compilación en dos etapas:
1. **Compilación en el host:** El JAR se genera con Maven local en la máquina del desarrollador (no dentro de Docker), lo que reduce el tiempo de re-compilación a ~3 segundos.
2. **Runtime en contenedor:** El contenedor usa únicamente una imagen `eclipse-temurin:21-jre` (sin Maven ni JDK), donde se monta/copia el JAR ya compilado, manteniendo la imagen final pequeña.

---

### 3. Persistencia de Datos

Docker Compose define volúmenes nombrados para la persistencia entre reinicios:
- `postgres_data` → `/var/lib/postgresql/data` — Datos de la base de datos.
- `redis_data` → `/data` — Datos de Redis.
- `n8n_data` → `/home/node/.n8n` — Configuración y flujos de n8n.

---

### 4. Script de Arranque (`start-dev.sh`)

El script de desarrollo levanta el entorno completo en orden:
1. Compila el JAR con Maven local (`mvn package -DskipTests`).
2. Levanta todos los servicios de Docker Compose (Postgres, Redis, n8n, API).
3. Inicia el servidor de desarrollo del frontend (Vite).

No incluye ninguna automatización de túneles. Para exponer n8n al internet (requisito de los webhooks de WhatsApp de Meta), se usa un servicio de túnel externo de forma manual, sin que esté integrado en el flujo de arranque.

---

### 5. Variables de Entorno

| Grupo | Variables |
|---|---|
| Base de datos | `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` |
| Redis | `REDIS_HOST`, `REDIS_PORT` |
| Backend | `PORT`, `JWT_SECRET`, `JWT_EXPIRES_IN`, `BOOKING_TEST_PAYMENT_ENABLED` |
| WhatsApp / Meta | `META_APP_ID`, `META_APP_SECRET`, `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID`, `WHATSAPP_ACCOUNT_ID`, `WHATSAPP_VERIFY_TOKEN` |
| IA | `GEMINI_API_KEY` |
| Pasarela de pago | `MERCADOPAGO_ACCESS_TOKEN`, `MERCADOPAGO_WEBHOOK_SECRET` |
| n8n | `COMPOSE_PROFILES`, `N8N_PUBLIC_URL`, `N8N_BASIC_AUTH_USER`, `N8N_BASIC_AUTH_PASSWORD`, `N8N_BLOCK_ENV_ACCESS_IN_NODE` |
| Frontend | `VITE_API_URL`, `VITE_WS_URL` |

> **Importante:** `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` es requerido para que los nodos de n8n puedan leer `$env.*` (tokens de WhatsApp, Gemini, etc.). `N8N_PUBLIC_URL` es la dirección pública que usa n8n para registrar sus webhooks con Meta; debe apuntar a la URL del túnel activo en desarrollo.

---

### 6. Patrón de Archivos Sensibles

El archivo `.env` (con los valores reales) nunca se sube al repositorio; solo se versiona una plantilla `.env.example` con los nombres de las variables. El mismo patrón aplica a los archivos reales de semilla de base de datos (`V*__seed_*.sql`), que quedan fuera de control de versiones, mientras que sus plantillas (`.sql.example`) sí se versionan.
