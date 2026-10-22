# Módulo — Aplicación Web (Recepción y Administración)

## 1. Arquitectura del Frontend

La aplicación está desarrollada con **React y Vite** bajo un modelo de Single Page Application, con enrutamiento declarativo mediante `react-router-dom` y gestión asíncrona del estado del servidor con `@tanstack/react-query`. El diseño se construye con Tailwind CSS. El cliente HTTP intercepta cada solicitud para incluir automáticamente el token de autenticación JWT, y redirige al inicio de sesión cuando el token expira o es rechazado.

La aplicación se actualiza en tiempo real mediante un canal WebSocket con protocolo STOMP, por el que el backend propaga los eventos de cambios en habitaciones, nuevas reservas y conversaciones escaladas, sin necesidad de recargar la página. Las variables `VITE_API_URL` y `VITE_WS_URL` definen las direcciones del backend REST y del canal WebSocket.

## 2. Control de Acceso y Roles

El acceso requiere iniciar sesión con usuario y contraseña. El backend devuelve un JWT con el rol del usuario, y la interfaz muestra únicamente las vistas y acciones permitidas para ese rol. El backend vuelve a validar el rol en cada solicitud, de modo que ocultar una opción en la interfaz nunca es la única barrera de seguridad.

| Rol | Alcance de permisos |
|---|---|
| **Administrador** | Gestión de usuarios del sistema, configuración global de precios y políticas, auditoría de logs y reportes financieros consolidados. |
| **Recepcionista** | Operación diaria de reservas (creación manual, check-in y check-out), catálogo y ventas de la tienda, y atención de conversaciones escaladas. Sin acceso a reportes financieros globales ni a la administración de usuarios. |

Las contraseñas nunca se almacenan en texto plano; se cifran con BCrypt. Cualquier usuario puede recuperar su contraseña desde la pantalla de inicio de sesión (HU-11).

## 3. Funcionalidades y Vistas Principales

### 3.1 Panel de Habitaciones y Calendario (HU-03)

El panel muestra las habitaciones en cuadrícula o en línea de tiempo, con el estado operativo de cada una: `Disponible`, `Ocupada`, `En limpieza`, `Mantenimiento` y `Bloqueo temporal`. Este último aparece mientras la habitación está retenida por un bloqueo vigente de 15 minutos y desaparece al confirmarse la reserva o vencer el bloqueo. La vista admite filtros por tipo de habitación y por rango de fechas, y se actualiza en tiempo real sin recargar la página cuando ocurre un check-in, un check-out, una reserva nueva o un cambio de estado.

### 3.2 Gestión Operativa de Estadías (CU-03 y CU-04)

**Check-in (CU-03).** La recepcionista busca la reserva confirmada por código, nombre o documento del titular. El sistema muestra el detalle de la reserva y valida el documento del titular. Si las condiciones cambian, la recepcionista ajusta el número de personas y el sistema recalcula el cargo adicional por RN-01, rechazando el ajuste si supera la capacidad máxima. Se registran los acompañantes finales. Al confirmar, la habitación pasa a `Ocupada` y la reserva a `En curso`. El evento se propaga a todos los clientes conectados para actualizar el calendario.

**Check-out (CU-04).** La recepcionista abre la estadía en curso y el sistema consolida el resumen: el valor del hospedaje, lo abonado y los consumos de tienda cargados a la habitación que aún no se han pagado. Con ese consolidado se calcula el saldo final. Al completar el check-out, la habitación pasa a `En limpieza`, la reserva queda finalizada, se emite el comprobante de pago (RN-05) y el sistema envía al huésped por WhatsApp la solicitud de reseña.

### 3.3 Gestión de Reservas Manuales (CU-08)

La recepción crea reservas presenciales o telefónicas desde la aplicación. La creación admite la opción de check-in inmediato, que ejecuta el check-in automáticamente al crear la reserva. La modificación de fechas revalida la disponibilidad y la capacidad en tiempo real y recalcula el precio. La cancelación manual aplica la política de reembolso de RN-03 y exige registrar el motivo. Todas las operaciones generan el registro financiero correspondiente cuando aplica.

Una reserva es independiente del canal de origen: una reserva hecha por el chatbot o por la aplicación web tiene la misma estructura en la base de datos, y el campo `source` solo identifica el canal.

### 3.4 Centro de Conversaciones y Chatbot

El centro de conversaciones muestra en tiempo real las sesiones del chatbot de WhatsApp y destaca la lista de conversaciones escaladas pendientes de atención humana. Cuando un huésped solicita un agente dentro del horario de atención (7:00 a. m. a 11:00 p. m.), la conversación aparece como escalada y se notifica a la recepción mediante el canal de eventos en tiempo real.

La recepcionista puede responder al huésped desde este mismo centro: el backend envía sus mensajes a través de la WhatsApp Cloud API por el número del hotel. También puede atender la conversación desde la aplicación WhatsApp Business, y en ese caso el centro de conversaciones solo se usa para gestionar el estado. En ambos casos el huésped conversa con el mismo número.

La opción **Marcar como resuelta** cierra la atención humana: desactiva el silenciamiento del bot y reactiva la IA, de modo que el siguiente mensaje del huésped se atiende desde el menú principal. La conversación también se cierra automáticamente por inactividad o cuando el huésped escribe exclusivamente una palabra de salida como "menú".

### 3.5 Tienda e Inventario

La vista permite dar de alta y editar productos (nombre, descripción, precio, stock, categoría y foto de factura), registrar ventas directas con descuento automático de inventario, y cargar consumos a la habitación durante la estadía para liquidarlos en el check-out. Un producto con historial de ventas no se elimina, solo se desactiva (RN-04). La vista de rotación lista los productos por cantidad vendida en un rango de fechas, en orden ascendente o descendente (HU-14). El detalle funcional está en el módulo de Tienda e Inventario.

### 3.6 Finanzas y Reportes

Los egresos operativos se registran con categoría, fecha, valor y soporte digital (HU-13). La consulta consolidada muestra ingresos (hospedaje y tienda) y egresos por período (CU-06). El informe mensual se exporta a Excel (HU-01). El sueldo del recepcionista se calcula de forma automática según el modelo que define el administrador (HU-07). Estas vistas son exclusivas del administrador, salvo el registro de ventas de tienda. El detalle funcional está en el módulo de Facturación y Finanzas.

### 3.7 Reseñas (HU-10)

El panel de reseñas, disponible para el administrador y la recepcionista, muestra la calificación promedio, el listado filtrable por fecha, puntuación o fuente (`chatbot`, `google`, `web`) y el detalle de los comentarios.

### 3.8 Administración de Usuarios y Auditoría (HU-05, HU-11 y HU-15)

El administrador gestiona las cuentas de administradores y recepcionistas: crear, editar y desactivar. Un usuario desactivado conserva su historial en los registros de auditoría, pero no puede iniciar sesión.

El registro de auditoría lista las acciones operativas (reserva, cancelación, check-in, check-out, venta, ajuste de inventario, cambio de usuario o de tarifas) con fecha, hora, usuario y tipo de acción, y es filtrable por el administrador.

## 4. Notificaciones y Confirmaciones en la Interfaz

Las operaciones muestran notificaciones tipo toast para éxito y error. Las acciones críticas, como cancelar una reserva, completar un check-out, desactivar un usuario o desactivar un producto, piden confirmación en un diálogo modal que resume el efecto de la acción antes de ejecutarla.
