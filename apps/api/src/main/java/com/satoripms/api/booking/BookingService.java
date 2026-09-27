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
import java.util.HashSet;
import java.util.ArrayList;
import java.util.Set;
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

    @Transactional
    public BookingBatchResponseDto confirmPendingBookings(BookingBatchRequestDto request) {
        return saveBookings(request, "pending_payment", "pending");
    }

    @Transactional
    public BookingBatchResponseDto confirmPaidBookings(BookingBatchRequestDto request) {
        return saveBookings(request, "confirmed", "paid");
    }

    private BookingBatchResponseDto saveBookings(BookingBatchRequestDto request, String status, String paymentStatus) {
        if (request == null || request.getRooms() == null || request.getRooms().isEmpty()) {
            throw new IllegalArgumentException("Debe seleccionarse al menos una habitación");
        }
        if (request.getWaId() == null || request.getWaId().isBlank()
                || request.getGuestName() == null || request.getGuestName().isBlank()
                || request.getGuestDocument() == null || request.getGuestDocument().isBlank()) {
            throw new IllegalArgumentException("Faltan datos obligatorios del huésped");
        }
        if (!request.getGuestDocument().matches("\\d{6,10}")) {
            throw new IllegalArgumentException("La identificación debe contener entre 6 y 10 dígitos");
        }
        if (request.getCheckIn() == null || request.getCheckOut() == null
                || !request.getCheckIn().isBefore(request.getCheckOut())) {
            throw new IllegalArgumentException("El check-in debe ser anterior al check-out");
        }
        if (request.getAdults() == null || request.getAdults() < 1
                || request.getChildren() == null || request.getChildren() < 0
                || request.getHasPet() == null) {
            throw new IllegalArgumentException("Los datos de ocupación no son válidos");
        }

        Set<Long> roomIds = new HashSet<>();
        List<Room> selectedRooms = new ArrayList<>();
        for (BookingRoomLockDto roomLock : request.getRooms()) {
            if (roomLock.getRoomId() == null || roomLock.getLockToken() == null
                    || roomLock.getLockToken().isBlank() || !roomIds.add(roomLock.getRoomId())) {
                throw new IllegalArgumentException("La selección de habitaciones no es válida");
            }
            if (!redisLockService.isValid(roomLock.getRoomId(), roomLock.getLockToken())) {
                throw new IllegalStateException("Un bloqueo temporal expiró o no es válido");
            }
            Room room = roomRepository.findById(roomLock.getRoomId())
                    .orElseThrow(() -> new IllegalArgumentException("La habitación no existe"));
            if (!Boolean.TRUE.equals(room.getActive()) || !"available".equals(room.getStatus())
                    || !isAvailable(room.getId(), request.getCheckIn(), request.getCheckOut())) {
                throw new IllegalStateException("Una habitación ya no está disponible");
            }
            if (Boolean.TRUE.equals(request.getHasPet()) && !Boolean.TRUE.equals(room.getAllowsPets())) {
                throw new IllegalArgumentException("Una habitación seleccionada no permite mascotas");
            }
            selectedRooms.add(room);
        }

        int maxCapacity = selectedRooms.stream()
                .mapToInt(room -> room.getMaxAdultsCapacity() + room.getChildrenCapacity()).sum();
        int baseCapacity = selectedRooms.stream().mapToInt(Room::getBaseAdultsCapacity).sum();
        int guests = request.getAdults() + request.getChildren();
        if (guests > maxCapacity) {
            throw new IllegalArgumentException("La capacidad de las habitaciones es insuficiente");
        }

        Guest guest = guestRepository.findByWhatsappPhone(request.getWaId())
                .orElseGet(() -> {
                    Guest newGuest = new Guest();
                    newGuest.setWhatsappPhone(request.getWaId());
                    return newGuest;
                });
        guest.setName(request.getGuestName().trim());
        guest.setDocumentNumber(request.getGuestDocument().trim());
        Guest savedGuest = guestRepository.save(guest);

        long nights = ChronoUnit.DAYS.between(request.getCheckIn(), request.getCheckOut());
        BigDecimal baseTotal = selectedRooms.stream()
                .map(room -> room.getPricePerNight().multiply(BigDecimal.valueOf(nights)))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        int extraGuests = Math.max(0, guests - baseCapacity);
        BigDecimal averageExtraPrice = selectedRooms.stream()
                .map(Room::getExtraGuestPrice)
                .reduce(BigDecimal.ZERO, BigDecimal::add)
                .divide(BigDecimal.valueOf(selectedRooms.size()), 2, java.math.RoundingMode.HALF_UP);
        BigDecimal extraTotal = averageExtraPrice.multiply(BigDecimal.valueOf(extraGuests));
        BigDecimal totalPrice = baseTotal.add(extraTotal);
        UUID reservationGroupId = UUID.randomUUID();
        List<Booking> bookings = new ArrayList<>();

        for (int index = 0; index < selectedRooms.size(); index++) {
            Room room = selectedRooms.get(index);
            Booking booking = new Booking();
            booking.setGuestId(savedGuest.getId());
            booking.setRoomId(room.getId());
            booking.setCheckIn(request.getCheckIn());
            booking.setCheckOut(request.getCheckOut());
            booking.setStatus(status);
            booking.setPaymentStatus(paymentStatus);
            booking.setAdults(request.getAdults());
            booking.setChildren(request.getChildren());
            booking.setWithPet(request.getHasPet());
            BigDecimal roomTotal = room.getPricePerNight().multiply(BigDecimal.valueOf(nights));
            if (index == 0) roomTotal = roomTotal.add(extraTotal);
            booking.setTotalPrice(roomTotal);
            booking.setSource("chatbot");
            booking.setLockId(request.getRooms().get(index).getLockToken());
            booking.setReservationGroupId(reservationGroupId);
            booking.setCompanions(request.getCompanions());
            bookings.add(booking);
        }

        List<Booking> savedBookings = bookingRepository.saveAll(bookings);
        bookingRepository.flush();
        for (BookingRoomLockDto roomLock : request.getRooms()) {
            redisLockService.release(roomLock.getRoomId(), roomLock.getLockToken());
        }

        return new BookingBatchResponseDto(
                reservationGroupId,
                totalPrice,
                savedBookings.stream().map(Booking::getId).toList(),
                selectedRooms.stream().map(Room::getId).toList(),
                status,
                paymentStatus);
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
