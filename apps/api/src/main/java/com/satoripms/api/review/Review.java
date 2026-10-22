package com.satoripms.api.review;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * Entidad JPA que representa una reseña u opinión sobre el servicio del hotel.
 * Almacena la calificación (1-5 estrellas), el comentario del huésped y el canal de procedencia.
 */
@Entity
@Table(name = "review")
@Data
public class Review {
    /** Identificador primario de la reseña */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Identificador del huésped asociado (opcional) */
    @Column(name = "guest_id")
    private Long guestId;

    /** Identificador de la habitación evaluada (opcional) */
    @Column(name = "room_id")
    private Long roomId;

    /** Identificador de la reserva evaluada (opcional, previene duplicados) */
    @Column(name = "booking_id")
    private Long bookingId;

    /** Calificación de 1 a 5 estrellas */
    @Column(nullable = false)
    private Integer rating;

    /** Comentario u opinión escrita del huésped */
    @Column
    private String comment;

    /** Nombre del autor para visualización pública */
    @Column(name = "author_name")
    private String authorName;

    /** Canal de origen de la reseña: 'chatbot', 'google', 'web' */
    @Column(name = "source", nullable = false)
    private String source;

    /** Fecha y hora de creación del registro */
    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;
}
