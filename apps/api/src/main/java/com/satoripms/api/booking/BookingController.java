package com.satoripms.api.booking;

import com.satoripms.api.room.Room;
import com.satoripms.api.room.RoomRepository;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class BookingController {

    private final BookingService bookingService;
    private final RoomRepository roomRepository;
    public BookingController(BookingService bookingService, RoomRepository roomRepository) {
        this.bookingService = bookingService;
        this.roomRepository = roomRepository;
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
    public ResponseEntity<?> lockRoom(@RequestBody LockRequestDto request) {
        try {
            String token = bookingService.createTemporaryLock(request.getRoomId(), request.getCheckIn(), request.getCheckOut());
            Room room = roomRepository.findById(request.getRoomId()).orElseThrow();
            long nights = ChronoUnit.DAYS.between(request.getCheckIn(), request.getCheckOut());
            BigDecimal totalPrice = room.getPricePerNight().multiply(BigDecimal.valueOf(nights));

            return ResponseEntity.ok(Map.of(
                    "lockToken", token,
                    "ttlSeconds", 900,
                    "totalPrice", totalPrice
            ));
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", e.getMessage()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/bookings")
    public ResponseEntity<?> confirmBooking(@RequestBody BookingRequestDto request) {
        try {
            Booking booking = bookingService.confirmBooking(request);
            return ResponseEntity.ok(booking);
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", e.getMessage()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/bookings/{id}/payment-confirmation")
    public ResponseEntity<?> confirmPayment(@PathVariable Long id,
                                             @RequestBody(required = false) Map<String, Object> payment) {
        try {
            return ResponseEntity.ok(bookingService.confirmPayment(id));
        } catch (java.util.NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping("/bookings/{id}/cancellation")
    public ResponseEntity<?> cancelBooking(@PathVariable Long id) {
        return ResponseEntity.status(HttpStatus.NOT_IMPLEMENTED)
                .body(Map.of("error", "cancelBooking no implementado todavía"));
    }
}
