package com.satoripms.api.booking;

import com.satoripms.api.room.Room;
import com.satoripms.api.room.RoomRepository;
import com.satoripms.api.guest.Guest;
import com.satoripms.api.guest.GuestRepository;
import com.satoripms.api.event.SpecialEvent;
import com.satoripms.api.event.SpecialEventRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.security.SecureRandom;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Set;
import java.util.UUID;
import java.util.regex.Pattern;

/**
 * Servicio central de la lógica de negocio para la gestión de reservas en SatoriPMS.
 *
 * Responsabilidades:
 * - Consulta y validación de disponibilidad en PostgreSQL y en caché concurrente Redis.
 * - Bloqueos temporales distribuidos (15 min) anti-doble reserva (RN-02).
 * - Confirmación y persistencia atómica por lote con cálculo de tarifas por noche
 *   (eventos especiales) y abonos (50% / 100%).
 * - Consulta, pago de saldo y cancelación por código público TS-XXXX, con verificación
 *   opcional del documento del titular.
 * - Aplicación de la regla de reembolso hotelera sobre lo efectivamente pagado (RN-03).
 */
@Service
public class BookingService {

    /** Mensaje único para "no existe" y "documento no coincide", para no revelar qué códigos existen. */
    static final String NOT_FOUND_MESSAGE = "No se encontró una reserva con ese código y documento";

    private static final String CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    private static final int CODE_LENGTH = 4;
    private static final Pattern UUID_PATTERN =
            Pattern.compile("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$");

    private final BookingRepository bookingRepository;
    private final RoomRepository roomRepository;
    private final GuestRepository guestRepository;
    private final RedisLockService redisLockService;
    private final SecureRandom random = new SecureRandom();

    @Autowired(required = false)
    private SpecialEventRepository specialEventRepository;

    public BookingService(BookingRepository bookingRepository,
                          RoomRepository roomRepository,
                          GuestRepository guestRepository,
                          RedisLockService redisLockService) {
        this.bookingRepository = bookingRepository;
        this.roomRepository = roomRepository;
        this.guestRepository = guestRepository;
        this.redisLockService = redisLockService;
    }

    // ───────────────────────────── Disponibilidad y bloqueos ─────────────────────────────

    /**
     * Verifica si una habitación está libre en un rango de fechas, tanto en PostgreSQL
     * (reservas reales) como en Redis (bloqueos temporales).
     */
    public boolean isAvailable(Long roomId, LocalDate checkIn, LocalDate checkOut) {
        boolean dbAvailable = bookingRepository.countConflictingBookings(roomId, checkIn, checkOut) == 0;
        return dbAvailable && !redisLockService.isLocked(roomId, checkIn, checkOut);
    }

    /**
     * Habitaciones disponibles según fechas, capacidad y mascotas, excluyendo las que tienen
     * un bloqueo temporal activo en Redis.
     */
    public List<Room> listAvailableRooms(LocalDate checkIn, LocalDate checkOut,
                                         Integer adults, Integer children, Boolean pet) {
        List<Room> dbRooms = roomRepository.findAvailableRooms(checkIn, checkOut, adults, children, pet);
        return dbRooms.stream()
                .filter(room -> !redisLockService.isLocked(room.getId(), checkIn, checkOut))
                .toList();
    }

    /**
     * Crea un bloqueo temporal atómico en Redis (15 minutos) para una habitación y rango de fechas.
     *
     * @throws IllegalArgumentException si el rango de fechas no es válido o la habitación no existe
     * @throws IllegalStateException    si la habitación no está disponible o ya está bloqueada
     */
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

    /** Libera uno o varios bloqueos temporales en Redis. Devuelve cuántos se liberaron. */
    public int releaseTemporaryLocks(List<BookingRoomLockDto> locks) {
        if (locks == null || locks.isEmpty()) {
            return 0;
        }
        int releasedCount = 0;
        for (BookingRoomLockDto lock : locks) {
            if (lock != null && lock.getRoomId() != null
                    && lock.getLockToken() != null && !lock.getLockToken().isBlank()
                    && redisLockService.release(lock.getRoomId(), lock.getLockToken().trim())) {
                releasedCount++;
            }
        }
        return releasedCount;
    }

    /**
     * Cotización del alojamiento de una habitación (sin personas adicionales), aplicando los
     * eventos especiales noche a noche. Usada al bloquear una habitación.
     */
    public BigDecimal quoteRoomStay(Room room, LocalDate checkIn, LocalDate checkOut) {
        List<BigDecimal> multipliers = StayPricing.nightlyMultipliers(checkIn, checkOut, activeEvents(checkIn, checkOut));
        return StayPricing.roomStayTotal(room.getPricePerNight(), multipliers);
    }

    // ───────────────────────────── Confirmación ─────────────────────────────

    /** Registra las habitaciones como reserva pendiente de pago (o según la modalidad indicada). */
    @Transactional
    public BookingBatchResponseDto confirmPendingBookings(BookingBatchRequestDto request) {
        return saveBookings(request, "pending_payment", "pending");
    }

    /** Registra las habitaciones como reserva pagada (entornos de prueba). */
    @Transactional
    public BookingBatchResponseDto confirmPaidBookings(BookingBatchRequestDto request) {
        return saveBookings(request, "confirmed", "paid");
    }

    /**
     * Valida, calcula tarifas y persiste de manera transaccional un lote de reservas bajo un
     * único grupo (reservationGroupId) y un único código público TS-XXXX.
     */
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
            // Solo se verifica PostgreSQL: el lock de Redis ya fue validado arriba y pertenece
            // a este mismo solicitante (isLocked() lo rechazaría a sí mismo).
            boolean dbAvailable = bookingRepository.countConflictingBookings(
                    room.getId(), request.getCheckIn(), request.getCheckOut()) == 0;
            if (!Boolean.TRUE.equals(room.getActive()) || !"available".equals(room.getStatus()) || !dbAvailable) {
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

        // Tarifas por noche con eventos especiales (regla provisional, ver StayPricing).
        List<BigDecimal> multipliers = StayPricing.nightlyMultipliers(
                request.getCheckIn(), request.getCheckOut(), activeEvents(request.getCheckIn(), request.getCheckOut()));
        int extraGuests = Math.max(0, guests - baseCapacity);
        BigDecimal averageExtraPrice = selectedRooms.stream()
                .map(Room::getExtraGuestPrice)
                .reduce(BigDecimal.ZERO, BigDecimal::add)
                .divide(BigDecimal.valueOf(selectedRooms.size()), 2, RoundingMode.HALF_UP);
        BigDecimal extraTotal = averageExtraPrice.multiply(BigDecimal.valueOf(extraGuests))
                .multiply(StayPricing.averageMultiplier(multipliers))
                .setScale(2, RoundingMode.HALF_UP);

        List<BigDecimal> roomTotals = new ArrayList<>();
        for (int index = 0; index < selectedRooms.size(); index++) {
            BigDecimal roomTotal = StayPricing.roomStayTotal(selectedRooms.get(index).getPricePerNight(), multipliers);
            if (index == 0) {
                roomTotal = roomTotal.add(extraTotal);
            }
            roomTotals.add(roomTotal);
        }
        BigDecimal totalPrice = roomTotals.stream().reduce(BigDecimal.ZERO, BigDecimal::add);

        // Modalidad de pago (abono 50% vs total 100% vs pendiente de pasarela)
        BigDecimal paidAmount;
        String finalPaymentStatus;
        String finalStatus;
        String option = request.getPaymentOption() == null ? "" : request.getPaymentOption().trim().toLowerCase();
        switch (option) {
            case "deposit" -> {
                paidAmount = totalPrice.divide(BigDecimal.valueOf(2), 2, RoundingMode.HALF_UP);
                finalPaymentStatus = "partial";
                finalStatus = "confirmed";
            }
            case "full" -> {
                paidAmount = totalPrice;
                finalPaymentStatus = "paid";
                finalStatus = "confirmed";
            }
            case "wompi_deposit", "pending_deposit", "wompi_full", "pending_full", "pending" -> {
                paidAmount = BigDecimal.ZERO;
                finalPaymentStatus = "pending";
                finalStatus = "pending_payment";
            }
            default -> {
                paidAmount = "paid".equalsIgnoreCase(paymentStatus) ? totalPrice : BigDecimal.ZERO;
                finalPaymentStatus = paymentStatus;
                finalStatus = status;
            }
        }

        UUID reservationGroupId = UUID.randomUUID();
        String bookingCode = generateBookingCode();
        String companions = request.getCompanions() == null || request.getCompanions().isBlank()
                ? null : request.getCompanions().trim();
        String resolvedSource = (request.getSource() != null && !request.getSource().isBlank())
                ? request.getSource().trim().toLowerCase()
                : "chatbot";

        List<Booking> bookings = new ArrayList<>();
        for (int index = 0; index < selectedRooms.size(); index++) {
            Room room = selectedRooms.get(index);
            BigDecimal roomTotal = roomTotals.get(index);
            Booking booking = new Booking();
            booking.setGuestId(savedGuest.getId());
            booking.setRoomId(room.getId());
            booking.setCheckIn(request.getCheckIn());
            booking.setCheckOut(request.getCheckOut());
            booking.setStatus(finalStatus);
            booking.setPaymentStatus(finalPaymentStatus);
            booking.setAdults(request.getAdults());
            booking.setChildren(request.getChildren());
            booking.setWithPet(request.getHasPet());
            booking.setTotalPrice(roomTotal);
            booking.setPaidAmount(proportionalShare(paidAmount, roomTotal, totalPrice, selectedRooms.size()));
            booking.setSource(resolvedSource);
            booking.setLockId(request.getRooms().get(index).getLockToken());
            booking.setReservationGroupId(reservationGroupId);
            booking.setBookingCode(bookingCode);
            booking.setCompanions(companions);
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
                finalStatus,
                finalPaymentStatus,
                paidAmount,
                totalPrice.subtract(paidAmount),
                bookingCode);
    }

    // ───────────────────────────── Consulta, pago y cancelación ─────────────────────────────

    /**
     * Detalle de una reserva por su código público (TS-XXXX) o UUID de grupo.
     *
     * @param code           código público o UUID del grupo
     * @param holderDocument documento del titular a verificar; null omite la verificación (personal del hotel)
     * @param maskDocument   true para no exponer el documento completo en la respuesta
     */
    public ReservationDetailsDto getReservationDetailsByCode(String code, String holderDocument, boolean maskDocument) {
        List<Booking> bookings = resolveGroup(code);
        Booking first = bookings.get(0);
        Guest guest = guestRepository.findById(first.getGuestId()).orElse(null);
        verifyHolderDocument(guest, holderDocument);

        List<ReservationDetailsDto.RoomSummaryDto> roomSummaries = new ArrayList<>();
        BigDecimal totalGroupPrice = BigDecimal.ZERO;
        for (Booking b : bookings) {
            totalGroupPrice = totalGroupPrice.add(nonNull(b.getTotalPrice()));
            roomRepository.findById(b.getRoomId()).ifPresent(room -> roomSummaries.add(
                    ReservationDetailsDto.RoomSummaryDto.builder()
                            .id(room.getId())
                            .number(room.getNumber())
                            .name(room.getName())
                            .type(room.getType())
                            .pricePerNight(room.getPricePerNight())
                            .build()));
        }

        long nights = ChronoUnit.DAYS.between(first.getCheckIn(), first.getCheckOut());
        BigDecimal totalPaidAmount = bookings.stream()
                .map(b -> nonNull(b.getPaidAmount()))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal pendingBalance = totalGroupPrice.subtract(totalPaidAmount);

        RefundRule refund = RefundRule.forCheckIn(first.getCheckIn());
        BigDecimal estimatedRefund = refund.applyTo(totalPaidAmount);

        boolean isActive = "confirmed".equalsIgnoreCase(first.getStatus()) || "pending_payment".equalsIgnoreCase(first.getStatus());
        boolean canCancel = isActive && LocalDate.now().isBefore(first.getCheckOut());
        boolean canPayRemaining = isActive && "partial".equalsIgnoreCase(first.getPaymentStatus())
                && pendingBalance.compareTo(BigDecimal.ZERO) > 0;

        String statusLabel = switch (first.getStatus().toLowerCase()) {
            case "confirmed" -> "Confirmada";
            case "pending_payment" -> "Pendiente de pago";
            case "cancelled" -> "Cancelada";
            case "finished" -> "Finalizada";
            default -> first.getStatus();
        };
        String paymentStatusLabel = switch (first.getPaymentStatus().toLowerCase()) {
            case "paid" -> "Pagada";
            case "partial" -> "Abono parcial";
            case "pending" -> "Pendiente de pago";
            case "refunded" -> "Reembolsada";
            default -> first.getPaymentStatus();
        };

        String document = guest != null ? guest.getDocumentNumber() : null;
        return ReservationDetailsDto.builder()
                .code(first.getBookingCode())
                .reservationGroupId(first.getReservationGroupId())
                .guestName(guest != null ? guest.getName() : null)
                .guestPhone(guest != null ? guest.getWhatsappPhone() : null)
                .guestDocument(maskDocument ? maskDocument(document) : document)
                .checkIn(first.getCheckIn())
                .checkOut(first.getCheckOut())
                .nights(nights)
                .adults(first.getAdults())
                .children(first.getChildren())
                .companions(first.getCompanions())
                .withPet(first.getWithPet())
                .totalPrice(totalGroupPrice)
                .paidAmount(totalPaidAmount)
                .pendingBalance(pendingBalance)
                .status(first.getStatus())
                .statusLabel(statusLabel)
                .paymentStatus(first.getPaymentStatus())
                .paymentStatusLabel(paymentStatusLabel)
                .rooms(roomSummaries)
                .canCancel(canCancel)
                .canPayRemaining(canPayRemaining)
                .refundPolicy(ReservationDetailsDto.RefundPolicyDto.builder()
                        .hoursUntilCheckin(refund.hoursUntilCheckIn())
                        .refundPercentage(refund.percentage())
                        .estimatedRefund(estimatedRefund)
                        .policyDescription(refund.description())
                        .build())
                .build();
    }

    /**
     * Cancela todas las habitaciones de una reserva y calcula el reembolso sobre lo pagado (RN-03).
     *
     * @param holderDocument documento del titular a verificar; null omite la verificación (personal del hotel)
     */
    @Transactional
    public CancellationResponseDto cancelReservationGroupByCode(String code, String holderDocument) {
        List<Booking> bookings = resolveGroup(code);
        Booking first = bookings.get(0);
        verifyHolderDocument(guestRepository.findById(first.getGuestId()).orElse(null), holderDocument);
        if ("cancelled".equalsIgnoreCase(first.getStatus())) {
            throw new IllegalStateException("Esta reserva ya se encuentra cancelada");
        }

        RefundRule refund = RefundRule.forCheckIn(first.getCheckIn());
        BigDecimal totalGroupPrice = BigDecimal.ZERO;
        BigDecimal totalPaidForGroup = BigDecimal.ZERO;
        for (Booking b : bookings) {
            totalGroupPrice = totalGroupPrice.add(nonNull(b.getTotalPrice()));
            totalPaidForGroup = totalPaidForGroup.add(nonNull(b.getPaidAmount()));
        }

        String newPaymentStatus;
        if ("partial".equalsIgnoreCase(first.getPaymentStatus()) || "paid".equalsIgnoreCase(first.getPaymentStatus())) {
            newPaymentStatus = refund.percentage() > 0 ? "refunded" : "paid";
        } else {
            newPaymentStatus = "pending";
        }

        List<Long> cancelledIds = new ArrayList<>();
        List<String> roomNumbers = new ArrayList<>();
        for (Booking b : bookings) {
            b.setStatus("cancelled");
            b.setPaymentStatus(newPaymentStatus);
            cancelledIds.add(b.getId());
            roomRepository.findById(b.getRoomId()).ifPresent(room -> roomNumbers.add(room.getNumber()));
        }
        bookingRepository.saveAll(bookings);
        bookingRepository.flush();

        return CancellationResponseDto.builder()
                .code(first.getBookingCode())
                .reservationGroupId(first.getReservationGroupId())
                .status("cancelled")
                .paymentStatus(newPaymentStatus)
                .totalPrice(totalGroupPrice)
                .paidAmount(totalPaidForGroup)
                .refundPercentage(refund.percentage())
                .refundAmount(refund.applyTo(totalPaidForGroup))
                .policyDescription(refund.description())
                .cancelledBookingIds(cancelledIds)
                .freedRoomNumbers(roomNumbers)
                .cancelledAt(LocalDateTime.now())
                .message("Tu reserva ha sido cancelada exitosamente y las habitaciones han sido liberadas.")
                .build();
    }

    /**
     * Liquida el saldo pendiente de una reserva abonada al 50%.
     *
     * @param holderDocument documento del titular a verificar; null omite la verificación (personal del hotel)
     */
    @Transactional
    public BookingBatchResponseDto payRemainingBalance(String code, String holderDocument) {
        List<Booking> bookings = resolveGroup(code);
        Booking first = bookings.get(0);
        verifyHolderDocument(guestRepository.findById(first.getGuestId()).orElse(null), holderDocument);
        if ("cancelled".equalsIgnoreCase(first.getStatus())) {
            throw new IllegalStateException("Esta reserva está cancelada");
        }
        if (!"partial".equalsIgnoreCase(first.getPaymentStatus())) {
            throw new IllegalStateException("Esta reserva no tiene un saldo pendiente o ya fue pagada completamente");
        }
        BigDecimal totalGroupPrice = BigDecimal.ZERO;
        for (Booking b : bookings) {
            b.setPaymentStatus("paid");
            b.setPaidAmount(nonNull(b.getTotalPrice()));
            totalGroupPrice = totalGroupPrice.add(nonNull(b.getTotalPrice()));
        }
        bookingRepository.saveAll(bookings);
        bookingRepository.flush();
        return new BookingBatchResponseDto(
                first.getReservationGroupId(),
                totalGroupPrice,
                bookings.stream().map(Booking::getId).toList(),
                bookings.stream().map(Booking::getRoomId).toList(),
                first.getStatus(),
                "paid",
                totalGroupPrice,
                BigDecimal.ZERO,
                first.getBookingCode());
    }

    /**
     * Confirma el pago reportado por una pasarela externa (ej. Wompi APPROVED): pasa la reserva
     * de 'pending_payment' a 'confirmed' con abono parcial (50%) o total (100%).
     */
    @Transactional
    public BookingBatchResponseDto confirmExternalPayment(String code, ExternalPaymentConfirmationDto confirmation) {
        List<Booking> bookings = resolveGroup(code);
        Booking first = bookings.get(0);
        if ("cancelled".equalsIgnoreCase(first.getStatus())) {
            throw new IllegalStateException("No se puede registrar pago para una reserva cancelada");
        }

        BigDecimal totalGroupPrice = bookings.stream()
                .map(b -> nonNull(b.getTotalPrice()))
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        String targetPaymentOption = confirmation != null && confirmation.getPaymentOption() != null
                ? confirmation.getPaymentOption().trim().toLowerCase()
                : null;
        BigDecimal incomingAmount = confirmation != null ? confirmation.getAmount() : null;

        boolean isFullPayment;
        if ("full".equals(targetPaymentOption) || "100".equals(targetPaymentOption)) {
            isFullPayment = true;
        } else if ("deposit".equals(targetPaymentOption) || "50".equals(targetPaymentOption)) {
            isFullPayment = false;
        } else if (incomingAmount != null && incomingAmount.compareTo(totalGroupPrice.multiply(new BigDecimal("0.75"))) >= 0) {
            isFullPayment = true;
        } else {
            isFullPayment = "partial".equalsIgnoreCase(first.getPaymentStatus());
        }

        String newPaymentStatus = isFullPayment ? "paid" : "partial";
        BigDecimal newTotalPaid = isFullPayment
                ? totalGroupPrice
                : (incomingAmount != null && incomingAmount.compareTo(BigDecimal.ZERO) > 0
                    ? incomingAmount
                    : totalGroupPrice.divide(BigDecimal.valueOf(2), 2, RoundingMode.HALF_UP));

        for (Booking b : bookings) {
            b.setStatus("confirmed");
            b.setPaymentStatus(newPaymentStatus);
            b.setPaidAmount(isFullPayment
                    ? nonNull(b.getTotalPrice())
                    : proportionalShare(newTotalPaid, nonNull(b.getTotalPrice()), totalGroupPrice, bookings.size()));
        }
        bookingRepository.saveAll(bookings);
        bookingRepository.flush();

        return new BookingBatchResponseDto(
                first.getReservationGroupId(),
                totalGroupPrice,
                bookings.stream().map(Booking::getId).toList(),
                bookings.stream().map(Booking::getRoomId).toList(),
                "confirmed",
                newPaymentStatus,
                newTotalPaid,
                totalGroupPrice.subtract(newTotalPaid).max(BigDecimal.ZERO),
                first.getBookingCode());
    }

    // ───────────────────────────── Utilidades ─────────────────────────────

    /**
     * Resuelve las reservas de un grupo por código público exacto (TS-XXXX) o UUID completo.
     * Si un código histórico estuviera repetido, se toma el grupo más reciente.
     */
    List<Booking> resolveGroup(String code) {
        if (code == null || code.trim().isBlank()) {
            throw new IllegalArgumentException("El código de reserva es obligatorio");
        }
        String clean = code.trim();
        List<Booking> bookings;
        if (UUID_PATTERN.matcher(clean).matches()) {
            bookings = bookingRepository.findByReservationGroupId(UUID.fromString(clean));
        } else {
            List<Booking> matches = bookingRepository.findByBookingCodeIgnoreCaseOrderByCreatedAtDesc(clean);
            UUID newestGroup = matches.isEmpty() ? null : matches.get(0).getReservationGroupId();
            bookings = newestGroup == null
                    ? matches
                    : matches.stream().filter(b -> newestGroup.equals(b.getReservationGroupId())).toList();
        }
        if (bookings.isEmpty()) {
            throw new NoSuchElementException(NOT_FOUND_MESSAGE);
        }
        return bookings;
    }

    /**
     * Verifica que el documento indicado coincida con el del titular (solo dígitos).
     * Si no coincide responde igual que si la reserva no existiera.
     */
    static void verifyHolderDocument(Guest guest, String holderDocument) {
        if (holderDocument == null) {
            return;
        }
        String expected = guest == null ? "" : digitsOnly(guest.getDocumentNumber());
        String provided = digitsOnly(holderDocument);
        if (expected.isEmpty() || !expected.equals(provided)) {
            throw new NoSuchElementException(NOT_FOUND_MESSAGE);
        }
    }

    /** Deja visibles solo los últimos 4 dígitos del documento. */
    static String maskDocument(String document) {
        String digits = digitsOnly(document);
        if (digits.isEmpty()) {
            return null;
        }
        int visible = Math.min(4, digits.length());
        return "*".repeat(digits.length() - visible) + digits.substring(digits.length() - visible);
    }

    private static String digitsOnly(String value) {
        return value == null ? "" : value.replaceAll("\\D", "");
    }

    /** Genera un código TS-XXXX que no esté en uso. */
    private String generateBookingCode() {
        for (int attempt = 0; attempt < 50; attempt++) {
            StringBuilder sb = new StringBuilder("TS-");
            for (int i = 0; i < CODE_LENGTH; i++) {
                sb.append(CODE_ALPHABET.charAt(random.nextInt(CODE_ALPHABET.length())));
            }
            String candidate = sb.toString();
            if (!bookingRepository.existsByBookingCodeIgnoreCase(candidate)) {
                return candidate;
            }
        }
        throw new IllegalStateException("No fue posible generar un código de reserva único");
    }

    private List<SpecialEvent> activeEvents(LocalDate checkIn, LocalDate checkOut) {
        if (specialEventRepository == null) {
            return List.of();
        }
        return specialEventRepository.findActiveEventsInDateRange(checkIn, checkOut);
    }

    private static BigDecimal proportionalShare(BigDecimal amount, BigDecimal part, BigDecimal whole, int parts) {
        if (parts == 1) {
            return amount;
        }
        if (whole.compareTo(BigDecimal.ZERO) <= 0) {
            return BigDecimal.ZERO;
        }
        BigDecimal fraction = part.divide(whole, 10, RoundingMode.HALF_UP);
        return amount.multiply(fraction).setScale(2, RoundingMode.HALF_UP);
    }

    private static BigDecimal nonNull(BigDecimal value) {
        return value == null ? BigDecimal.ZERO : value;
    }

    /** Regla de reembolso RN-03, con el check-in tomado a las 15:00 del día de llegada. */
    record RefundRule(long hoursUntilCheckIn, int percentage, String description) {

        static RefundRule forCheckIn(LocalDate checkIn) {
            long hours = ChronoUnit.HOURS.between(LocalDateTime.now(), checkIn.atTime(15, 0));
            if (hours > 72) {
                return new RefundRule(hours, 100, "Reembolso del 100% de lo abonado (+72h antes del check-in)");
            }
            if (hours >= 24) {
                return new RefundRule(hours, 50, "Reembolso del 50% de lo abonado (entre 24h y 72h antes del check-in)");
            }
            return new RefundRule(hours, 0, "Sin reembolso (menos de 24h antes del check-in)");
        }

        BigDecimal applyTo(BigDecimal paidAmount) {
            return paidAmount.multiply(BigDecimal.valueOf(percentage))
                    .divide(BigDecimal.valueOf(100), 2, RoundingMode.HALF_UP);
        }
    }
}
