# Seguridad y Protección de Datos — SatoriPMS

## 1. Propósito del Módulo

El módulo de **Seguridad y Protección de Datos** define las medidas de resguardo de la información, el control de acceso del personal del hotel y el cumplimiento legal en el tratamiento de los datos personales de los huéspedes de **Torre Satori**.

---

## 2. Control de Acceso por Roles en la Aplicación Web

El acceso a las funciones administrativas y operativas del panel web se protege mediante inicio de sesión con usuario y contraseña, emitiendo una credencial digital firmada con vigencia controlada (`Credencial de sesión : "JWT"` configurada con `Clave secreta de firma : "JWT_SECRET"` y `Tiempo de expiración : "JWT_EXPIRATION"`).

El sistema distingue estrictamente dos perfiles de usuario:

| Funcionalidad del Sistema | Administrador (`"admin"`) | Recepcionista (`"receptionist"`) |
|---|---|---|
| Consultar calendario de ocupación y disponibilidad | Permitido | Permitido |
| Registrar llegadas (Check-in), salidas (Check-out) y reservas manuales | Permitido | Permitido |
| Atender conversaciones de WhatsApp escaladas a humano | Permitido | Permitido |
| Registrar ventas y cargos de la tienda interna | Permitido | Permitido |
| **Crear, editar y eliminar habitaciones del hotel** | **Exclusivo Administrador** | No permitido |
| **Configurar eventos especiales, temporadas y descuentos** | **Exclusivo Administrador** | No permitido |
| **Administrar catálogo de productos, precios y ajuste de inventario** | **Exclusivo Administrador** | No permitido |
| **Consultar reportes financieros, registrar gastos y exportar Excel contable** | **Exclusivo Administrador** | No permitido |
| **Configurar parámetros de turnos y liquidar pagos de nómina** | **Exclusivo Administrador** | No permitido |
| **Crear, editar o desactivar cuentas de usuarios del personal** | **Exclusivo Administrador** | No permitido |

### Reglas de Cuentas del Personal
- **Almacenamiento seguro de contraseñas:** Ninguna contraseña se guarda en texto visible; el sistema almacena únicamente su huella criptográfica irreversible (`Contraseña cifrada : "password_hash"`).
- **Retiro de personal sin pérdida de historial:** Cuando un empleado deja de laborar en el hotel, su cuenta no se elimina físicamente de la base de datos para conservar el registro histórico de qué operaciones realizó en su momento; en su lugar, el administrador desactiva la cuenta (`Usuario activo : "active = false"`), bloqueando de inmediato su ingreso al sistema.

---

## 3. Seguridad en las Comunicaciones y el Chatbot

1. **Aislamiento de servicios internos:** La base de datos principal y el motor de memoria rápida se ejecutan dentro de una red interna privada de contenedores y no están expuestos a internet público. Únicamente el servidor de aplicaciones y el canal de recepción de mensajes de WhatsApp reciben tráfico externo autorizado.
2. **Verificación de autenticidad de mensajes de WhatsApp:** Las notificaciones entrantes desde la plataforma oficial de Meta incluyen una firma criptográfica en su encabezado (`Firma de seguridad de Meta : "X-Hub-Signature-256"`), la cual permite validar que el mensaje proviene genuinamente de WhatsApp y no de un tercero no autorizado.
3. **Control de mensajes duplicados:** En caso de que la red telefónica o Meta reenvíe un mismo mensaje por intermitencia de conexión, el sistema identifica el código único del mensaje (`Identificador de mensaje : "message_id"`) para evitar procesarlo dos veces.
4. **Protección de claves y credenciales:** Todas las contraseñas de base de datos, llaves de inteligencia artificial (`Clave de Google Gemini : "GEMINI_API_KEY"`) y tokens de conexión a WhatsApp (`Token de WhatsApp : "WHATSAPP_API_TOKEN"`) se cargan desde variables de entorno locales ([.env.example](file:///home/guarinve/Documentos/SatoriPMS/.env.example)) excluidas del repositorio de código.

---

## 4. Cumplimiento de la Ley 1581 de 2012 (Protección de Datos Personales)

En cumplimiento del régimen colombiano de Habeas Data y protección de datos personales:
- **Aviso de privacidad e información previa:** Tanto en el flujo de reserva guiada paso a paso como en el asistente con inteligencia artificial en WhatsApp, antes de recopilar el nombre completo y el número de documento de identidad del huésped, el asistente presenta el aviso de privacidad informando que los datos suministrados serán tratados por Torre Satori con la única finalidad de gestionar su reserva, registro hotelero y facturación.
- **Finalidad exclusiva y confidencialidad:** Los números telefónicos, nombres, documentos de identidad y registros de acompañantes se utilizan únicamente para la prestación del servicio de hospedaje y no se comparten ni comercializan con terceros.

---

## 5. Trazabilidad y Auditoría de Operaciones Críticas

Para brindar total transparencia al propietario del hotel, el sistema contempla el registro de auditoría de las acciones sensibles realizadas desde el panel web:
- Creación, modificación de tarifas o eliminación de habitaciones.
- Creación o modificación de eventos especiales y descuentos por fechas.
- Cancelaciones manuales de reservas y aplicación de reembolsos.
- Ajustes de precios o de existencias en la tienda interna y registro de egresos financieros.
Cada evento conserva la fecha y hora exacta, el usuario responsable y el detalle de la modificación realizada.
