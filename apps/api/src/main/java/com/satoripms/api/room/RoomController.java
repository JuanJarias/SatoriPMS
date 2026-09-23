package com.satoripms.api.room;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

@RestController
@RequestMapping("/api/rooms")
public class RoomController {

    @GetMapping("/recommend")
    public ResponseEntity<?> recommendRoom() {
        // TODO: lógica de recomendación asistida por IA (HU-09)
        return ResponseEntity.ok("Recomendaciones");
    }
}