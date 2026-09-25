package com.satoripms.api.review;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

import java.util.List;
import java.util.Map;
import java.util.ArrayList;

@RestController
@RequestMapping("/api/reviews")
public class ReviewController {

    private static final List<Map<String, Object>> MOCK_REVIEWS = new ArrayList<>();

    static {
        MOCK_REVIEWS.add(Map.of("rating", 5, "comment", "¡Excelente atención y servicio! Muy recomendado."));
        MOCK_REVIEWS.add(Map.of("rating", 4, "comment", "Muy bonito hotel, aunque la comida podría mejorar."));
    }

    @GetMapping
    public ResponseEntity<?> getReviews(@RequestParam(defaultValue = "5") int limit) {
        return ResponseEntity.ok(MOCK_REVIEWS.stream().limit(limit).toList());
    }

    @PostMapping
    public ResponseEntity<?> createReview(@RequestBody ReviewRequestDto request) {
        // En el Sprint 1 las reseñas reales en BD están fuera de alcance.
        // Simulamos guardarlas en memoria.
        MOCK_REVIEWS.add(0, Map.of("rating", request.getRating() != null ? request.getRating() : 5,
                                   "comment", request.getComment()));
        return ResponseEntity.ok(Map.of("status", "ok", "message", "Reseña guardada mock"));
    }
}
