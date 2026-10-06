# Módulo — Seguridad, Identidad y Cumplimiento

### 1. Autenticación y Autorización

* **Mecanismo:** JSON Web Tokens (JWT) firmados con clave secreta y tiempo de expiración configurable vía variable de entorno.
* **Políticas de CORS:** Control estricto de dominios autorizados para peticiones cruzadas (frontend local y de producción).
* **Gestión de contraseñas:** Cifrado unidireccional de contraseñas de usuarios administradores y recepcionistas mediante BCrypt.

---

### 2. Trazabilidad y Auditoría (HU-15)

El sistema genera registros de auditoría inmutables para todas las acciones operativas críticas:
* Creación, modificación y cancelación de reservas.
* Ejecución de check-in y check-out.
* Ventas de tienda y ajustes de inventario.
* Cambios en usuarios del sistema o tarifas.

Cada registro almacena: `timestamp`, `user_id`, `action_type`, `entity_id`, `details_json`.

---

### 3. Protección de Datos Personales (Ley 1581 de 2012 - Colombia)

En cumplimiento del marco legal colombiano sobre tratamiento de datos personales:
* **Principio de necesidad y finalidad:** El chatbot y la app web solo recolectan datos esenciales para la prestación del servicio de hospedaje (Nombre, WhatsApp, Documento de identidad).
* **Autorización:** Inclusión de aviso de privacidad antes de la recolección de datos en el canal conversacional.
* **Seguridad:** Tráfico protegido mediante HTTPS en todos los canales y ofuscación de datos sensibles en archivos de log.
