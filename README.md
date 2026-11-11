# SatoriPMS — Sistema de Gestión Hotelera y Reservas Automatizadas

**SatoriPMS** es la plataforma integral de administración hotelera y atención automatizada diseñada para **Torre Satori** (Sevilla, Valle del Cauca). Su objetivo es modernizar la operación diaria del hotel, ofreciendo atención continua a los huéspedes a través de WhatsApp y centralizando el control administrativo, financiero y de recepción en una aplicación web intuitiva.

> [!NOTE]
> **Backend en migración a FastAPI; legado en el tag `legacy-java-backup`**.

---

## Contextualización y Propósito

En la operación hotelera tradicional, la atención manual de mensajes por WhatsApp, el control de disponibilidad en hojas de cálculo y la falta de sincronización entre recepción y ventas generan demoras de respuesta, pérdida de clientes fuera del horario laboral y riesgo de sobreventa de habitaciones.

**SatoriPMS** resuelve esta necesidad mediante un sistema unificado que:
- Atiende a los viajeros las 24 horas del día por WhatsApp, tanto mediante un menú guiado paso a paso como mediante un asistente con inteligencia artificial capaz de comprender solicitudes en lenguaje natural.
- Garantiza que dos personas no puedan reservar la misma habitación en las mismas fechas mediante un bloqueo temporal de 15 minutos mientras el huésped completa sus datos y realiza su pago.
- Permite abonar el 50% de anticipo o el 100% del valor de la estadía, liquidar saldos pendientes, cancelar reservas aplicando las políticas de reembolso del hotel y recopilar reseñas de los huéspedes con enlace directo a Google Maps.
- Brinda al personal de recepción y a la administración un panel web para gestionar el catálogo de habitaciones (referencia actual de 9 habitaciones configurables), tarifas por temporada o eventos especiales, llegadas y salidas de huéspedes, ventas de productos de vitrina, control de inventario y reportes financieros.

---

## Cómo Funciona

1. **Canal de Atención por WhatsApp:** El viajero escribe al número del hotel y el asistente virtual le muestra la disponibilidad real según las fechas, la cantidad de adultos y niños, y si viaja con mascota.
2. **Reserva Protegida y Pagos:** Al elegir una habitación, el sistema la reserva temporalmente durante 15 minutos para ese huésped, solicita los datos del titular y acompañantes (previa aceptación del aviso de privacidad) y registra el pago del anticipo (50%) o del total (100%), entregando un código único de reserva.
3. **Gestión en el Hotel (Aplicación Web):** El recepcionista visualiza la ocupación en tiempo real, atiende conversaciones escaladas a un operador humano, registra el ingreso y la salida de los huéspedes, y anota consumos adicionales de la tienda interna a la cuenta de la habitación.
4. **Administración y Finanzas:** El administrador gestiona la creación, edición y eliminación segura de habitaciones, define eventos especiales o descuentos por fechas, supervisa el inventario y descarga el balance contable mensual.

---

## Tecnologías Utilizadas

- **Servidor Central (Backend):** Python 3.12 con FastAPI (monolito modular), encargado de las reglas de negocio, concurrencia en base de datos y autenticación RBAC.
- **Base de Datos Principal:** PostgreSQL 16 con extensión `btree_gist` y control de versiones mediante Alembic.
- **Orquestación del Chatbot e Inteligencia Artificial:** n8n conectado con la plataforma oficial de WhatsApp (Meta Cloud API) y Google Gemini 2.0 Flash.
- **Aplicación Web de Recepción y Administración:** React 18 con TypeScript y Vite.
- **Infraestructura Local:** Contenedores Docker y Docker Compose para ejecutar los servicios de forma aislada y reproducible.

---

## Requisitos Previos

Para inicializar el proyecto en un entorno local se requiere contar con:
- **Docker** (versión 24 o superior) y **Docker Compose** (versión 2.20 o superior).
- **Node.js** (versión 20 o superior) y **npm** (para ejecutar la interfaz web en modo de desarrollo).
- **Git** para clonar el repositorio y gestionar versiones.

---

## Configuración Necesaria

1. **Variables de Entorno:**
   En la raíz del proyecto se incluye la plantilla [.env.example](file:///home/guarinve/Documentos/SatoriPMS/.env.example). Cópiala con el nombre `.env` y completa las contraseñas locales y las claves de conexión:
   ```bash
   cp .env.example .env
   ```

2. **Datos Iniciales del Hotel (Plantillas de Semilla):**
   Para proteger la información comercial del hotel, las plantillas de habitaciones y productos vienen con extensión `.example`. Para cargar los datos de referencia (incluidas las 9 habitaciones de prueba), genera los archivos locales:
   ```bash
   cp apps/api/src/main/resources/db/migration/V2__seed_rooms.sql.example \
      apps/api/src/main/resources/db/migration/V2__seed_rooms.sql

   cp apps/api/src/main/resources/db/migration/V6__seed_products.sql.example \
      apps/api/src/main/resources/db/migration/V6__seed_products.sql
   ```

---

## Instrucciones de Instalación e Inicialización (Infraestructura Local)

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/JuanJarias/SatoriPMS.git
   cd SatoriPMS
   ```

2. **Levantar la infraestructura local:**
   Puedes utilizar el asistente automático de inicio o ejecutar Docker Compose directamente:
   ```bash
   ./start-dev.sh
   ```
   O de forma manual:
   ```bash
   docker compose up -d --build
   ```

3. **Servicios disponibles en el entorno local:**
   - **Servidor Principal (API FastAPI):** `http://localhost:8080`
   - **Orquestador del Chatbot (n8n):** `http://localhost:5678` (en la primera ejecución, importa y activa el flujo [V8_ChatbotReservas.json](file:///home/guarinve/Documentos/SatoriPMS/flows/n8n/V8_ChatbotReservas.json)).
   - **Base de Datos (PostgreSQL):** Puerto local `5432`.

4. **Iniciar la aplicación web (opcional para desarrollo visual):**
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```
   La interfaz estará disponible en `http://localhost:5173`.

---

## Documentación Detallada

Toda la documentación funcional, de diseño, diagramas y presupuesto del proyecto se encuentra organizada en la carpeta [docs/](file:///home/guarinve/Documentos/SatoriPMS/docs/README.md). Consulta el [índice de documentación](file:///home/guarinve/Documentos/SatoriPMS/docs/README.md) para explorar cada módulo.

---

## Cómo Contribuir

1. Crea una rama descriptiva a partir de la rama de trabajo vigente (`feat/nombre-funcionalidad` o `fix/nombre-correccion`).
2. Realiza tus cambios verificando que los contenedores levanten sin errores y que las pruebas del flujo conversacional en [tests/chatbot/](file:///home/guarinve/Documentos/SatoriPMS/tests/chatbot) se ejecuten satisfactoriamente.
3. Actualiza la documentación correspondiente en [docs/](file:///home/guarinve/Documentos/SatoriPMS/docs/README.md) manteniendo el registro de avance en [EstadoActual.md](file:///home/guarinve/Documentos/SatoriPMS/docs/modulos/EstadoActual.md) y el detalle de commits pendientes en [CambiosPendientes.md](file:///home/guarinve/Documentos/SatoriPMS/docs/CambiosPendientes.md).
4. Abre una solicitud de integración (Pull Request) describiendo el propósito y alcance de los cambios realizados.
