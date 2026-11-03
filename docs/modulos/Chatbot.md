# Chatbot y Atención Automatizada por WhatsApp — SatoriPMS

## 1. Propósito del Módulo

El módulo de **Chatbot por WhatsApp** es el canal principal de atención directa y ventas las 24 horas del día para **Torre Satori**. Permite que cualquier viajero consulte disponibilidad, reciba orientación en lenguaje natural mediante inteligencia artificial, reserve una o varias habitaciones con protección contra sobreventa, pague el 100% o el 50% de anticipo, consulte o liquide su saldo pendiente, cancele su reserva bajo las políticas del hotel, consulte o escriba reseñas y solicite hablar con una persona de recepción en cualquier momento.

---

## 2. Reglas Generales de Conversación y Experiencia del Usuario

### A. Palabras Clave Globales (Reinicio y Atención Humana)
Sin importar en qué paso se encuentre el usuario, el asistente reconoce comandos inmediatos:
- **Volver al inicio:** Si el huésped escribe *"hola"*, *"menú"*, *"inicio"* o *"reiniciar"*, el asistente cancela el borrador actual, **libera de inmediato cualquier habitación que estuviera bloqueada temporalmente** para ese usuario y presenta de nuevo el menú principal.
- **Hablar con una persona:** Si el huésped escribe *"agente"*, *"recepcionista"* o *"humano"* (salvo cuando está redactando el texto libre de una reseña), el asistente detiene las respuestas automáticas y transfiere la conversación al personal de recepción.

### B. Manejo de Mensajes Multimedia
Si el viajero envía una nota de voz, imagen, video, documento o sticker cuando el asistente espera una respuesta de texto, el bot le informa amablemente que por ese canal procesa únicamente mensajes escritos o selecciones del menú interactivo, conservando el paso exacto en el que se encontraba la conversación para que el usuario no tenga que empezar de nuevo.

### C. Control de Inactividad y Liberación Automática de Bloqueos
- Cada interacción del huésped actualiza su sesión activa en memoria rápida (`Sesión de usuario : "session:{waId}"`).
- Si transcurren **10 minutos** sin que el usuario responda, el asistente envía un único aviso preguntando si desea continuar con su solicitud.
- Si se cumple **1 minuto adicional** sin respuesta (11 minutos en total), el sistema cierra la sesión, limpia los datos temporales y **libera inmediatamente los bloqueos de habitaciones asociados**, dejándolas disponibles para otros viajeros.

### D. Aviso de Privacidad y Protección de Datos (Ley 1581 de 2012)
Antes de solicitar el nombre completo y el número de documento de identidad del titular de la reserva —tanto en el flujo guiado paso a paso como en el asistente con inteligencia artificial—, el chatbot presenta el aviso de privacidad informando que el suministro de los datos personales autoriza a Torre Satori para su tratamiento con la única finalidad de gestionar la reserva y la estadía.

---

## 3. Menú Principal de Atención

Al iniciar la conversación, el asistente saluda al huésped por su nombre de perfil de WhatsApp y despliega una lista interactiva con seis opciones numeradas:

| Opción | Identificador de Opción | Título en el Menú | Descripción Funcional |
|---|---|---|---|
| **1** | `Opción de reserva guiada : "menu_reserva"` | **Hacer una reserva** | Guía al viajero paso a paso para elegir fechas, habitaciones, huéspedes y modalidad de pago. |
| **2** | `Opción de asistente con IA : "menu_ia"` | **Asistente IA** | Permite describir el viaje libremente en un solo mensaje para que la inteligencia artificial extraiga los datos y busque disponibilidad. |
| **3** | `Opción de ver reseñas : "menu_resenas"` | **Ver reseñas** | Muestra la calificación promedio del hotel y las opiniones más recientes de otros huéspedes. |
| **4** | `Opción de escribir reseña : "menu_escribir_resena"` | **Escribir reseña** | Permite calificar la estadía de 1 a 5 estrellas, dejar un comentario y obtener el enlace directo a Google Maps. |
| **5** | `Opción de revisar o cancelar : "menu_cancelar"` | **Revisar o Cancelar** | Permite consultar el estado de una reserva con su código, pagar el saldo pendiente o solicitar su cancelación. |
| **6** | `Opción de hablar con agente : "menu_agente"` | **Hablar con agente** | Silencia el asistente automático y transfiere la conversación al personal humano de recepción. |

El huésped puede seleccionar cualquiera de las seis opciones tocando el botón de la lista interactiva o escribiendo el número correspondiente (`1` al `6`).

---

## 4. Flujo 1: Reserva Guiada Paso a Paso (Opción 1)

Este flujo acompaña al viajero pregunta por pregunta, validando la información en cada etapa:

1. **Fecha de llegada:** Solicita la fecha de entrada (`Fecha de entrada : "checkIn"`). Acepta tanto fechas en formato estándar (`AAAA-MM-DD`) como expresiones naturales en español (por ejemplo, *"mañana"*, *"15 de diciembre de 2026"*). Verifica que no sea una fecha pasada.
2. **Fecha de salida:** Solicita la fecha de salida (`Fecha de salida : "checkOut"`), validando que sea posterior a la fecha de entrada.
3. **Consulta de habitaciones disponibles:** El asistente consulta en el servidor las habitaciones libres para ese rango de fechas y presenta un listado numerado con el nombre, número de habitación, tarifa base por noche y capacidad máxima. Si no hay disponibilidad en esas fechas, invita al huésped a elegir un nuevo rango.
4. **Selección y bloqueo temporal de 15 minutos:** El huésped indica el número (o números separados por coma, si desea reservar varias habitaciones para su grupo). El sistema bloquea inmediatamente las habitaciones seleccionadas por 15 minutos e informa al usuario que cuenta con ese tiempo garantizado para completar sus datos.
5. **Cantidad de adultos y niños:** El huésped indica cuántos adultos y niños se hospedarán (por ejemplo, *"2 adultos y 1 niño"*). El sistema verifica que el total de personas no supere la capacidad máxima de las habitaciones seleccionadas y calcula si aplica recargo por persona adicional sobre la capacidad base.
6. **Aviso de privacidad y nombre del titular:** Se presenta el aviso de tratamiento de datos personales (Ley 1581 de 2012) y se solicita el nombre completo del titular de la reserva.
7. **Documento de identidad:** Se solicita la cédula o documento de identificación del titular, validando que contenga únicamente números (entre 6 y 10 dígitos).
8. **Viaje con mascota:** El asistente pregunta mediante botones interactivos (*Sí* / *No*) si el huésped viaja con mascota. Si responde afirmativamente, verifica que la habitación seleccionada permita mascotas.
9. **Registro de acompañantes:** Si la reserva incluye más de una persona, solicita los nombres completos de los acompañantes separados por coma, verificando que la cantidad de nombres coincida con el número de acompañantes indicados. Si el titular viaja solo, acepta la respuesta *"ninguno"*.
10. **Resumen detallado y elección de pago:** El asistente presenta el resumen completo de la reserva, incluyendo:
    - Habitación o habitaciones seleccionadas.
    - Fechas de entrada y salida y número de noches.
    - Cantidad de adultos, niños y si viaja con mascota.
    - Nombre y documento del titular y lista de acompañantes.
    - **Tarifa base de las noches de estadía.**
    - **Recargo por persona adicional** (indicando cuántas personas adicionales aplican y su valor unitario, o *"Sin recargo"* cuando no supera la capacidad base).
    - **Valor total de la estadía.**
    A continuación, ofrece tres opciones de acción:
    - **Opción 1 — Pagar el 100% ahora:** Confirma la reserva como totalmente pagada.
    - **Opción 2 — Pagar el 50% de anticipo:** Confirma la reserva abonando la mitad y dejando el 50% restante pendiente para pagarlo antes o durante el ingreso al hotel.
    - **Opción 3 — Cancelar reserva:** Cancela el proceso y **libera de inmediato el bloqueo temporal de la habitación** para que vuelva a estar disponible.
11. **Confirmación y entrega del código único:** Al completarse el pago del 100% o del 50%, el sistema registra la reserva definitiva, libera el candado temporal y entrega al huésped su **código único de reserva** de 8 caracteres alfanuméricos junto con el desglose del monto abonado y el saldo pendiente.

---

## 5. Flujo 2: Asistente Inteligente en Lenguaje Natural (Opción 2)

Pensado para viajeros que prefieren escribir todos sus requerimientos en un solo mensaje conversacional:

1. **Mensaje de bienvenida y aviso de privacidad:** El asistente invita al usuario a describir su viaje libremente (fechas, cantidad de adultos y niños, si lleva mascota, nombre completo y documento de identidad) e incluye el aviso de privacidad de datos personales.
2. **Interpretación con Inteligencia Artificial:** El texto del huésped es analizado por el modelo de inteligencia artificial, que extrae de forma estructurada las fechas, huéspedes, mascota, nombre, documento y acompañantes. Si el usuario no indicó fechas válidas de entrada y salida, el asistente resume lo que entendió y le pide únicamente las fechas faltantes.
3. **Búsqueda y selección de habitación:** Con las fechas y la ocupación identificadas, el asistente consulta la disponibilidad real filtrando por capacidad y admisión de mascotas, y muestra las opciones disponibles para que el viajero elija con un número.
4. **Bloqueo temporal y resumen con desglose de recargos:** Al elegir la habitación, el sistema la bloquea por 15 minutos y muestra el resumen completo con el desglose de **tarifa base**, **recargo por persona adicional** y **total de la estadía**, ofreciendo las opciones de pagar el 100%, abonar el 50% o cancelar (liberando el bloqueo de inmediato).
5. **Confirmación:** Genera la reserva y entrega el código único de 8 caracteres con las mismas garantías que el flujo guiado.

---

## 6. Flujo 3: Consulta y Registro de Reseñas (Opciones 3 y 4)

### A. Ver Reseñas (Opción 3)
- El asistente consulta las calificaciones más recientes almacenadas en el sistema, calcula el promedio general de satisfacción sobre 5.0 estrellas y presenta hasta 5 comentarios reales indicando el nombre del autor, las estrellas otorgadas y el canal de origen.

### B. Escribir una Reseña y Enlace a Google Maps (Opción 4)
1. **Calificación numérica:** El asistente solicita al huésped calificar su experiencia del **1 al 5** (aceptando números, palabras como *"cinco"* o *"excelente"*, o emojis de estrellas).
2. **Comentario descriptivo:** Una vez recibida la puntuación, pide al huésped un breve comentario sobre su estadía, la atención o las instalaciones.
3. **Guardado y redirección a Google:** El sistema registra la reseña y responde agradeciendo al huésped junto con un enlace directo al perfil de **Torre Satori en Google Maps** para que pueda compartir también su opinión públicamente con un solo toque.

---

## 7. Flujo 4: Revisar Reserva, Pagar Saldo Pendiente o Cancelar (Opción 5)

Permite al huésped autogestionar su reserva activa en cualquier momento utilizando su código de 8 caracteres:

1. **Solicitud del código:** El asistente pide el código de reserva entregado al momento de la confirmación.
2. **Presentación del estado de la reserva:** Muestra el titular, estado actual, fechas, número de noches, habitaciones asignadas, ocupación, valor total, monto abonado a la fecha y saldo pendiente:
   - Si la reserva tiene **saldo pendiente** (porque se confirmó con anticipo del 50%), habilita tres opciones: **1. Pagar saldo restante**, **2. Cancelar reserva** y **3. Volver al menú**.
   - Si la reserva ya está **pagada al 100%**, habilita: **1. Cancelar reserva** y **2. Volver al menú**.
3. **Liquidación del saldo restante:** Si el huésped elige pagar el saldo pendiente, el sistema registra el pago del 50% restante, actualiza el estado de pago a completado (100%), deja el saldo pendiente en cero y envía el comprobante de actualización por WhatsApp.
4. **Cancelación con cálculo transparente sobre lo abonado:**
   - Si el huésped elige cancelar, el asistente no anula la reserva de inmediato: primero muestra las **Políticas de Cancelación de Torre Satori**, informa cuánto dinero ha abonado el huésped hasta la fecha, cuántas horas faltan para la hora de entrada (15:00 del día de llegada) y cuál es el **reembolso estimado exacto calculado sobre lo abonado** (100% si faltan más de 72 horas, 50% entre 24 y 72 horas, o 0% si faltan menos de 24 horas).
   - Solicita una **doble confirmación** (*"Sí, confirmar"* para anular definitivamente o *"No"* para conservar la reserva).
   - Al confirmarse, la reserva pasa a estado cancelado, las habitaciones quedan libres de inmediato para nuevas reservas y se informa el resumen final de la operación.

---

## 8. Flujo 5: Escalamiento a Recepción Humana (Opción 6)

Cuando el viajero selecciona la opción 6 del menú o escribe palabras como *"agente"* o *"recepcionista"*:
1. El sistema activa el indicador de atención humana en la sesión del usuario (`Atención por agente activa : "agent_active"`).
2. Envía una alerta al panel de recepción para que el personal del hotel atienda el chat desde el WhatsApp del establecimiento o desde la bandeja de conversaciones de la aplicación web.
3. Mientras el modo de agente humano está activo, el chatbot guarda silencio ante los nuevos mensajes del huésped para no interrumpir la conversación con el recepcionista, hasta que la atención concluya o el huésped escriba *"menú"* para reactivar el asistente automático.
