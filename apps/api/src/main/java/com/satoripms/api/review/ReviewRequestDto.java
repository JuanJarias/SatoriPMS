package com.satoripms.api.review;

import lombok.Data;

/**
 * DTO para la creación y recepción de reseñas desde el chatbot o canales web.
 */
@Data
public class ReviewRequestDto {
    /** Número de WhatsApp del huésped */
    private String waId;
    /** Comentario u opinión escrita */
    private String comment;
    /** Calificación de 1 a 5 estrellas */
    private Integer rating;
    /** Identificador opcional de la reserva asociada */
    private Long bookingId;
    /** Nombre del autor */
    private String authorName;
    /** Canal de origen de la reseña: "chatbot", "google", "web" */
    private String source;
}
