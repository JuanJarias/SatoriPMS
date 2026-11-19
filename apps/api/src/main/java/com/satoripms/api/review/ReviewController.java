package com.satoripms.api.review;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * Controlador REST para la consulta en tiempo real de Reseñas Oficiales de Google Reviews en SatoriPMS.
 *
 * Extrae y expone exclusivamente datos reales del perfil oficial de Hotel Torre Satori
 * en Google Reviews (solo lectura, sin reseñas simuladas ni redirecciones externas).
 */
@RestController
@RequestMapping("/api/reviews")
public class ReviewController {

    private final GoogleReviewsService googleReviewsService;

    public ReviewController(GoogleReviewsService googleReviewsService) {
        this.googleReviewsService = googleReviewsService;
    }

    /**
     * Retorna las reseñas reales obtenidas desde Google Reviews.
     *
     * @param limit   Cantidad máxima de registros a retornar (por defecto 50)
     * @param refresh Si es true, fuerza la actualización en vivo omitiendo la caché de 15 minutos
     * @return Lista de reseñas reales de Google Reviews
     */
    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> getReviews(
            @RequestParam(defaultValue = "50") int limit,
            @RequestParam(defaultValue = "false") boolean refresh
    ) {
        return ResponseEntity.ok(googleReviewsService.getReviews(limit, refresh));
    }

    /**
     * Provee el resumen oficial en vivo desde Google Reviews:
     * calificación promedio real, total de opiniones, distribución exacta por estrellas
     * y listado de opiniones reales disponibles.
     *
     * @param refresh Si es true, fuerza la actualización en vivo desde Google
     * @return Métricas y reseñas reales para el panel de visualización web
     */
    @GetMapping("/summary")
    public ResponseEntity<Map<String, Object>> getReviewsSummary(
            @RequestParam(defaultValue = "false") boolean refresh
    ) {
        return ResponseEntity.ok(googleReviewsService.getSummary(refresh));
    }
}
