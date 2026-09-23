package com.satoripms.api.review;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

@RestController
@RequestMapping("/api/reviews")
public class ReviewController {

    @GetMapping
    public ResponseEntity<?> getReviews(@RequestParam(defaultValue = "5") int limit) {
        // TODO: retornar las reseñas
        return ResponseEntity.ok("Reseñas");
    }
}