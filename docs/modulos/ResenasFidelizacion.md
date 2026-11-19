# Reseñas y Fidelización de Huéspedes — SatoriPMS

## 1. Propósito del Módulo

El módulo de **Reseñas y Fidelización** tiene un doble objetivo comercial para **Torre Satori**:
1. Medir de forma continua la satisfacción de los viajeros que se hospedan en el hotel y potenciar el posicionamiento público del establecimiento en **Google Maps**.
2. Identificar automáticamente a los huéspedes frecuentes para brindarles un trato preferencial y ofrecerles beneficios o descuentos en sus próximas visitas a Sevilla.

---

## 2. Gestión Unificada de Reseñas mediante Google Reviews (Opción 3 del Menú)

Para garantizar la máxima transparencia, autenticidad e imparcialidad, el chatbot de WhatsApp no almacena ni muestra reseñas en bases de datos internas privadas. Toda la reputación y valoración pública del hotel se canaliza directamente hacia el perfil oficial de **Torre Satori en Google Reviews**:

### A. Política de Transparencia e Imparcialidad Hotelera
- En el sector hotelero contemporáneo, los viajeros valoran la credibilidad de las plataformas públicas independientes frente a sistemas internos donde las opiniones podrían ser filtradas o sesgadas.
- Al centralizar las calificaciones en Google, cada opinión positiva contribuye directamente a elevar el posicionamiento orgánico del hotel en **Google Maps**, **Google Search** y **Google Travel**, atrayendo nuevos clientes de manera orgánica sin intermediación de OTAs de alta comisión.

### B. Flujo Unificado en WhatsApp (Opción 3: "Reseñas y opiniones")
Cuando un huésped selecciona la **Opción 3** del menú principal (o escribe palabras como *"reseñas"*, *"opiniones"*, *"calificar"* o *"Google"*):
1. **Mensaje de bienvenida formal:** El asistente saluda cordialmente explicando que todas las valoraciones son gestionadas de forma abierta en Google Reviews para certificar su autenticidad.
2. **Entrega de enlace canónico directo:** Provee el enlace oficial permanente al perfil de Torre Satori en Google Travel / Google Reviews ([https://www.google.com/travel/hotels/entity/CgsIvsf-mZ_-h-fGARAB/reviews](https://www.google.com/travel/hotels/entity/CgsIvsf-mZ_-h-fGARAB/reviews)), con previsualización enriquecida (`preview_url: true`), permitiendo:
   - Consultar las experiencias, fotos y calificaciones dejadas por otros viajeros.
   - Publicar su propia calificación de 1 a 5 estrellas y reseña escrita directamente con su cuenta de Google en un solo toque.
3. **Navegación inmediata:** La sesión permanece en el menú principal (`state: 'menu'`), permitiendo al usuario continuar consultando tarifas, reservando o hablando con un agente sin tener que completar formularios interactivos en el chat.
4. **Configuración dinámica:** La URL de destino está respaldada por la variable de entorno `GOOGLE_REVIEWS_URL`, permitiendo actualizarla si el hotel adopta un enlace corto corporativo (por ejemplo: `https://torresatori.com/resenas`).

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
