package com.satoripms.api.review;

import com.satoripms.api.booking.BookingRepository;
import com.satoripms.api.guest.GuestRepository;
import com.satoripms.api.guest.Guest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Controlador REST para el módulo de Reseñas y Fidelización de SatoriPMS.
 *
 * Expone endpoints para:
 * 1. Consultar las valoraciones y comentarios más recientes de huéspedes.
 * 2. Registrar nuevas opiniones recibidas a través del chatbot de WhatsApp o la aplicación web.
 */
@RestController
@RequestMapping("/api/reviews")
public class ReviewController {

    private final ReviewRepository reviewRepository;
    private final BookingRepository bookingRepository;
    private final GuestRepository guestRepository;

    /**
     * Constructor con inyección de repositorios requeridos.
     *
     * @param reviewRepository  Repositorio JPA de reseñas
     * @param bookingRepository Repositorio JPA de reservas
     * @param guestRepository   Repositorio JPA de huéspedes
     */
    public ReviewController(ReviewRepository reviewRepository,
                            BookingRepository bookingRepository,
                            GuestRepository guestRepository) {
        this.reviewRepository = reviewRepository;
        this.bookingRepository = bookingRepository;
        this.guestRepository = guestRepository;
    }

    /**
     * Consulta las reseñas más recientes ordenadas por fecha de creación descendente.
     *
     * @param limit Cantidad máxima de registros a retornar (por defecto 10)
     * @return Lista de reseñas recientes para mostrar al huésped o en el portal web
     */
    @GetMapping
    public ResponseEntity<?> getReviews(@RequestParam(defaultValue = "10") int limit) {
        List<Review> reviews = reviewRepository.findTop10ByOrderByCreatedAtDesc();
        return ResponseEntity.ok(reviews.stream().limit(limit).toList());
    }

    /**
     * Registra una nueva reseña de servicio.
     * Soporta registro automático desde el chatbot (asociando el número de WhatsApp, huésped y reserva)
     * o registro manual desde interfaces externas.
     *
     * @param request Datos de la calificación (1-5 estrellas), comentario y origen
     * @return Respuesta con el identificador asignado y confirmación del registro
     */
    @PostMapping
    public ResponseEntity<?> createReview(@RequestBody ReviewRequestDto request) {
        if (request.getRating() == null || request.getRating() < 1 || request.getRating() > 5) {
            return ResponseEntity.badRequest().body(Map.of("error", "La calificación debe ser entre 1 y 5"));
        }
        if (request.getComment() == null || request.getComment().isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("error", "El comentario es requerido"));
        }

        Review review = new Review();
        review.setRating(request.getRating());
        review.setComment(request.getComment());
        review.setSource("chatbot");

        if (request.getWaId() != null && !request.getWaId().isBlank()) {
            Optional<Guest> guestOpt = guestRepository.findByWhatsappPhone(request.getWaId());
            guestOpt.ifPresent(g -> review.setGuestId(g.getId()));
            review.setAuthorName(guestOpt.map(Guest::getName).orElse(null));

            if (request.getBookingId() != null) {
                if (reviewRepository.existsByBookingId(request.getBookingId())) {
                    return ResponseEntity.status(HttpStatus.CONFLICT)
                        .body(Map.of("error", "Ya existe una reseña para esa reserva"));
                }
                review.setBookingId(request.getBookingId());
                bookingRepository.findById(request.getBookingId())
                    .ifPresent(b -> review.setRoomId(b.getRoomId()));
            }
        } else {
            review.setAuthorName(request.getAuthorName());
            review.setSource(request.getSource() != null ? request.getSource() : "google");
        }

        Review saved = reviewRepository.save(review);
        return ResponseEntity.ok(Map.of(
            "status", "ok",
            "message", "Reseña guardada exitosamente",
            "id", saved.getId(),
            "rating", saved.getRating(),
            "comment", saved.getComment()
        ));
    }
}
