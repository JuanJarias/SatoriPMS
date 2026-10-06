package com.satoripms.api.booking;

import com.satoripms.api.guest.Guest;
import com.satoripms.api.guest.GuestRepository;
import com.satoripms.api.room.Room;
import com.satoripms.api.room.RoomRepository;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.beans.factory.annotation.Value;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class BookingController {

    private final BookingService bookingService;
    private final RoomRepository roomRepository;
    private final GuestRepository guestRepository;
    private final BookingRepository bookingRepository;
    @Value("${satori.booking.test-payment-enabled:false}")
    private boolean testPaymentEnabled;

    public BookingController(BookingService bookingService,
                            RoomRepository roomRepository,
                            GuestRepository guestRepository,
                            BookingRepository bookingRepository) {
        this.bookingService = bookingService;
        this.roomRepository = roomRepository;
        this.guestRepository = guestRepository;
        this.bookingRepository = bookingRepository;
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

    @GetMapping("/bookings/debug")
    public ResponseEntity<List<Map<String, Object>>> listDebugBookings() {
        List<Map<String, Object>> rows = new ArrayList<>();

        for (Booking booking : bookingRepository.findAllByOrderByCreatedAtDesc()) {
            Guest guest = guestRepository.findById(booking.getGuestId()).orElse(null);
            Room room = roomRepository.findById(booking.getRoomId()).orElse(null);

            Map<String, Object> row = new HashMap<>();
            row.put("id", booking.getId());
            row.put("reservationGroupId", booking.getReservationGroupId());
            row.put("status", booking.getStatus());
            row.put("paymentStatus", booking.getPaymentStatus());
            row.put("checkIn", booking.getCheckIn());
            row.put("checkOut", booking.getCheckOut());
            row.put("roomId", booking.getRoomId());
            row.put("roomNumber", room != null ? room.getNumber() : null);
            row.put("roomName", room != null ? room.getName() : null);
            row.put("guestId", booking.getGuestId());
            row.put("guestName", guest != null ? guest.getName() : null);
            row.put("guestPhone", guest != null ? guest.getWhatsappPhone() : null);
            row.put("guestDocument", guest != null ? guest.getDocumentNumber() : null);
            row.put("adults", booking.getAdults());
            row.put("children", booking.getChildren());
            row.put("withPet", booking.getWithPet());
            row.put("companions", booking.getCompanions());
            row.put("totalPrice", booking.getTotalPrice());
            row.put("source", booking.getSource());
            row.put("createdAt", booking.getCreatedAt());
            row.put("updatedAt", booking.getUpdatedAt());
            rows.add(row);
        }

        return ResponseEntity.ok(rows);
    }

    @PostMapping("/bookings/test-paid")
    public ResponseEntity<?> confirmTestPayment(@RequestBody BookingBatchRequestDto request) {
        if (!testPaymentEnabled) {
            return ResponseEntity.notFound().build();
        }
        try {
            return ResponseEntity.ok(bookingService.confirmPaidBookings(request));
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", e.getMessage()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/bookings/confirm")
    public ResponseEntity<?> confirmPendingBookings(@RequestBody BookingBatchRequestDto request) {
        try {
            return ResponseEntity.ok(bookingService.confirmPendingBookings(request));
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", e.getMessage()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/bookings/group/{code}")
    public ResponseEntity<?> getReservationDetails(@PathVariable String code) {
        try {
            return ResponseEntity.ok(bookingService.getReservationDetailsByCode(code));
        } catch (java.util.NoSuchElementException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", e.getMessage()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/bookings/group/{code}/cancellation")
    public ResponseEntity<?> cancelReservationGroup(@PathVariable String code) {
        try {
            return ResponseEntity.ok(bookingService.cancelReservationGroupByCode(code));
        } catch (java.util.NoSuchElementException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", e.getMessage()));
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
                .body(Map.of("error", "Por favor use POST /api/bookings/group/{code}/cancellation"));
    }
}
