# Módulo — Seguridad, Identidad y Cumplimiento

## 1. Autenticación y Autorización

**Mecanismo.** La aplicación web se autentica con JSON Web Tokens (JWT) firmados con una clave secreta y con un tiempo de expiración configurable mediante variables de entorno (`JWT_SECRET` y `JWT_EXPIRES_IN`). El token incluye el rol del usuario. El cliente web lo envía en cada solicitud y, cuando expira o es rechazado, regresa al inicio de sesión.

**Autorización por rol.** Existen dos roles, `admin` y `receptionist`, definidos con una restricción a nivel de base de datos. El backend valida el rol en cada solicitud; ocultar una opción en la interfaz nunca reemplaza esa validación. El administrador gestiona usuarios, configuración global y reportes financieros. La recepcionista opera reservas, estadías, tienda y conversaciones, sin acceso a reportes financieros globales ni a la administración de usuarios.

**Contraseñas.** Se almacenan con cifrado unidireccional BCrypt; nunca en texto plano ni en registros de log. La recuperación de contraseña (HU-11) permite restablecerla sin que la contraseña anterior se revele en ningún momento.

**Cuentas desactivadas.** Un usuario desactivado no puede iniciar sesión, pero conserva su historial en los registros de auditoría.

**CORS.** Solo los dominios autorizados (frontend local en desarrollo y dominio de producción) pueden realizar peticiones cruzadas a la API.

## 2. Seguridad de las Integraciones

**WhatsApp (Meta).** La verificación inicial del webhook (GET) valida el `hub.verify_token` contra `WHATSAPP_VERIFY_TOKEN`. Cada evento recibido (POST) se acepta solo si la firma criptográfica SHA-256 del encabezado `X-Hub-Signature-256`, calculada con el App Secret de Meta, coincide con el cuerpo recibido; los eventos sin firma válida se descartan. Cada `message_id` se registra para ignorar los reintentos duplicados de entrega.

**MercadoPago.** Una reserva solo se confirma por el webhook de pago, verificado con `MERCADOPAGO_WEBHOOK_SECRET`; nunca por una pantalla de éxito del cliente.

**Google Gemini.** La clave `GEMINI_API_KEY` solo vive en el entorno del backend y de n8n. Toda salida del modelo se trata como una sugerencia y se valida antes de aceptarla. Al modelo solo se envía la información mínima necesaria para interpretar el mensaje.

**Red interna.** PostgreSQL y Redis solo escuchan en `127.0.0.1`; el backend y n8n se comunican dentro de la red interna de Docker. Solo n8n (para el webhook de Meta), el backend y la aplicación web se exponen, y siempre por HTTPS.

## 3. Gestión de Secretos

Los secretos (`JWT_SECRET`, claves de bases de datos, tokens de WhatsApp, claves de Gemini y de MercadoPago) se definen exclusivamente por variables de entorno. El archivo `.env` real nunca se versiona; solo se versiona la plantilla `.env.example` con los nombres de las variables. Los valores de desarrollo no se reutilizan en producción, y los tokens de Meta y el secreto JWT se rotan periódicamente.

## 4. Trazabilidad y Auditoría (HU-15)

El sistema genera registros de auditoría inmutables para todas las acciones operativas críticas: creación, modificación y cancelación de reservas; ejecución de check-in y check-out; ventas de tienda y ajustes de inventario; registro, edición y eliminación de egresos; y cambios en usuarios del sistema, tarifas o políticas.

Cada registro almacena `timestamp`, `user_id`, `action_type`, `entity_id` y `details_json`. Los registros no se editan ni se eliminan desde la aplicación, y solo el administrador puede consultarlos, con filtros por fecha, usuario y tipo de acción.

## 5. Protección de Datos Personales (Ley 1581 de 2012, Colombia)

La Ley Estatutaria 1581 de 2012 desarrolla el derecho de las personas a conocer, actualizar y rectificar la información que se recoge sobre ellas en bases de datos, y aplica a cualquier entidad que trate datos personales en Colombia. SatoriPMS la aplica con las siguientes medidas.

**Necesidad y finalidad.** El chatbot y la aplicación web solo recolectan los datos esenciales para prestar el servicio de hospedaje: nombre, número de WhatsApp y documento de identidad, además de los nombres de los acompañantes. Los datos solo se usan para la finalidad informada: gestionar la reserva y la estadía, y mejorar el servicio.

**Autorización.** Antes de recolectar datos en el canal conversacional, el chatbot presenta el aviso de privacidad con la finalidad del tratamiento y los derechos del titular.

**Derechos del titular.** El huésped puede solicitar conocer, actualizar, rectificar o suprimir sus datos ante el hotel. Los datos asociados a registros contables o a obligaciones legales se conservan por el tiempo que la norma exige.

**Seguridad y confidencialidad.** El tráfico se protege con HTTPS en todos los canales. Los datos sensibles se ofuscan en los archivos de log y no aparecen en enlaces públicos. El acceso a la información de huéspedes se limita según el rol, y los archivos de soporte (recibos y facturas) se protegen con permisos y enlaces controlados.
