# Módulo — Chatbot de Reservas por WhatsApp

### 1. Principio Arquitectónico y de Diseño

n8n opera estrictamente como **orquestador conversacional, de entrada/salida y presentación**. Nunca calcula precios, no determina disponibilidad ni aplica reglas de negocio por su cuenta: todas las validaciones y mutaciones se delegan a los endpoints del Backend PMS (Spring Boot + PostgreSQL + Redis).

---

### 2. Menú Principal

El chatbot ofrece 6 opciones mediante listas y botones interactivos de WhatsApp:
1. **Hacer una reserva:** Flujo guiado tradicional paso a paso.
2. **Asistente IA:** Reserva asistida por lenguaje natural.
3. **Ver reseñas del hotel:** Consulta de opiniones históricas de huéspedes.
4. **Escribir una reseña:** Captura de calificaciones y comentarios post check-out.
5. **Hablar con un agente:** Escalamiento a la recepción humana.
6. **Revisar o Cancelar reserva:** Consulta de estado mediante código único y cancelación con políticas de reembolso.

**Palabras clave de reinicio universal:** En cualquier punto de la conversación, si el huésped escribe palabras como `"menú"`, `"menu"`, `"inicio"`, `"reiniciar"`, `"hola"`, `"start"` o `"cancelar"` (fuera de confirmaciones específicas), la sesión se reinicia inmediatamente al Menú Principal.

---

### 3. Especificación de Flujos Conversacionales

#### 3.1 Reserva Guiada Paso a Paso (CU-01)

* **Propósito:** Guiar al huésped de manera estructurada para cotizar, bloquear y reservar una o múltiples habitaciones.
* **Inputs requeridos por paso:**
  1. `checkIn`: Fecha de llegada (Formato `AAAA-MM-DD`). Validación: posterior o igual a la fecha actual.
  2. `checkOut`: Fecha de salida (Formato `AAAA-MM-DD`). Validación: posterior a `checkIn` y cumplimiento de estancia mínima/máxima (RN-06).
  3. `rooms`: Selección de una o varias habitaciones (ej: `"1"`, `"1, 2"`, `"1, 3"`).
  4. `huespedes`: Cantidad de adultos y niños. Acepta números y texto (ej. `"2 adultos y 1 niño"`, `"dos personas y un bebé"`).
  5. `guestName`: Nombre completo del titular (mínimo 3 caracteres).
  6. `guestDocument`: Documento de identidad (solo dígitos, 6 a 10 caracteres).
  7. `hasPet`: Viaja con mascota (`Sí` / `No`).
  8. `companions`: Nombres de los acompañantes separados por coma. **Condición estricta:** Si la reserva es para $N$ personas en total, se exige ingresar exactamente $N - 1$ nombres de acompañantes (o `"ninguno"` si solo viaja el titular).
  9. `confirmation`: Confirmación explícita del resumen (`Continuar` / `Cancelar`).
* **Reglas de Negocio asociadas:**
  * **RN-01 (Capacidad y cobro extra):** Si la suma de huéspedes supera la capacidad máxima total de las habitaciones seleccionadas, se rechaza. Si supera la capacidad base pero no la máxima, se calcula automáticamente el recargo por huésped adicional por noche.
  * **RN-02 (Bloqueo temporal):** Al elegir las habitaciones, se genera un bloqueo temporal en Redis por 15 minutos (900s). Al confirmarse la reserva, el bloqueo se libera en Redis y pasa a estar protegido permanentemente en PostgreSQL mediante la restricción `EXCLUDE`.
  * **RN-05 (Comprobante):** Toda reserva confirmada genera un código de grupo único (`reservationGroupId`) asociado a los registros de habitación.
* **Outputs del flujo:**
  * Mensaje de confirmación final con el código único de 8 caracteres (ej. `41560C98`), fechas, habitaciones y valor total.
  * Sesión reiniciada a `menu:esperando_opcion`.

---

#### 3.2 Reserva Asistida por IA (HU-09)

A diferencia de la reserva guiada paso a paso, aquí el huésped escribe en un solo mensaje toda la información de su reserva —fechas, número de adultos y niños, nombre de la persona a cargo, si tiene mascota, etc.— en sus propias palabras. El sistema:

1. Procesa el mensaje y le devuelve al huésped un resumen de lo que entendió, para que confirme si es correcto.
2. Si algo es incorrecto, el huésped indica qué corregir y el sistema ajusta el resumen.
3. Si falta información o algo no quedó claro, el sistema lo indica y pide que se aclare o se repita.
4. Solo cuando el huésped confirma que el resumen es correcto, el sistema muestra las habitaciones disponibles según esa información para que el huésped elija.
5. Una vez que el usuario elige las habitaciones, se bloquean por 15 minutos. La IA muestra un resumen final con precio y pregunta: "¿Proceder a pagar?", "Modificar la información", o "Terminar sin reservar".

La IA en este modo únicamente ayuda a interpretar el mensaje libre del huésped: **nunca confirma disponibilidad, precio ni reserva por sí sola** — solo puede llegar a completar una reserva si el huésped confirma explícitamente lo que la IA entendió.

Fuera de este modo dedicado, la misma interpretación asistida por IA también puede apoyar la reserva guiada paso a paso (2.3), únicamente para dar más libertad en el formato de las respuestas del huésped, sin exigir un formato estricto y sin tomar ninguna decisión de negocio por su cuenta.

Como en la reserva guiada, en cualquier momento se puede escalar a un recepcionista o volver al menú principal.

---

#### 3.3 Escalamiento a Recepcionista (HU-06)

* **Propósito:** Transferir la conversación a un agente humano cuando el usuario lo solicite explícitamente o cuando el bot no logre procesar la solicitud.
* **Condiciones y límites:**
  * Valida horario de atención de recepción (ej. 7:00 a.m. a 11:00 p.m.). Si está fuera de horario, informa y no escala.
  * Al escalar, establece `agent_active = true` en Redis, silenciando todas las respuestas automáticas del bot para ese número de WhatsApp.
* **Mecanismos de retorno al bot:**
  * El usuario escribe una palabra de reinicio (`"menú"`).
  * La recepcionista marca la conversación como resuelta desde la aplicación web.
  * Inactividad de 10 minutos con aviso preventivo de 1 minuto antes del cierre.

---

#### 3.4 Consulta y Cancelación de Reserva (CU-02)

* **Propósito:** Permitir al huésped consultar el estado completo de su reserva mediante su código identificador y cancelarla voluntariamente bajo las políticas del hotel.
* **Inputs:**
  * `code`: Código alfanumérico de la reserva (primeros 8 caracteres del `reservationGroupId`, ej. `41560C98`, o el UUID completo).
* **Fase 1: Consulta de Estado e Información:**
  * El sistema consulta `GET /api/bookings/group/{code}` y presenta:
    * Código de reserva.
    * Nombre del titular y documento.
    * Fechas de entrada y salida (número de noches).
    * Habitaciones reservadas (números y tipos).
    * Ocupación (adultos, niños, acompañantes, mascota).
    * Estado de la reserva (`Confirmada`, `Pendiente de pago` o `Cancelada`).
    * **Privacidad estricta:** No se muestra información interna operativa del hotel (ej. no se muestran estados de limpieza ni ocupación física de la habitación).
* **Fase 2: Presentación de Políticas y Estimación de Reembolso (RN-03):**
  * Si la reserva está activa, se ofrece la opción de cancelar. Al seleccionarla, se calculan las horas restantes hasta el check-in (15:00 del día de llegada):
    * **Más de 72 horas antes:** Reembolso del 100%.
    * **Entre 24 y 72 horas antes:** Reembolso del 50%.
    * **Menos de 24 horas antes o no-show:** Sin reembolso (0%).
  * Se informa al huésped la política exacta aplicable y el valor estimado a devolver.
* **Fase 3: Doble Confirmación:**
  * Se solicita confirmación explícita: `Sí, confirmar cancelación` o `No, mantener reserva`.
* **Fase 4: Ejecución de Cancelación:**
  * Endpoint: `POST /api/bookings/group/{code}/cancellation`.
  * **Efecto en datos:** La reserva **no se elimina** de la base de datos; su estado cambia a `cancelled`, preservando la trazabilidad histórica.
  * **Liberación de habitaciones:** Al pasar a `cancelled`, las fechas de las habitaciones quedan liberadas de inmediato para nuevas consultas y reservas.

---

#### 3.5 Módulo de Reseñas (HU-02, HU-04)

* **Consulta (HU-02):** Lista las calificaciones promedio y opiniones recientes de huéspedes anteriores. Disponible antes de reservar para que el huésped tome una decisión informada.
* **Captura (HU-04):** Tras el check-out, el sistema solicita al huésped —vía WhatsApp— una calificación numérica (1 a 5 estrellas) y un comentario libre. Solo puede dejarse una reseña por reserva finalizada.

---

### 4. Convención de Nombres de los Flujos

Cada versión del flujo de n8n se nombra con el patrón `V<versión>_ChatbotReservas.json` (por ejemplo `V6_ChatbotReservas.json`), para mantener un inventario claro de versiones y facilitar la comparación entre ellas. La versión activa actualmente es **V6**.

