package com.satoripms.api.review;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;

/**
 * Repositorio Spring Data JPA para la entidad Review (reseñas y opiniones).
 */
public interface ReviewRepository extends JpaRepository<Review, Long> {

    /**
     * Obtiene las 10 reseñas más recientes ordenadas por fecha de creación descendente.
     *
     * @return Lista de las últimas 10 reseñas
     */
    List<Review> findTop10ByOrderByCreatedAtDesc();

    /**
     * Busca una reseña vinculada a un identificador de reserva específico.
     *
     * @param bookingId Identificador de la reserva
     * @return Reseña encontrada envuelta en Optional
     */
    Optional<Review> findByBookingId(Long bookingId);

    /**
     * Determina si ya existe una reseña registrada para una reserva dada.
     *
     * @param bookingId Identificador de la reserva
     * @return true si ya existe una opinión para esa reserva, false de lo contrario
     */
    boolean existsByBookingId(Long bookingId);
}
