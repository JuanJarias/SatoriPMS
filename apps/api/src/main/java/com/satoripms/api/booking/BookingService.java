package com.satoripms.api.booking;

import com.satoripms.api.room.Room;
import com.satoripms.api.room.RoomRepository;
import com.satoripms.api.guest.Guest;
import com.satoripms.api.guest.GuestRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.UUID;

@Service
public class BookingService {

    private final BookingRepository bookingRepository;
    private final RoomRepository roomRepository;
    private final GuestRepository guestRepository;
    private final RedisLockService redisLockService;

    public BookingService(BookingRepository bookingRepository,
                          RoomRepository roomRepository,
                          GuestRepository guestRepository,
                          RedisLockService redisLockService) {
        this.bookingRepository = bookingRepository;
        this.roomRepository = roomRepository;
        this.guestRepository = guestRepository;
        this.redisLockService = redisLockService;
    }

    public boolean isAvailable(Long roomId, LocalDate checkIn, LocalDate checkOut) {
        return bookingRepository.countConflictingBookings(roomId, checkIn, checkOut) == 0;
    }

    public List<Room> listAvailableRooms(LocalDate checkIn, LocalDate checkOut,
                                          Integer adults, Integer children, Boolean pet) {
        return roomRepository.findAvailableRooms(checkIn, checkOut, adults, children, pet);
    }

    public String createTemporaryLock(Long roomId, LocalDate checkIn, LocalDate checkOut) {
        if (checkIn == null || checkOut == null || !checkIn.isBefore(checkOut)) {
            throw new IllegalArgumentException("El check-in debe ser anterior al check-out");
        }
        Room room = roomRepository.findById(roomId)
                .orElseThrow(() -> new IllegalArgumentException("La habitación no existe"));
        if (!Boolean.TRUE.equals(room.getActive()) || !"available".equals(room.getStatus())) {
            throw new IllegalStateException("La habitación no está disponible");
        }
        if (!isAvailable(roomId, checkIn, checkOut)) {
            throw new IllegalStateException("La habitación no está disponible para esas fechas");
        }
        String token = UUID.randomUUID().toString();
        boolean acquired = redisLockService.tryLock(roomId, checkIn, checkOut, token);
        if (!acquired) {
            throw new IllegalStateException("La habitación ya tiene un bloqueo temporal activo");
        }
        return token;
    }

    @Transactional
    public Booking confirmBooking(BookingRequestDto request) {
        if (!redisLockService.isValid(request.getRoomId(), request.getLockToken())) {
            throw new IllegalStateException("El bloqueo temporal ha expirado o no es válido");
        }

        Room room = roomRepository.findById(request.getRoomId())
                .orElseThrow(() -> new IllegalArgumentException("La habitación no existe"));

        long nights = ChronoUnit.DAYS.between(request.getCheckIn(), request.getCheckOut());
        BigDecimal totalPrice = room.getPricePerNight().multiply(BigDecimal.valueOf(nights));

        Guest guest = guestRepository.findByWhatsappPhone(request.getWaId())
                .orElseGet(() -> {
                    Guest newGuest = new Guest();
                    newGuest.setWhatsappPhone(request.getWaId());
                    return guestRepository.save(newGuest);
                });

        Booking booking = new Booking();
        booking.setGuestId(guest.getId());
        booking.setRoomId(room.getId());
        booking.setCheckIn(request.getCheckIn());
        booking.setCheckOut(request.getCheckOut());
        booking.setStatus("pending_payment");
        booking.setPaymentStatus("pending");
        booking.setAdults(request.getAdults());
        booking.setChildren(request.getChildren());
        booking.setWithPet(request.getHasPet());
        booking.setTotalPrice(totalPrice);
        booking.setSource("chatbot");
        booking.setLockId(request.getLockToken());

        Booking savedBooking = bookingRepository.save(booking);

        redisLockService.release(request.getRoomId(), request.getLockToken());

        return savedBooking;
    }

    public void cancelBooking(Long id) {
        throw new UnsupportedOperationException("cancelBooking aún no implementado");
    }

    @Transactional
    public Booking confirmPayment(Long id) {
        Booking booking = bookingRepository.findById(id).orElseThrow();
        booking.setPaymentStatus("paid");
        booking.setStatus("confirmed");
        return bookingRepository.save(booking);
    }
}
