# Guía de Configuración de Variables de Entorno (.env) — SatoriPMS

Este documento proporciona una guía exhaustiva, paso a paso y sin requerir conocimientos técnicos previos, para configurar correctamente el archivo de variables de entorno `.env` en la raíz de **SatoriPMS**. 

Las variables de entorno son parámetros de configuración y secretos (claves de acceso, credenciales de base de datos, tokens de comunicación) que el sistema necesita para conectar el servidor central (API), el motor de base de datos, la memoria de concurrencia, el asistente de WhatsApp en n8n, la inteligencia artificial de Gemini y la pasarela de pagos de Mercado Pago.

---

## Tabla de Contenidos

- [Instrucciones Iniciales y Creación del Archivo](#instrucciones-iniciales-y-creación-del-archivo)
- [1. Base de Datos Relacional (PostgreSQL)](#1-base-de-datos-relacional-postgresql)
  - [DATABASE_URL](#database_url)
  - [POSTGRES_USER](#postgres_user)
  - [POSTGRES_PASSWORD](#postgres_password)
  - [POSTGRES_DB](#postgres_db)
- [2. Memoria en Caché y Bloqueo Concurrente (Redis)](#2-memoria-en-caché-y-bloqueo-concurrente-redis)
  - [REDIS_URL](#redis_url)
- [3. Servidor Central (Backend API)](#3-servidor-central-backend-api)
  - [PORT](#port)
  - [JWT_SECRET](#jwt_secret)
  - [JWT_EXPIRES_IN](#jwt_expires_in)
- [4. Integración con Meta for Developers y WhatsApp Cloud API](#4-integración-con-meta-for-developers-y-whatsapp-cloud-api)
  - [META_APP_ID](#meta_app_id)
  - [META_APP_SECRET](#meta_app_secret)
  - [WHATSAPP_TEST_PHONE](#whatsapp_test_phone)
  - [WHATSAPP_TOKEN](#whatsapp_token)
  - [WHATSAPP_PHONE_ID](#whatsapp_phone_id)
  - [WHATSAPP_ACCOUNT_ID](#whatsapp_account_id)
  - [WHATSAPP_VERIFY_TOKEN](#whatsapp_verify_token)
  - [WHATSAPP_GRAPH_VERSION](#whatsapp_graph_version)
- [5. Inteligencia Artificial (Google Gemini)](#5-inteligencia-artificial-google-gemini)
  - [GEMINI_API_KEY](#gemini_api_key)
- [6. Pasarela de Pagos (Mercado Pago)](#6-pasarela-de-pagos-mercado-pago)
  - [MERCADOPAGO_ACCESS_TOKEN](#mercadopago_access_token)
  - [MERCADOPAGO_WEBHOOK_SECRET](#mercadopago_webhook_secret)
  - [BOOKING_TEST_PAYMENT_ENABLED](#booking_test_payment_enabled)
- [7. Automatización del Chatbot (n8n)](#7-automatización-del-chatbot-n8n)
  - [COMPOSE_PROFILES](#compose_profiles)
  - [N8N_BASIC_AUTH_USER](#n8n_basic_auth_user)
  - [N8N_BASIC_AUTH_PASSWORD](#n8n_basic_auth_password)
  - [N8N_PUBLIC_URL](#n8n_public_url)
- [8. Panel Web de Recepción (Frontend)](#8-panel-web-de-recepción-frontend)
  - [VITE_API_URL](#vite_api_url)
  - [VITE_WS_URL](#vite_ws_url)
- [Resumen de Ubicación y Verificación](#resumen-de-ubicación-y-verificación)

---

## Instrucciones Iniciales y Creación del Archivo

1. Abra una terminal en el directorio raíz del proyecto (`.` o su equivalente local).
2. Cree una copia local del archivo plantilla [.env.example](../.env.example) con el nombre exacto `.env`:
   ```bash
   cp .env.example .env
   ```
3. Abra el archivo `.env` en su editor de código preferido.
4. **Regla de seguridad fundamental:** El archivo `.env` contiene contraseñas y claves privadas reales. Jamás debe compartirse por correo, redes o subirse a repositorios públicos de control de versiones. El archivo ya se encuentra protegido e ignorado en el archivo `.gitignore`.

---

## 1. Base de Datos Relacional (PostgreSQL)

### DATABASE_URL
- **Para qué sirve:** Define la cadena de conexión JDBC completa que utiliza el servidor central para comunicarse con el motor de base de datos PostgreSQL, autenticarse y realizar consultas de lectura y escritura.
- **De dónde se saca:** Es una combinación estándar compuesta por el usuario, la contraseña, el host (nombre de máquina o contenedor), el puerto y el nombre de la base de datos.
- **Cómo obtenerlo y configurarlo:**
  - *Requisitos previos:* Tener Docker instalado para desplegar el contenedor de PostgreSQL.
  - *Valores predeterminados para desarrollo local:*
    ```env
    DATABASE_URL=jdbc:postgresql://satori:satori_dev@localhost:5432/satoripms
    ```
  - *Estructura de la URL:* `jdbc:postgresql://<USUARIO>:<PASSWORD>@<HOST>:<PUERTO>/<NOMBRE_BD>`.
  - Si el backend corre dentro de la red interna de Docker Compose, el host cambia de `localhost` a `postgres`.
- **En dónde ponerlo:** En la sección `# ── Base de datos` del archivo `.env`.

---

### POSTGRES_USER
- **Para qué sirve:** Es el nombre de usuario administrativo que Docker asigna a PostgreSQL al inicializar el contenedor por primera vez.
- **De dónde se saca:** Lo define usted libremente. Para el entorno de SatoriPMS, el valor estándar es `satori`.
- **Cómo obtenerlo y configurarlo:**
  - Escriba directamente el nombre de usuario deseado.
  - Valor recomendado:
    ```env
    POSTGRES_USER=satori
    ```
- **En dónde ponerlo:** En la variable `POSTGRES_USER` del archivo `.env`.

---

### POSTGRES_PASSWORD
- **Para qué sirve:** Contraseña de seguridad que protege la base de datos contra accesos no autorizados.
- **De dónde se saca:** Lo define usted libremente.
- **Cómo obtenerlo y configurarlo:**
  - Para desarrollo local se utiliza `satori_dev`.
  - Para servidores en producción, genere una contraseña robusta de al menos 16 caracteres alfanuméricos aleatorios.
  - Valor para desarrollo:
    ```env
    POSTGRES_PASSWORD=satori_dev
    ```
- **En dónde ponerlo:** En la variable `POSTGRES_PASSWORD` del archivo `.env`.

---

### POSTGRES_DB
- **Para qué sirve:** Nombre del catálogo o base de datos relacional dentro de PostgreSQL donde se crean las tablas de reservas, habitaciones, huéspedes y transacciones.
- **De dónde se saca:** Lo define usted libremente.
- **Cómo obtenerlo y configurarlo:**
  - Valor estándar del proyecto:
    ```env
    POSTGRES_DB=satoripms
    ```
- **En dónde ponerlo:** En la variable `POSTGRES_DB` del archivo `.env`.

---

## 2. Memoria en Caché y Bloqueo Concurrente (Redis)

### REDIS_URL
- **Para qué sirve:** Cadena de conexión para acceder al servidor Redis, el cual administra las sesiones activas del chatbot de WhatsApp y ejecuta el "Candado Rápido" (bloqueos temporales atómicos de 15 minutos que previenen sobreventas).
- **De dónde se saca:** Es la dirección de red donde corre el servicio de Redis.
- **Cómo obtenerlo y configurarlo:**
  - Para pruebas ejecutadas localmente desde la máquina anfitriona:
    ```env
    REDIS_URL=redis://localhost:6379
    ```
  - Si el servicio corre dentro de la red de Docker: el contenedor de backend resuelve el host automáticamente como `redis:6379`.
- **En dónde ponerlo:** En la variable `REDIS_URL` del archivo `.env`.

---

## 3. Servidor Central (Backend API)

### PORT
- **Para qué sirve:** Puerto de red TCP en el cual el servidor central escucha peticiones HTTP entrantes.
- **De dónde se saca:** Estándar de configuración de red local.
- **Cómo obtenerlo y configurarlo:**
  - Valor estándar:
    ```env
    PORT=8080
    ```
- **En dónde ponerlo:** En la variable `PORT` del archivo `.env`.

---

### JWT_SECRET
- **Para qué sirve:** Clave secreta criptográfica (HMAC-SHA256) empleada por el servidor central para firmar digitalmente los tokens de sesión de los administradores y recepcionistas. Garantiza que nadie pueda alterar o falsificar su identidad al interactuar con el sistema.
- **De dónde se saca:** Es una cadena aleatoria y secreta que debe generar el administrador del sistema.
- **Cómo obtenerlo paso a paso:**
  - *Requisitos previos:* Disponer de una terminal con el comando `openssl` o utilizar un generador seguro.
  - *Comando en terminal (Linux / macOS):*
    ```bash
    openssl rand -hex 32
    ```
  - Copie el resultado (una secuencia de 64 caracteres hexadecimales).
  - *Ejemplo de formato:*
    ```env
    JWT_SECRET=4f8b9d2e1c3a7f6e5d4c3b2a109876543210abcdef0123456789abcdef012345
    ```
- **En dónde ponerlo:** En la variable `JWT_SECRET` del archivo `.env`.

---

### JWT_EXPIRES_IN
- **Para qué sirve:** Determina el tiempo de vigencia de la sesión de un usuario en el panel web antes de requerir que inicie sesión nuevamente.
- **De dónde se saca:** Lo define la política de seguridad del hotel.
- **Cómo configurarlo:**
  - Formato: número seguido de la unidad de tiempo (`h` para horas, `d` para días).
  - Valor recomendado (un turno de recepción completo):
    ```env
    JWT_EXPIRES_IN=8h
    ```
- **En dónde ponerlo:** En la variable `JWT_EXPIRES_IN` del archivo `.env`.

---

## 4. Integración con Meta for Developers y WhatsApp Cloud API

Para que el hotel pueda enviar y recibir mensajes automáticos por WhatsApp, se requiere una cuenta en la plataforma para desarrolladores de Meta (Facebook).

### META_APP_ID
- **Para qué sirve:** Identificador numérico público único de la aplicación registrada en la plataforma de Meta.
- **De dónde se saca:** En el panel de control de su aplicación en Meta for Developers.
- **Cómo obtenerlo paso a paso:**
  1. *Requisitos previos:* Cuenta personal de Facebook y número de teléfono móvil para verificación.
  2. Ingrese en el navegador a: [https://developers.facebook.com/](https://developers.facebook/)
  3. Si es su primera vez, haga clic en el botón superior derecho **Empezar** o **Iniciar sesión**.
  4. En la barra superior, haga clic en **Mis apps** (o **My Apps**).
  5. Seleccione su aplicación creada para el hotel (si no tiene una, haga clic en **Crear app**, elija el caso de uso **Otro** o **Negocios**, asigne el nombre "Satori Hotel Chatbot" y confirme).
  6. En la parte superior izquierda de la pantalla, debajo del nombre de su app, verá la etiqueta **Identificador de la app:** (o **App ID:**) seguida de un número de 15 o 16 dígitos.
  7. Haga clic en el icono de copiar situado junto al número.
- **En dónde ponerlo:**
  ```env
  META_APP_ID=1234567890123456
  ```

---

### META_APP_SECRET
- **Para qué sirve:** Clave secreta que autentica la identidad de la aplicación ante los servidores de Meta al procesar webhooks o solicitar tokens de larga duración.
- **De dónde se saca:** En los ajustes básicos de la aplicación en Meta for Developers.
- **Cómo obtenerlo paso a paso:**
  1. Dentro de su aplicación en [https://developers.facebook.com/apps/](https://developers.facebook.com/apps/).
  2. En el menú lateral izquierdo, despliegue **Configuración de la app** (icono de engranaje) y haga clic en **Información básica**.
  3. En el panel central, localice el campo denominado **Clave secreta de la app** (o **App Secret**).
  4. Haga clic en el botón **Mostrar** (le solicitará reingresar la contraseña de su cuenta de Facebook por seguridad).
  5. Copie la cadena alfanumérica resultante.
- **En dónde ponerlo:**
  ```env
  META_APP_SECRET=a1b2c3d4e5f67890123456789abcdef0
  ```

---

### WHATSAPP_TEST_PHONE
- **Para qué sirve:** Número de teléfono personal autorizado para enviar y recibir mensajes durante la etapa de pruebas (Sandbox de WhatsApp Cloud API).
- **De dónde se saca:** Es el número telefónico propio o de prueba del administrador o evaluador.
- **Cómo configurarlo:**
  - Debe incluir el código de país sin el símbolo `+`, espacios ni guiones (por ejemplo, para Colombia: `57` seguido del número de diez dígitos).
  - *Ejemplo:*
    ```env
    WHATSAPP_TEST_PHONE=573001234567
    ```
  - *Importante:* En la consola de Meta, en la sección **WhatsApp** > **Configuración de la API**, en el campo **Para** (o **To**), debe registrar este mismo número y verificarlo ingresando el código OTP de 6 dígitos que Meta le enviará a su WhatsApp.
- **En dónde ponerlo:** En la variable `WHATSAPP_TEST_PHONE` del archivo `.env`.

---

### WHATSAPP_TOKEN
- **Para qué sirve:** Token de autorización (Bearer Token) que viaja en la cabecera HTTP de cada mensaje que n8n o el servidor central envían hacia la API de WhatsApp de Meta.
- **De dónde se saca:** En la sección de configuración de la API de WhatsApp de Meta.
- **Cómo obtenerlo paso a paso:**
  1. En el panel de su app en Meta for Developers, observe el menú lateral izquierdo.
  2. Haga clic en **WhatsApp** y luego seleccione **Configuración de la API** (o **API Setup**).
  3. En la sección central superior verá un recuadro titulado **Token de acceso temporal** (válido por 24 horas para pruebas inmediatas).
  4. Para un token permanente de producción:
     - En el menú lateral de Meta Business Suite ([https://business.facebook.com/](https://business.facebook/)), ingrese a **Configuración del negocio** > **Usuarios del sistema**.
     - Añada un usuario del sistema con rol de Administrador.
     - Asigne el activo de la aplicación y genere un token seleccionando los permisos `whatsapp_business_messaging` y `whatsapp_business_management`.
  5. Copie el token generado (empieza comúnmente con `EAA...`).
- **En dónde ponerlo:**
  ```env
  WHATSAPP_TOKEN=EAAG...
  ```

---

### WHATSAPP_PHONE_ID
- **Para qué sirve:** Identificador numérico del número de teléfono emisor configurado en los servidores de Meta. No es el número telefónico legible, sino el identificador interno que Meta asigna a dicho número.
- **De dónde se saca:** En la pantalla de Configuración de la API de WhatsApp en Meta for Developers.
- **Cómo obtenerlo paso a paso:**
  1. En el panel de su aplicación de Meta, diríjase en el menú izquierdo a **WhatsApp** > **Configuración de la API**.
  2. En el paso 1 titulado **Enviar y recibir mensajes**, observe el desplegable **De** (o **From**).
  3. Inmediatamente debajo de ese campo, observará una casilla etiquetada como **Identificador del número de teléfono** (o **Phone number ID**).
  4. Haga clic en el botón de copiar situado a la derecha del número (ej. `105432987654321`).
- **En dónde ponerlo:**
  ```env
  WHATSAPP_PHONE_ID=105432987654321
  ```

---

### WHATSAPP_ACCOUNT_ID
- **Para qué sirve:** Identificador único de la Cuenta de WhatsApp Business (WABA ID) que engloba los números de teléfono, plantillas y configuraciones comerciales del hotel.
- **De dónde se saca:** En la misma pantalla de Configuración de la API de WhatsApp en Meta for Developers.
- **Cómo obtenerlo paso a paso:**
  1. En la misma pantalla (**WhatsApp** > **Configuración de la API**).
  2. Justo al lado o debajo del Identificador del número de teléfono, observará el campo denominado **Identificador de la cuenta de WhatsApp Business** (o **WhatsApp Business Account ID**).
  3. Haga clic en el botón de copiar situado a la derecha de la cifra.
- **En dónde ponerlo:**
  ```env
  WHATSAPP_ACCOUNT_ID=209876543210987
  ```

---

### WHATSAPP_VERIFY_TOKEN
- **Para qué sirve:** Palabra secreta o contraseña personalizada elegida por usted que Meta utiliza para comprobar que el Webhook configurado en n8n le pertenece a usted y está listo para recibir mensajes.
- **De dónde se saca:** Usted inventa esta palabra o frase secreta.
- **Cómo configurarlo y enlazarlo:**
  1. Elija una clave secreta segura, sin espacios ni caracteres especiales raros (ejemplo: `SatoriPMS_Webhook_Token_2026`).
  2. Escríbala en su archivo `.env`:
     ```env
     WHATSAPP_VERIFY_TOKEN=SatoriPMS_Webhook_Token_2026
     ```
  3. Posteriormente, en el panel de Meta for Developers:
     - Vaya a **WhatsApp** > **Configuración** (o **Configuration**).
     - En el apartado **Webhook**, haga clic en **Editar**.
     - En el campo **URL de devolución de llamada**, coloque la URL pública de su webhook de n8n (ej. `https://su-dominio.com/webhook/whatsapp`).
     - En el campo **Token de verificación**, pegue exactamente este mismo valor (`SatoriPMS_Webhook_Token_2026`).
     - Haga clic en **Verificar y guardar**.
- **En dónde ponerlo:** En la variable `WHATSAPP_VERIFY_TOKEN` del archivo `.env`.

---

### WHATSAPP_GRAPH_VERSION
- **Para qué sirve:** Indica la versión oficial de la API Graph de Meta que el sistema utiliza para garantizar compatibilidad con los contratos de mensajería y plantillas interactivas.
- **De dónde se saca:** Corresponde a la versión estable actual de la API de Meta.
- **Cómo configurarlo:**
  - Valor estándar recomendado:
    ```env
    WHATSAPP_GRAPH_VERSION=v25.0
    ```
- **En dónde ponerlo:** En la variable `WHATSAPP_GRAPH_VERSION` del archivo `.env`.

---

## 5. Inteligencia Artificial (Google Gemini)

### GEMINI_API_KEY
- **Para qué sirve:** Permite al nodo `Gemini Interpretar Respuesta` de n8n conectarse con el modelo de lenguaje de Google (Gemini) para extraer de forma estructurada (fechas, ocupación, nombres, documento, mascota) las solicitudes enviadas en lenguaje natural por los huéspedes en el Flujo 2 (Reserva con IA).
- **De dónde se saca:** En la plataforma para desarrolladores Google AI Studio.
- **Cómo obtenerlo paso a paso:**
  1. *Requisitos previos:* Disponer de una cuenta de Google (Gmail o Workspace).
  2. Ingrese en el navegador a: [https://aistudio.google.com/](https://aistudio.google.com/)
  3. Inicie sesión con su cuenta de Google.
  4. En el menú de navegación lateral izquierdo, localice y haga clic en la opción **Get API key** (con icono de llave).
  5. En la pantalla principal, haga clic en el botón azul **Create API key** (o **Crear clave de API**).
  6. Si le solicita asociar un proyecto de Google Cloud, elija la opción por defecto para crear un proyecto nuevo o seleccione uno existente de la lista.
  7. Una vez generada, se mostrará una ventana con la clave. Haga clic en el botón **Copy** (icono de dos rectángulos superpuestos).
- **En dónde ponerlo:**
  ```env
  GEMINI_API_KEY=AIzaSy...tu_clave_de_google_ai_studio
  ```

---

## 6. Pasarela de Pagos (Mercado Pago)

### MERCADOPAGO_ACCESS_TOKEN
- **Para qué sirve:** Clave privada que permite al servidor central generar órdenes de pago, enlaces de cobro para anticipos (50%) o pagos completos (100%) y consultar el estado de las transacciones de los huéspedes.
- **De dónde se saca:** En el panel para desarrolladores de Mercado Pago.
- **Cómo obtenerlo paso a paso:**
  1. *Requisitos previos:* Disponer de una cuenta registrada en Mercado Pago (de Colombia para Torre Satori).
  2. Ingrese en el navegador a: [https://www.mercadopago.com.co/developers](https://www.mercadopago.com.co/developers)
  3. Inicie sesión con su cuenta de Mercado Pago.
  4. En la barra superior derecha, haga clic en la opción **Tus integraciones** (o acceda a [https://www.mercadopago.com.co/developers/panel/app](https://www.mercadopago.com.co/developers/panel/app)).
  5. Seleccione su aplicación (o haga clic en **Crear aplicación**, asigne el nombre "SatoriPMS Pagos" y elija el modelo de integración Checkout Pro o Pagos Online).
  6. En el menú lateral izquierdo de su aplicación, haga clic en **Credenciales de prueba** (para pruebas sin dinero real) o en **Credenciales de producción** (para cobros reales).
  7. Localice el campo titulado **Access Token** (suele comenzar por `TEST-` en pruebas o `APP_USR-` en producción).
  8. Haga clic en el icono de copiar situado junto a la clave.
- **En dónde ponerlo:**
  ```env
  MERCADOPAGO_ACCESS_TOKEN=TEST-1234567890123456-abcdef0123456789-123456789
  ```

---

### MERCADOPAGO_WEBHOOK_SECRET
- **Para qué sirve:** Clave criptográfica que utiliza Mercado Pago para firmar las notificaciones de confirmación de pago (Webhooks). Permite que el servidor central verifique que el aviso de pago proviene legítimamente de Mercado Pago y no de un atacante simulando un pago falso.
- **De dónde se saca:** En la sección de configuración de Notificaciones Webhooks de su aplicación en Mercado Pago Developers.
- **Cómo obtenerlo paso a paso:**
  1. Dentro de su aplicación en [https://www.mercadopago.com.co/developers/panel/app](https://www.mercadopago.com.co/developers/panel/app).
  2. En el menú lateral izquierdo, haga clic en **Webhooks** (o **Notificaciones Webhooks**).
  3. Configure su URL de notificación apuntando al endpoint de su servidor (ej. `https://su-dominio.com/api/payments/webhook`).
  4. En la parte superior de esa misma sección observará un apartado titulado **Clave secreta de firma** (o **Secret signature**).
  5. Haga clic en el botón de copiar.
- **En dónde ponerlo:**
  ```env
  MERCADOPAGO_WEBHOOK_SECRET=f9a8b7c6d5e4f3a2b1...
  ```

---

### BOOKING_TEST_PAYMENT_ENABLED
- **Para qué sirve:** Bandera de control operativa que habilita o desactiva la simulación de pagos instantáneos en entornos de prueba locales sin necesidad de interactuar con la pasarela bancaria.
- **De dónde se saca:** Es una directiva interna de control del servidor central.
- **Cómo configurarlo:**
  - Para pruebas automatizadas y desarrollo local: `true`.
  - Para el entorno operativo real del hotel: `false`.
  - Valor recomendado inicial:
    ```env
    BOOKING_TEST_PAYMENT_ENABLED=true
    ```
- **En dónde ponerlo:** En la variable `BOOKING_TEST_PAYMENT_ENABLED` del archivo `.env`.

---

## 7. Automatización del Chatbot (n8n)

### COMPOSE_PROFILES
- **Para qué sirve:** Controla qué servicios secundarios levanta Docker Compose al ejecutar el comando de inicio. Si contiene `n8n`, levanta el orquestador del chatbot; si está vacío, levanta únicamente la base de datos, Redis y el backend.
- **Cómo configurarlo:**
  - Valor estándar para operar el hotel con chatbot:
    ```env
    COMPOSE_PROFILES=n8n
    ```
- **En dónde ponerlo:** En la variable `COMPOSE_PROFILES` del archivo `.env`.

---

### N8N_BASIC_AUTH_USER
- **Para qué sirve:** Nombre de usuario requerido en la ventana de autenticación básica del navegador al acceder a la interfaz web de n8n (`http://localhost:5678`).
- **De dónde se saca:** Lo define usted libremente.
- **Cómo configurarlo:**
  - Valor estándar recomendado:
    ```env
    N8N_BASIC_AUTH_USER=SatoriPMS
    ```
- **En dónde ponerlo:** En la variable `N8N_BASIC_AUTH_USER` del archivo `.env`.

---

### N8N_BASIC_AUTH_PASSWORD
- **Para qué sirve:** Contraseña requerida en la ventana de autenticación básica de n8n para impedir accesos no autorizados al editor de flujos.
- **De dónde se saca:** La define usted libremente.
- **Cómo configurarlo:**
  - Elija una contraseña segura.
  - *Ejemplo:*
    ```env
    N8N_BASIC_AUTH_PASSWORD=SatoriSeguro2026*
    ```
- **En dónde ponerlo:** En la variable `N8N_BASIC_AUTH_PASSWORD` del archivo `.env`.

---

### N8N_PUBLIC_URL
- **Para qué sirve:** Es la dirección web pública con certificado SSL (HTTPS) accesible desde Internet hacia su instancia de n8n. Meta exige obligatoriamente una URL segura (HTTPS) para entregar los mensajes entrantes de WhatsApp mediante Webhook.
- **De dónde se saca:** Proviene de su dominio web con certificado SSL o de un túnel seguro temporal (zrok, ngrok, Cloudflare Tunnel).
- **Cómo obtenerlo paso a paso:**
  - *Si utiliza zrok (herramienta integrada en el proyecto):*
    1. Ejecute en su terminal:
       ```bash
       zrok share public http://localhost:5678
       ```
    2. La terminal mostrará un mensaje indicando la URL pública generada (ej. `https://n8n-chatbot.shares.zrok.io/`).
    3. Copie esa URL completa terminada en barra diagonal (`/`).
  - *Si utiliza un dominio propio del hotel:*
    Coloque el subdominio configurado (ej. `https://bot.torresatori.com/`).
- **En dónde ponerlo:**
  ```env
  N8N_PUBLIC_URL=https://n8n-chatbot.shares.zrok.io/
  ```

---

## 8. Panel Web de Recepción (Frontend)

### VITE_API_URL
- **Para qué sirve:** Dirección base que el navegador web del recepcionista o administrador utiliza para realizar peticiones HTTP (consultar calendario de habitaciones, registrar huéspedes, ver reservas, liquidar cuentas).
- **De dónde se saca:** Es la dirección de red donde se encuentra escuchando el servidor central.
- **Cómo configurarlo:**
  - Para ejecución local en el equipo de desarrollo:
    ```env
    VITE_API_URL=http://localhost:8080
    ```
  - Para despliegue en red local del hotel:
    ```env
    VITE_API_URL=http://192.168.1.50:8080
    ```
- **En dónde ponerlo:** En la variable `VITE_API_URL` del archivo `.env`.

---

### VITE_WS_URL
- **Para qué sirve:** Dirección del protocolo WebSocket (`ws://` o `wss://`) que utiliza el panel web para recibir actualizaciones y alertas en tiempo real (por ejemplo, notificación instantánea cuando un huésped en WhatsApp solicita atención de una recepcionista humana o cuando entra una nueva reserva).
- **De dónde se saca:** Es el mismo host y puerto del servidor central, pero empleando el protocolo `ws://`.
- **Cómo configurarlo:**
  - Para desarrollo local:
    ```env
    VITE_WS_URL=ws://localhost:8080
    ```
  - Para servidores con certificado SSL en producción:
    ```env
    VITE_WS_URL=wss://api.torresatori.com
    ```
- **En dónde ponerlo:** En la variable `VITE_WS_URL` del archivo `.env`.

---

## Resumen de Ubicación y Verificación

Una vez completadas todas las variables, el archivo `.env` en la raíz del proyecto debe tener una estructura completa como la siguiente:

```env
# Base de datos
DATABASE_URL=jdbc:postgresql://satori:satori_dev@localhost:5432/satoripms
POSTGRES_USER=user
POSTGRES_PASSWORD=password_dev
POSTGRES_DB=satoripms

# Redis
REDIS_URL=redis://localhost:6379

# Servidor Central
PORT=8080
JWT_SECRET=4f8b9d2e1c3a7f6e5d4c3b2a109876543210abcdef0123456789abcdef012345
JWT_EXPIRES_IN=8h

# WhatsApp / Meta
META_APP_ID=1234567890123456
META_APP_SECRET=a1b2c3d4e5f67890123456789abcdef0
WHATSAPP_TEST_PHONE=573001234567
WHATSAPP_TOKEN=EAAG...
WHATSAPP_PHONE_ID=105432987654321
WHATSAPP_ACCOUNT_ID=209876543210987
WHATSAPP_VERIFY_TOKEN=Webhook_Token_2026
WHATSAPP_GRAPH_VERSION=v25.0

# Inteligencia Artificial
GEMINI_API_KEY=AIzaSy...

# Pasarela de Pago
MERCADOPAGO_ACCESS_TOKEN=TEST-...
MERCADOPAGO_WEBHOOK_SECRET=f9a8b7...
BOOKING_TEST_PAYMENT_ENABLED=true

# n8n
COMPOSE_PROFILES=n8n
N8N_BASIC_AUTH_USER=SatoriPMS
N8N_BASIC_AUTH_PASSWORD=cambia_esta_password
N8N_PUBLIC_URL=https://n8n-chatbot.shares.zrok.io/

# Frontend
VITE_API_URL=http://localhost:8080
VITE_WS_URL=ws://localhost:8080
```

### Verificación de Arranque
Para comprobar que todos los servicios leen correctamente sus variables de entorno:
```bash
# Iniciar servicios con Docker Compose
docker compose up -d

# Verificar el estado de salud de los contenedores
docker compose ps
```
Todos los contenedores (`satori_postgres`, `satori_redis`, `satori_api` y `satori_n8n`) deben figurar en estado `running` o `healthy`.
