# Módulo — Chatbot de Reservas por WhatsApp

## 1. Principio Arquitectónico

n8n opera estrictamente como **orquestador conversacional, de entrada y salida, y de presentación**. Nunca calcula precios, no determina disponibilidad ni aplica reglas de negocio por su cuenta: todas las validaciones y mutaciones se delegan a los endpoints del Backend PMS (Spring Boot, PostgreSQL y Redis). El chatbot guía al huésped, pero no toma decisiones críticas: la disponibilidad, el precio, la capacidad, el estado de la reserva y los reembolsos siempre se validan en el backend.

Cada versión del flujo de n8n se nombra con el patrón `V<versión>_ChatbotReservas.json`, por ejemplo `V8_ChatbotReservas.json`. El flujo se organiza en una cadena común de recepción, carga de sesión y enrutamiento, seguida de ramas por funcionalidad que convergen en un único nodo de preparación de salida, responsable de guardar la sesión y enviar el mensaje por WhatsApp.

## 2. Rol de la Inteligencia Artificial

El chatbot usa Google Gemini Flash Lite con un rol distinto según el flujo. En todos los casos la IA no valida ni muta datos de negocio: devuelve una interpretación y el backend decide.

| Flujo | Rol de la IA |
|---|---|
| Menú principal | Sin IA. La selección se hace por lista interactiva o número. |
| Reserva guiada | Solo interpreta los mensajes del huésped. No redacta ni envía mensajes. |
| Reserva asistida por IA | Controla la conversación completa: lee, interpreta y responde. |
| Revisar o cancelar reserva | Solo interpreta los mensajes (por ejemplo, el código escrito de distintas formas o una confirmación dicha con otras palabras). |
| Escalamiento a recepcionista | Completamente desactivada mientras dure el escalamiento. |
| Reseñas | Sin IA. |

**Interpretación en la reserva guiada y en la cancelación.** En cada paso, el texto del huésped se envía a Gemini junto con el paso actual y los datos ya capturados. La IA responde con JSON estricto que contiene el valor extraído y normalizado (por ejemplo, una fecha dicha como "el 10 de noviembre" se convierte a `AAAA-MM-DD`, o "dos personas y un bebé" se convierte a adultos y niños) y la intención detectada. Las intenciones posibles son responder el paso actual, modificar un dato capturado antes, reiniciar, cancelar el flujo, solicitar un agente o mensaje no reconocido. n8n valida el valor con las reglas del paso y, si es correcto, continúa con los mensajes fijos del flujo. Esto permite aceptar formatos flexibles sin que el flujo se corte por un error de escritura.

**Modificación de datos.** Si la IA detecta que el huésped quiere corregir un dato anterior, el flujo regresa al paso correspondiente conservando el resto de lo capturado. Cambiar las fechas o las habitaciones libera los bloqueos vigentes y repite la consulta de disponibilidad. Cambiar la cantidad de huéspedes revalida la capacidad con RN-01. Cambiar el nombre, el documento, la mascota, los acompañantes o la modalidad de pago no afecta los bloqueos.

**Falla de la IA.** Si Gemini no responde, devuelve un JSON inválido o una intención no reconocida, el flujo recurre a la validación determinista del paso con el formato estricto y repite la pregunta con un ejemplo. La conversación nunca se interrumpe por una falla de la IA.

## 3. Recepción de Mensajes

El webhook de WhatsApp expone dos rutas sobre el mismo `path`. La ruta GET atiende la verificación de Meta: valida el `hub.verify_token` contra `WHATSAPP_VERIFY_TOKEN` y responde con el `hub.challenge`. La ruta POST recibe los eventos de mensajes: valida la firma `X-Hub-Signature-256` con el App Secret de Meta, responde 200 de inmediato y procesa el evento de forma desacoplada.

Cada evento se parsea para extraer el identificador de WhatsApp del huésped (`wa_id`), el nombre del remitente, el tipo de mensaje y el contenido. Solo se procesan mensajes de tipo texto, respuestas interactivas (botones y listas) y botones. Los eventos que no son mensajes, como las notificaciones de estado de entrega, se descartan sin respuesta. Si el mensaje es de otro tipo (imagen, audio, ubicación, documento), el bot responde que solo procesa mensajes de texto y mantiene el estado de la conversación. Cada `message_id` se registra para ignorar los reintentos de entrega que Meta pueda enviar del mismo evento.

## 4. Sesión y Máquina de Estados

### 4.1 Sesión

La sesión de cada huésped se guarda en Redis bajo la clave `session:{waId}`, se renueva en cada mensaje saliente y expira tras un período de inactividad. Si la sesión no existe, se trata como una conversación nueva y se muestra el menú principal.

| Campo | Contenido |
|---|---|
| `state` | Estado general del flujo en curso, por ejemplo `menu`, `reserva` o `escalamiento`, y los estados propios de los flujos de IA, consulta de reserva y reseñas |
| `step` | Paso dentro del estado actual; se combina con `state` para formar la ruta (`state:step`) |
| `agent_active` | Indicador de que un agente humano atiende la conversación; silencia al bot |
| `wa_id` y `sender_name` | Identificación del huésped en WhatsApp |
| `reservation_draft` | Borrador de la reserva en curso: fechas, huéspedes, mascota, habitaciones disponibles y elegidas, recargo por huéspedes extra, titular, documento, acompañantes, noches, total, tokens de bloqueo con su vigencia y modalidad de pago |
| `last_activity` | Marca de tiempo del último mensaje procesado |

### 4.2 Orden de Enrutamiento

Cada mensaje se enruta evaluando estas reglas en orden.

1. Si el mensaje no es de un tipo soportado, se responde que solo se procesa texto.
2. Si `agent_active` es verdadero, el bot permanece en silencio, salvo que el mensaje sea exactamente una palabra de salida del escalamiento (ver sección 6.3).
3. Si el mensaje es una palabra de reinicio universal, la sesión vuelve al menú principal.
4. Si el mensaje solicita un agente, el flujo pasa al escalamiento.
5. En cualquier otro caso, el mensaje se enruta según `state` y `step` al paso correspondiente de su flujo.

### 4.3 Palabras de Reinicio Universal

En cualquier punto de la conversación, si el mensaje consiste únicamente en `menú`, `menu`, `inicio`, `reiniciar`, `hola`, `start` o `cancelar`, la sesión se reinicia al menú principal y se liberan los bloqueos de habitación que tuviera vigentes. La palabra `cancelar` no reinicia cuando el paso actual es una confirmación específica, donde significa rechazar la acción. La coincidencia se hace sobre el mensaje completo, ignorando mayúsculas, tildes y signos de puntuación, de modo que una frase que solo contiene esas palabras entre otras no reinicia la sesión.

Las palabras `agente`, `recepcionista` y `humano` dentro de un mensaje solicitan el escalamiento, excepto cuando el huésped está escribiendo el comentario de una reseña.

## 5. Menú Principal

El menú se presenta como una lista interactiva de WhatsApp con seis opciones. Cada vez que se muestra, el borrador de reserva se reinicia.

1. **Hacer una reserva.** Flujo guiado paso a paso, con opción de abono del 50 % o pago total.
2. **Asistente IA.** Reserva asistida por lenguaje natural con Gemini.
3. **Ver reseñas del hotel.** Opiniones históricas de huéspedes desde la base de datos.
4. **Escribir una reseña.** Captura de calificación y comentario, con redirección a Google Reviews.
5. **Hablar con un agente.** Escalamiento a la recepción humana, con silenciamiento del bot.
6. **Revisar o cancelar reserva.** Consulta del estado mediante el código único, pago del saldo pendiente y cancelación con política de reembolso.

Si el huésped responde algo distinto a una opción válida, el bot pide un número del 1 al 6 y vuelve a mostrar el menú.

## 6. Especificación de Flujos

### 6.1 Reserva Guiada Paso a Paso (CU-01)

**Propósito.** Guiar al huésped de forma estructurada para cotizar, bloquear y reservar una o varias habitaciones, con opción de abonar el 50 % o liquidar el 100 %.

**Inputs por paso y validaciones.**

| Paso | Dato | Validación |
|---|---|---|
| 1 | `checkIn` | Fecha de llegada en formato `AAAA-MM-DD` (el huésped puede escribirla de otras formas, que se normalizan). Posterior o igual a la fecha actual en hora de Bogotá. |
| 2 | `checkOut` | Fecha de salida posterior a `checkIn` y que cumpla la estancia mínima y máxima de noches (RN-06). |
| 3 | `rooms` | Una o varias habitaciones de la lista presentada, por ejemplo `1`, `1, 2` o `1, 3`. |
| 4 | Huéspedes | Cantidad de adultos y niños, en números o texto, por ejemplo "2 adultos y 1 niño". Al menos 1 adulto. La suma se valida con RN-01. |
| 5 | `guestName` | Nombre completo del titular, mínimo 3 caracteres. Antes de pedirlo se muestra el aviso de privacidad de datos personales con la finalidad del tratamiento. |
| 6 | `guestDocument` | Documento de identidad, solo dígitos, de 6 a 10 caracteres. |
| 7 | `hasPet` | Si viaja con mascota, mediante botones Sí y No. Si es Sí y alguna habitación elegida no admite mascotas, se rechaza y se pide cambiar de habitación o responder No. |
| 8 | `companions` | Nombres de los acompañantes separados por coma. Si la reserva es para N personas en total, se exigen exactamente N - 1 nombres, o la palabra `ninguno` si solo viaja el titular. |
| 9 | `paymentOption` | `1` para pago total del 100 %, `2` para anticipo del 50 %. |
| 10 | Confirmación | Confirmación explícita del resumen con los botones Continuar y Cancelar. |

**Desarrollo del flujo.** Al elegir la opción 1 del menú, el bot pide la fecha de llegada y luego la de salida. Con ambas fechas válidas, consulta `GET /api/rooms/availability` y presenta las habitaciones libres como una lista interactiva con capacidad y precio por noche. Si no hay habitaciones disponibles, informa que no hay disponibilidad para esas fechas y regresa al menú. Cuando el huésped elige una o varias habitaciones, el bot llama a `POST /api/bookings/lock` y las bloquea por 15 minutos (RN-02). Si alguna ya no está disponible, informa y repite la consulta de disponibilidad.

Con el bloqueo vigente, el bot pide los huéspedes. Si la suma de adultos y niños supera la capacidad máxima total de las habitaciones elegidas, se rechaza e invita a ajustar la cantidad o elegir otras habitaciones. Si supera la capacidad base pero no la máxima, se calcula el recargo por huésped adicional por noche (RN-01) y se informa antes de continuar. Luego se piden titular, documento, mascota y acompañantes, y por último la modalidad de pago.

El resumen final muestra fechas, noches, habitaciones, ocupación, titular, acompañantes, mascota, total, monto a pagar ahora y saldo pendiente. Si el huésped elige Continuar, el bot llama a `POST /api/bookings/confirm` con el `lockToken` de cada habitación y la `paymentOption`. Si elige Cancelar, el bot libera los bloqueos y vuelve al menú. Si el bloqueo venció antes de confirmar, el backend rechaza la operación, el bot informa que el tiempo se agotó y ofrece repetir la búsqueda con las mismas fechas.

**Reglas de negocio asociadas.**

- **RN-01 (capacidad y cobro extra).** Se valida contra el tope combinado de adultos y niños, y se cobra el excedente sobre la capacidad base.
- **RN-02 (bloqueo temporal).** Al elegir las habitaciones se genera un bloqueo en Redis por 15 minutos. Al confirmarse la reserva, el bloqueo se libera y la protección pasa a la restricción `EXCLUDE` de PostgreSQL.
- **RN-05 (comprobante).** Toda reserva confirmada genera un código de grupo único (`reservationGroupId`) asociado a los registros de habitación, junto con total, monto pagado y saldo pendiente.
- **RN-06 (estancia).** Se respeta la duración mínima y máxima de noches.

**Outputs.** Un mensaje de confirmación con el código único de 8 caracteres (por ejemplo `B457F45D`), fechas, habitaciones, total, monto abonado y saldo pendiente. El mensaje indica de forma explícita que el huésped debe guardar ese código, porque lo necesitará para consultar, pagar el saldo o cancelar su reserva. La sesión regresa a `menu:esperando_opcion`.

### 6.2 Reserva Asistida por IA (HU-09)

**Propósito.** Permitir que el huésped escriba libremente, en uno o varios mensajes, todos los datos de su viaje. En este flujo la IA asume el control completo de la conversación: lee los mensajes, extrae los datos, responde al huésped y lo conduce hasta la reserva. Los cambios de estado de negocio (bloqueo, confirmación, cancelación del bloqueo) siguen ocurriendo solo mediante llamadas al backend y únicamente tras una decisión explícita del huésped.

**Flujo.**

1. **Mensaje libre.** El huésped escribe, por ejemplo: "Quiero reservar del 2026-11-10 al 2026-11-12 para 2 adultos sin mascotas. Soy Carlos Alberto Mendoza, cédula 987654321". Gemini extrae un JSON estricto con `checkIn`, `checkOut`, `adults`, `children`, `hasPet`, `guestName`, `guestDocument`, `companions` y un resumen.
2. **Datos faltantes.** Si falta información o una fecha es inválida, la IA pide la aclaración de forma cordial, sin perder lo que ya entendió. Si se indican N personas, se exigen N - 1 acompañantes o la indicación de que viaja solo.
3. **Confirmación de lo entendido.** La IA presenta lo que entendió y pregunta si es correcto. Si el huésped corrige algo, se vuelve a extraer y a confirmar.
4. **Habitaciones y sugerencia.** Una vez confirmado, el backend consulta `GET /api/rooms/availability` con las fechas, los huéspedes y la mascota, de modo que solo se presentan habitaciones que cuadran con la descripción y están disponibles en ese momento. La IA muestra el listado con precio por noche y capacidad máxima, y sugiere cuál elegir con una breve justificación (`GET /api/rooms/recommend`).
5. **Selección y bloqueo.** El huésped elige la habitación o habitaciones de la misma forma que en el flujo guiado. El bot llama a `POST /api/bookings/lock` y las bloquea por 15 minutos o hasta que la conversación termine, lo que ocurra primero (RN-02).
6. **Resumen y decisión.** La IA envía el resumen completo de la reserva (fechas, habitaciones, huéspedes, titular, documento, acompañantes, mascota) con el precio total y pregunta qué desea hacer: proceder a pagar, modificar la información o terminar la conversación sin reservar.
7. **Resolución según la decisión.**
   - **Proceder a pagar.** El bot ofrece las modalidades de 100 % o 50 % de anticipo, llama a `POST /api/bookings/confirm` con `source = 'chatbot'`, libera el bloqueo de Redis y entrega el mensaje de confirmación con el código de la reserva.
   - **Modificar la información.** La IA pregunta qué desea cambiar, vuelve a extraer los datos y repite la validación. Si cambian las fechas o los huéspedes, se verifica de nuevo la disponibilidad y se ajustan los bloqueos antes de generar un nuevo resumen.
   - **Terminar sin reservar.** Se liberan todos los bloqueos, se agradece al huésped y la sesión vuelve al menú.

Si el huésped abandona el flujo o la conversación expira por inactividad, los bloqueos se liberan, verificando antes que el flujo realmente terminó.

### 6.3 Escalamiento a Recepcionista (HU-06)

**Propósito.** Transferir la conversación a un agente humano cuando el huésped lo solicita de forma explícita, ya sea eligiendo la opción 5 del menú o escribiendo palabras como `agente`, `recepcionista` o `humano`.

**Condiciones y límites.** El bot valida el horario de atención de la recepción, de 7:00 a. m. a 11:00 p. m. en hora de Bogotá. Fuera de ese horario informa el horario de atención, no escala y regresa al menú. Dentro del horario, el flujo hace lo siguiente.

1. Establece `agent_active = true` en la sesión de Redis, con lo que el bot queda en silencio para ese número de WhatsApp.
2. Desactiva por completo la interpretación con IA para esa conversación.
3. Notifica a la recepción con `POST /api/conversations/{id}/escalation`, de modo que la conversación aparezca como escalada en el centro de conversaciones de la aplicación web.
4. Informa al huésped que un agente lo atenderá en breve.

**Atención humana.** La recepcionista habla con el huésped por el mismo número de WhatsApp del hotel, de dos formas posibles: desde el centro de conversaciones de la aplicación web, donde el backend envía sus mensajes por la Cloud API, o desde la aplicación WhatsApp Business. Durante el escalamiento, los mensajes del huésped no reciben respuesta automática y los mensajes que envía la propia recepción nunca se procesan como mensajes de huésped.

**Mecanismos de retorno al bot.** El bot vuelve a funcionar por cualquiera de estas tres vías.

- La recepcionista marca la conversación como resuelta desde la aplicación web.
- La conversación termina por inactividad.
- El huésped escribe exclusivamente una palabra de salida: `menú`, `menu` o `inicio`. El mensaje debe contener solo esa palabra; frases como "el menú", "como el menú" o "quiero ir al menú" no tienen efecto y el bot sigue en silencio.

En cualquiera de los tres casos se establece `agent_active = false`, se reactiva la IA y el siguiente mensaje del huésped se atiende desde el menú principal.

### 6.4 Consulta, Pago de Saldo y Cancelación de Reserva (CU-02)

**Propósito.** Permitir al huésped consultar el estado completo de su reserva mediante el código que recibió al reservar, pagar el saldo pendiente y cancelarla voluntariamente bajo las políticas del hotel. La opción del menú pide explícitamente el código de la reserva. La IA solo interpreta los mensajes, por ejemplo extrayendo el código de un texto con espacios, minúsculas o palabras adicionales, o entendiendo una confirmación escrita con otras palabras.

**Input.** `code`: código alfanumérico de la reserva, formado por los primeros 8 caracteres del `reservationGroupId` (por ejemplo `B457F45D`), o el UUID completo.

**Fase 1: consulta.** El flujo llama a `GET /api/bookings/group/{code}`. Si el código no existe, informa que no se encontró la reserva y permite escribirlo de nuevo o volver al menú. Si existe, presenta la información de la reserva, sin incluir ningún dato sobre el estado operativo de la habitación:

- Código de reserva y nombre del titular.
- Estado de la reserva, `Confirmada` (la reserva está vigente y en orden) o `Cancelada`, y estado de pago (`paid`, `partial` o `pending`).
- Fechas de entrada y salida, número de noches y habitaciones reservadas.
- Ocupación: adultos, niños, acompañantes y mascota.
- Total de la reserva, monto pagado a la fecha y saldo pendiente.

**Fase 2: acciones disponibles.** Dependen de `canPayRemaining` y `canCancel`.

| Situación | Opciones |
|---|---|
| Con saldo pendiente | 1. Pagar saldo restante, 2. Cancelar reserva, 3. Volver al menú |
| Pagada al 100 % | 1. Cancelar reserva, 2. Volver al menú |
| Ya cancelada | Solo volver al menú |

Al pagar el saldo restante, el flujo llama a `POST /api/bookings/group/{code}/pay-remaining`, la reserva queda `paid` y el saldo pendiente en $0,00.

**Fase 3: política y estimación de reembolso (RN-03).** Al elegir cancelar, el bot muestra las políticas del hotel y calcula el reembolso estimado sobre el monto efectivamente pagado (`paid_amount`), según las horas restantes hasta el check-in a las 15:00 del día de llegada: más de 72 horas, 100 % de lo abonado; entre 24 y 72 horas, 50 %; menos de 24 horas o no-show, 0 %.

**Fase 4: doble confirmación.** El bot pide una confirmación explícita con los botones `Sí, confirmar` y `No`, mostrando de nuevo el código, las fechas y el monto del reembolso. Cualquier respuesta distinta a la confirmación afirmativa se trata como rechazo.

**Fase 5: ejecución.** El flujo llama a `POST /api/bookings/group/{code}/cancellation`. La reserva cambia a `cancelled` y se conserva como historial; `payment_status` cambia a `refunded` cuando hay devolución y se mantiene cuando el reembolso es 0 %. Las habitaciones quedan liberadas de inmediato. El bot informa el resultado con el porcentaje y el monto de reembolso calculados según la política.

### 6.5 Módulo de Reseñas (HU-02 y HU-04)

**Consulta de reseñas (HU-02, opción 3).** El flujo llama a `GET /api/reviews?limit=5` y presenta la calificación promedio en estrellas, el número de opiniones registradas y los últimos comentarios de los huéspedes, tanto de Google Reviews como del chatbot.

**Captura de reseña y redirección a Google (HU-04, opción 4).**

1. **Calificación.** El bot solicita una calificación de 1 a 5 estrellas y admite dígitos, palabras o emojis de estrellas. Cualquier valor fuera de ese rango se rechaza con un mensaje que indica el formato esperado.
2. **Comentario.** Solicita un comentario libre sobre la experiencia y el servicio. En este paso las palabras de escalamiento no se interpretan como solicitud de agente.
3. **Persistencia local.** Guarda la reseña en la tabla `review` mediante `POST /api/reviews` con `source = 'chatbot'`, asociándola al `guest_id` si el número de WhatsApp está registrado.
4. **Redirección a Google.** Agradece el comentario y entrega el enlace directo para publicar la reseña en el perfil de Google Business y Google Maps del hotel: `https://search.google.com/local/writereview?placeid=${GOOGLE_PLACE_ID}`. Google no permite crear reseñas de forma programática sin la autenticación del usuario final; este enlace es la vía estándar para que el huésped verifique y publique su reseña con un solo clic.

## 7. Contratos con el Backend

| Flujo | Endpoints que consume |
|---|---|
| Reserva guiada | `GET /api/rooms/availability`, `POST /api/bookings/lock`, `POST /api/bookings/confirm` |
| Reserva asistida por IA | `GET /api/rooms/availability`, `GET /api/rooms/recommend`, `POST /api/bookings/lock`, `POST /api/bookings/confirm` |
| Revisar o cancelar | `GET /api/bookings/group/{code}`, `POST /api/bookings/group/{code}/pay-remaining`, `POST /api/bookings/group/{code}/cancellation` |
| Reseñas | `GET /api/reviews`, `POST /api/reviews` |
| Escalamiento | `POST /api/conversations/{id}/escalation` |

El backend se invoca con la variable de entorno `API_BASE_URL` y un tiempo de espera fijo por llamada. Si una llamada falla, el bot informa que no pudo completar la operación, conserva el estado de la sesión y ofrece reintentar o volver al menú.

## 8. Convenciones de Presentación

Los mensajes usan listas interactivas para menús y selección de habitaciones, con máximo 10 filas y títulos de fila de hasta 24 caracteres, y botones de respuesta rápida para decisiones de dos o tres opciones. Todo texto dirigido al huésped está en español. Todo paso de captura de datos explica el formato esperado con un ejemplo cuando el dato no se reconoce, y recuerda siempre que se puede reiniciar escribiendo "menú".
