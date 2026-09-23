package com.satoripms.api.booking;

import com.satoripms.api.room.Room;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class BookingController {

    private final BookingService bookingService;

    public BookingController(BookingService bookingService) {
        this.bookingService = bookingService;
    }

    @GetMapping("/rooms/availability")
    public ResponseEntity<List<Room>> getAvailability(
            @RequestParam LocalDate checkIn,
            @RequestParam LocalDate checkOut,
            @RequestParam Integer adults,
            @RequestParam(defaultValue = "0") Integer children,
            @RequestParam(defaultValue = "false") Boolean pet) {
        List<Room> rooms = bookingService.listAvailableRooms(checkIn, checkOut, adults, children, pet);
        return ResponseEntity.ok(rooms);
    }

    @PostMapping("/bookings/lock")
    public ResponseEntity<?> lockRoom(
            @RequestParam Long roomId,
            @RequestParam LocalDate checkIn,
            @RequestParam LocalDate checkOut) {
        String token = bookingService.createTemporaryLock(roomId, checkIn, checkOut);
        return ResponseEntity.ok(Map.of("lockToken", token, "ttlSeconds", 900));
    }

    // CORREGIDO: antes devolvía 200 OK sin hacer nada, lo cual es peor que
    // no responder nada — cualquier cliente (n8n incluido) lo leería como
    // "reserva confirmada" de verdad. Ahora responde 501 explícitamente
    // mientras no esté implementado.
    @PostMapping("/bookings")
    public ResponseEntity<?> confirmBooking() {
        // TODO: llamar a bookingService.confirmBooking(...) cuando esté implementado
        return ResponseEntity.status(HttpStatus.NOT_IMPLEMENTED)
                .body(Map.of("error", "confirmBooking no implementado todavía"));
    }

    @PostMapping("/bookings/{id}/cancellation")
    public ResponseEntity<?> cancelBooking(@PathVariable Long id) {
        // TODO: llamar a bookingService.cancelBooking(id) — aplica RN-03
        return ResponseEntity.status(HttpStatus.NOT_IMPLEMENTED)
                .body(Map.of("error", "cancelBooking no implementado todavía"));
    }
}