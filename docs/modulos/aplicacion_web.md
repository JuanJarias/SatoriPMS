# Módulo — Aplicación Web (Recepción y Administración)

### 1. Arquitectura del Frontend

Desarrollada con **React + Vite** bajo un modelo de Single Page Application (SPA), con enrutamiento declarativo (`react-router-dom`) y gestión asíncrona de estado del servidor mediante `@tanstack/react-query`. El cliente HTTP intercepta las solicitudes para incluir automáticamente el token de autenticación JWT.

La aplicación se actualiza en tiempo real mediante un canal WebSocket con protocolo STOMP, que propaga eventos desde el backend (cambios en habitaciones, nuevas reservas, conversaciones escaladas) sin necesidad de recargar la página.

---

### 2. Control de Acceso y Roles

| Rol | Alcance de Permisos |
|---|---|
| **Administrador** | Gestión de usuarios del sistema, configuración global de precios y políticas, auditoría de logs, reportes financieros consolidados. |
| **Recepcionista** | Operación diaria de reservas (creación manual, check-in, check-out), catálogo y ventas de la tienda, atención de conversaciones escaladas. Sin acceso a reportes financieros globales ni administración de usuarios. |

Las contraseñas nunca se almacenan en texto plano (cifrado BCrypt).

---

### 3. Funcionalidades y Vistas Principales

#### 3.1 Panel de Habitaciones y Calendario (HU-03)
* Visualización en cuadrícula o línea de tiempo con los estados operativos de cada habitación: `Disponible`, `Ocupada`, `En limpieza`, `Mantenimiento`, `Bloqueo temporal`.
* Filtros por tipo de habitación y rango de fechas.
* Actualización en tiempo real sin recargar la página.

#### 3.2 Gestión Operativa de Estadías (CU-03, CU-04)
* **Check-in (CU-03):** Búsqueda de reserva confirmada, validación del documento del titular, ajuste de número de personas si cambian las condiciones (recalcula cargo por RN-01), registro de acompañantes finales y cambio del estado de habitación a `Ocupada` y reserva a `En curso`.
* **Check-out (CU-04):** Consolidación de consumos de tienda pendientes, cálculo de saldo final, liberación de la habitación (cambio a estado `En limpieza`), emisión de comprobante de pago y solicitud de reseña al huésped por WhatsApp.

#### 3.3 Gestión de Reservas Manuales (CU-08)
* Creación de reservas presenciales o telefónicas con opción de check-in inmediato (ejecuta el check-in automáticamente al crear).
* Modificación de fechas con revalidación de disponibilidad en tiempo real.
* Cancelación manual con aplicación de política de reembolso (RN-03) y registro del motivo.
* Independiente del canal de origen: una reserva hecha por chatbot o por la app web tiene la misma estructura en la base de datos.

#### 3.4 Centro de Conversaciones y Chatbot
* Panel de monitoreo de sesiones del chatbot de WhatsApp en tiempo real.
* Lista de chats escalados pendientes de atención humana.
* Opción de marcar la conversación como resuelta, lo que reactiva automáticamente el bot para el siguiente mensaje del huésped.

#### 3.5 Tienda e Inventario
* Alta y edición de productos (nombre, descripción, precio, stock, categoría, foto de factura).
* Registro de ventas directas y descuento automático de inventario.
* Cargo de consumos a habitación durante la estadía (liquidados en el check-out).
* Vista de rotación de productos: listado por cantidad vendida en un rango de fechas (HU-14).

#### 3.6 Finanzas y Reportes
* Registro de egresos/gastos operativos (HU-13).
* Consulta consolidada de ingresos (hospedaje + tienda) y egresos por período (CU-06).
* Exportación de informe mensual (HU-01).
* Cálculo automático de sueldo del recepcionista según el modelo definido por el administrador (HU-07).

#### 3.7 Reseñas (HU-10)
* Panel de reseñas para administrador y recepcionista: calificación promedio, listado filtrable por fecha o puntuación, detalle de comentarios.

#### 3.8 Administración de Usuarios y Auditoría (HU-05, HU-11, HU-15)
* Gestión de cuentas de administradores y recepcionistas (crear, editar, desactivar).
* Recuperación de contraseña (HU-11).
* Registro de auditoría: listado de acciones operativas (reserva, cancelación, check-in/out, venta, cambio de usuario) con fecha, hora, usuario y tipo de acción, filtrables por el administrador.
