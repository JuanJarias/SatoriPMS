# Reseñas y Fidelización de Huéspedes — SatoriPMS

## 1. Propósito del Módulo

El módulo de **Reseñas y Fidelización** tiene un doble objetivo comercial para **Torre Satori**:
1. Medir de forma continua la satisfacción de los viajeros que se hospedan en el hotel y potenciar el posicionamiento público del establecimiento en **Google Maps**.
2. Identificar automáticamente a los huéspedes frecuentes para brindarles un trato preferencial y ofrecerles beneficios o descuentos en sus próximas visitas a Sevilla.

---

## 2. Captura y Consulta de Reseñas por WhatsApp

### A. Consulta Pública de Opiniones (Opción 3 del Menú)
Cuando un viajero potencial desea conocer la experiencia de otros clientes antes de reservar:
- El asistente de WhatsApp consulta las valoraciones más recientes almacenadas en el sistema.
- Calcula y muestra la **calificación promedio del hotel sobre 5.0 estrellas** junto con los últimos comentarios verificados, indicando el nombre del huésped, la puntuación otorgada y el origen de la reseña.

### B. Registro de Nueva Reseña e Impulso en Google Maps (Opción 4 del Menú)
Tanto al finalizar la estadía como en cualquier momento desde el menú principal de WhatsApp:
1. **Calificación por estrellas:** El asistente invita al huésped a puntuar su experiencia del **1 al 5** (donde 1 es muy insatisfecho y 5 es excelente).
2. **Comentario abierto:** A continuación, le solicita escribir con sus propias palabras qué le pareció la atención, la comodidad de la habitación o las instalaciones de Torre Satori.
3. **Almacenamiento en el sistema:** La reseña queda registrada en la base de datos (`Tabla de reseñas : "review"`) con el nombre del autor (`Nombre del autor : "author_name"`), teléfono (`Teléfono de WhatsApp : "wa_id"`), calificación (`Estrellas : "rating"`), texto (`Comentario : "comment"`) y fecha.
4. **Enlace directo a Google Maps:** Inmediatamente después de guardar el comentario interno, el asistente agradece al huésped y le entrega un enlace directo a la ficha oficial de **Torre Satori en Google** (configurada mediante `Identificador de lugar en Google : "GOOGLE_PLACE_ID"`) para que, con un solo toque, pueda publicar también su reseña en Google Maps y ayudar a que más viajeros descubran el hotel.

---

## 3. Panel Administrativo de Moderación de Reseñas

En la aplicación web, el **Administrador** dispone de una vista dedicada para supervisar la reputación del hotel:
- Visualiza la evolución de la calificación promedio, la distribución de estrellas (de 1 a 5) y el listado cronológico de todos los comentarios recibidos.
- Identifica de forma temprana cualquier comentario con calificación baja (1 a 3 estrellas) para contactar al huésped, conocer qué ocurrió durante su turno de atención y aplicar mejoras operativas en el hotel.

---

## 4. Reconocimiento y Fidelización de Huéspedes Recurrentes

Dado que muchos visitantes viajan periódicamente a Sevilla por motivos familiares, laborales o turísticos, el sistema aprovecha el directorio unificado de clientes (`Directorio de huéspedes : "guest"`):

1. **Reconocimiento automático por número de WhatsApp:** Cada vez que un cliente se comunica por WhatsApp o se registra en recepción, el sistema identifica su perfil a través de su número telefónico (`Teléfono de WhatsApp : "whatsapp_phone"`) y su documento de identidad (`Documento de identidad : "document_number"`), asociando todas sus estadías históricas bajo una misma ficha.
2. **Clasificación de clientes frecuentes:** El sistema contabiliza cuántas estadías finalizadas (`Estado de la reserva : "finished"`) acumula cada huésped y cuál ha sido su inversión histórica en el hotel.
3. **Beneficios y campañas de fidelización:**
   - En el panel de recepción y administración se destaca con un distintivo de **Huésped Frecuente** a todo cliente que registra múltiples visitas previas, mostrando sus notas de preferencia (por ejemplo, si suele viajar con mascota o prefiere habitaciones de un piso específico).
   - El administrador puede consultar el listado de clientes recurrentes para otorgarles descuentos especiales, tarifas preferenciales en temporada baja o invitaciones directas durante eventos especiales del hotel.
