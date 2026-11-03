# Módulo — Reseñas y Fidelización

## 1. Requerimientos y Casos de Uso

**HU-02, Consultar reseñas.** Los huéspedes y futuros clientes ven los comentarios de huéspedes anteriores desde el chatbot (opción 3 del menú) y desde la web pública, con la calificación promedio en estrellas y las opiniones reales persistidas en PostgreSQL.

**HU-04, Dejar reseña.** Formulario conversacional vía WhatsApp (opción 4 del menú) o por la web tras el check-out. Captura una calificación numérica de 1 a 5 estrellas y un comentario libre. No se permite duplicar la reseña de una misma estadía.

**Redirección a Google Reviews.** Tras guardar la reseña local con `source = 'chatbot'`, el chatbot entrega el enlace directo al perfil de Google Business del hotel (`https://search.google.com/local/writereview?placeid=${GOOGLE_PLACE_ID}`) e invita al huésped a publicarla en Google Maps. Google no permite crear reseñas de forma programática sin la autenticación del usuario final, por lo que esta redirección es la vía oficial.

**HU-10, Panel de reseñas.** Vista para el administrador y la recepcionista que muestra las opiniones recibidas, su calificación y su fuente (`chatbot`, `google` o `web`).

**HU-12, Huéspedes recurrentes.** Identificación automática de los clientes que superan el umbral de estadías definido por el administrador, para aplicar beneficios de fidelización.

## 2. Flujo de Reseña

Después del check-out, el sistema envía al huésped por WhatsApp una invitación a calificar su estadía. El huésped también puede iniciar el flujo en cualquier momento desde la opción 4 del menú. El bot pide la calificación, luego el comentario, guarda la reseña en PostgreSQL con `POST /api/reviews` y entrega el enlace para que el huésped la publique también en Google. Si el número de WhatsApp pertenece a un huésped registrado, la reseña queda asociada a su `guest_id` y, cuando se conoce, a la reserva de origen.

## 3. Reglas de Integridad y Persistencia

**Persistencia real.** La entidad JPA `Review` y el repositorio `ReviewRepository` se conectan a la tabla `review` de PostgreSQL. Las reseñas se listan ordenadas por fecha de creación descendente.

**Unicidad por reserva.** Si la reseña proviene de una reserva conocida (`bookingId`), se valida que no exista ya otra reseña asociada a ella (`existsByBookingId`), evitando duplicados.

**Calificación válida.** El valor de `rating` debe estar entre 1 y 5.

**Fuentes admitidas.** La columna `source` acepta `chatbot`, `google` y `web`. Las reseñas importadas de Google no requieren huésped, habitación ni reserva asociados.

## 4. Fidelización

El sistema identifica a un huésped recurrente contando las estadías finalizadas asociadas a su registro. Cuando el conteo alcanza el umbral que define el administrador, el huésped queda marcado como recurrente y aparece en el panel de fidelización, filtrable por frecuencia de visitas. Los beneficios para huéspedes recurrentes, así como los descuentos para familiares y amigos del hotel, se aplican según las reglas definidas por el administrador.
