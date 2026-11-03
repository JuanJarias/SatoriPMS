package com.satoripms.api.booking;

import com.satoripms.api.room.Room;
import com.satoripms.api.room.RoomRepository;
import com.satoripms.api.guest.Guest;
import com.satoripms.api.guest.GuestRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.HashSet;
import java.util.ArrayList;
import java.util.Set;
import java.util.UUID;

/**
 * Servicio central de la lógica de negocio para la gestión de reservas en SatoriPMS.
 *
 * Responsabilidades:
 * - Consulta y validación de disponibilidad en PostgreSQL y en caché concurrente Redis.
 * - Bloqueos temporales distribuidos (15 min) anti-doble reserva (RN-02).
 * - Confirmación y persistencia atómica por lote con cálculo proporcional de tarifas y abonos (50% / 100%).
 * - Consulta de información y estado de reservas mediante código de reserva.
 * - Cancelación de reservas grupales y aplicación de la regla de reembolso hotelera (RN-03).
 * - Pago de saldo restante para reservas garantizadas con abono inicial.
 */
@Service
public class BookingService {

    private final BookingRepository bookingRepository;
    private final RoomRepository roomRepository;
    private final GuestRepository guestRepository;
    private final RedisLockService redisLockService;

    /**
     * Constructor con inyección de dependencias.
     *
     * @param bookingRepository Repositorio JPA de reservas
     * @param roomRepository    Repositorio JPA de habitaciones
     * @param guestRepository   Repositorio JPA de huéspedes
     * @param redisLockService  Servicio de bloqueos distribuidos en Redis
     */
    public BookingService(BookingRepository bookingRepository,
                          RoomRepository roomRepository,
                          GuestRepository guestRepository,
                          RedisLockService redisLockService) {
        this.bookingRepository = bookingRepository;
        this.roomRepository = roomRepository;
        this.guestRepository = guestRepository;
        this.redisLockService = redisLockService;
    }

    /**
     * Verifica si una habitación se encuentra completamente libre en un rango de fechas.
     * Valida tanto la ausencia de reservas reales en base de datos como la ausencia
     * de un bloqueo temporal activo en Redis.
     *
     * @param roomId   Identificador único de la habitación
     * @param checkIn  Fecha de llegada
     * @param checkOut Fecha de salida
     * @return true si la habitación está disponible en ambas capas, false si hay conflicto
     */
    public boolean isAvailable(Long roomId, LocalDate checkIn, LocalDate checkOut) {
        // 1. Verifica en SQL (reservas reales)
        boolean dbAvailable = bookingRepository.countConflictingBookings(roomId, checkIn, checkOut) == 0;
        
        // 2. Verifica en Redis (bloqueos temporales)
        return dbAvailable && !redisLockService.isLocked(roomId, checkIn, checkOut);
    }

    /**
     * Consulta y filtra el catálogo de habitaciones disponibles según fechas, capacidad
     * de adultos, niños y admisión de mascotas.
     * Excluye automáticamente cualquier habitación con un bloqueo temporal activo en Redis.
     *
     * @param checkIn  Fecha de check-in
     * @param checkOut Fecha de check-out
     * @param adults   Número de adultos
     * @param children Número de niños
     * @param pet      Si el huésped viaja con mascota
     * @return Lista de habitaciones que cumplen los criterios y no están bloqueadas
     */
    public List<Room> listAvailableRooms(LocalDate checkIn, LocalDate checkOut,
                                          Integer adults, Integer children, Boolean pet) {
        // 1. Trae las habitaciones libres según PostgreSQL
        List<Room> dbRooms = roomRepository.findAvailableRooms(checkIn, checkOut, adults, children, pet);
        
        // 2. Excluye de la lista las que están bloqueadas actualmente en Redis
        return dbRooms.stream()
                .filter(room -> !redisLockService.isLocked(room.getId(), checkIn, checkOut))
                .toList();
    }

    /**
     * Crea un bloqueo temporal atómico en Redis para una habitación y rango de fechas.
     * Permite al usuario tener 15 minutos exclusivos para ingresar sus datos o procesar el pago.
     *
     * @param roomId   Identificador de la habitación
     * @param checkIn  Fecha de llegada
     * @param checkOut Fecha de salida
     * @return Token de bloqueo (UUID) si fue exitoso
     * @throws IllegalArgumentException Si el rango de fechas no es válido
     * @throws IllegalStateException Si la habitación no existe, no está activa o ya está bloqueada
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

    /**
     * Confirma una o varias habitaciones en estado de reserva pendiente de pago.
     *
     * @param request Datos de la reserva grupal o individual y tokens de bloqueo
     * @return Resumen con ID de grupo, montos, IDs creados y estados
     */
    @Transactional
    public BookingBatchResponseDto confirmPendingBookings(BookingBatchRequestDto request) {
        return saveBookings(request, "pending_payment", "pending");
    }

    /**
     * Confirma una o varias habitaciones con registro de pago confirmado.
     *
     * @param request Datos de la reserva y tokens de bloqueo
     * @return Resumen con ID de grupo, montos pagados, IDs creados y estados
     */
    @Transactional
    public BookingBatchResponseDto confirmPaidBookings(BookingBatchRequestDto request) {
        return saveBookings(request, "confirmed", "paid");
    }

    /**
     * Valida, calcula tarifas y persiste de manera transaccional un lote de reservas.
     * Asocia las habitaciones a un único UUID de grupo de reserva (reservationGroupId),
     * vincula o actualiza el perfil del huésped, calcula el abono (50% o 100%) y libera
     * los bloqueos temporales en Redis.
     *
     * @param request       Datos de la solicitud de reserva
     * @param status        Estado inicial de la reserva ('confirmed' o 'pending_payment')
     * @param paymentStatus Estado inicial del pago ('paid', 'partial' o 'pending')
     * @return DTO con el resultado de la reserva agrupada
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
            // Solo verificamos en PostgreSQL (reservas reales). NO verificamos Redis
            // porque el lock ya fue validado via isValid() arriba — el usuario YA
            // posee ese lock, así que isLocked() retornaría true y se auto-rechazaría.
            boolean dbAvailable = bookingRepository.countConflictingBookings(
                    room.getId(), request.getCheckIn(), request.getCheckOut()) == 0;
            if (!Boolean.TRUE.equals(room.getActive()) || !"available".equals(room.getStatus())
                    || !dbAvailable) {
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

        // Determinación de importes de pago según opción elegida (abono 50% vs total 100%)
        BigDecimal paidAmount;
        String finalPaymentStatus;
        String finalStatus;
        if ("deposit".equalsIgnoreCase(request.getPaymentOption())) {
            paidAmount = totalPrice.divide(BigDecimal.valueOf(2), 2, java.math.RoundingMode.HALF_UP);
            finalPaymentStatus = "partial";
            finalStatus = "confirmed";
        } else if ("full".equalsIgnoreCase(request.getPaymentOption())) {
            paidAmount = totalPrice;
            finalPaymentStatus = "paid";
            finalStatus = "confirmed";
        } else {
            paidAmount = paymentStatus.equalsIgnoreCase("paid") ? totalPrice : BigDecimal.ZERO;
            finalPaymentStatus = paymentStatus;
            finalStatus = status;
        }

        UUID reservationGroupId = UUID.randomUUID();
        List<Booking> bookings = new ArrayList<>();

        for (int index = 0; index < selectedRooms.size(); index++) {
            Room room = selectedRooms.get(index);
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
            BigDecimal roomTotal = room.getPricePerNight().multiply(BigDecimal.valueOf(nights));
            if (index == 0) roomTotal = roomTotal.add(extraTotal);
            booking.setTotalPrice(roomTotal);

            // Asignar importe pagado proporcional a cada habitación
            BigDecimal roomPaidAmount;
            if (selectedRooms.size() == 1) {
                roomPaidAmount = paidAmount;
            } else {
                BigDecimal roomFraction = roomTotal.divide(totalPrice, 10, java.math.RoundingMode.HALF_UP);
                roomPaidAmount = paidAmount.multiply(roomFraction).setScale(2, java.math.RoundingMode.HALF_UP);
            }
            booking.setPaidAmount(roomPaidAmount);
            booking.setSource("chatbot");
            booking.setLockId(request.getRooms().get(index).getLockToken());
            booking.setReservationGroupId(reservationGroupId);
            booking.setCompanions(request.getCompanions());
            bookings.add(booking);
        }

        List<Booking> savedBookings = bookingRepository.saveAll(bookings);
        bookingRepository.flush();

        // Liberación de bloqueos temporales en Redis
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
                totalPrice.subtract(paidAmount));
    }

    /**
     * Consulta la información detallada de una reserva mediante su prefijo de código (8 caracteres)
     * o UUID completo.
     * Retorna datos del huésped, habitaciones reservadas, desglose financiero (total, pagado, saldo pendiente)
     * y el cálculo de la política de reembolso (RN-03).
     *
     * @param code Código o prefijo de reserva
     * @return DTO con los detalles completos de la reserva
     * @throws NoSuchElementException Si el código no coincide con ninguna reserva
     */
    public ReservationDetailsDto getReservationDetailsByCode(String code) {
        if (code == null || code.trim().isBlank()) {
            throw new IllegalArgumentException("El código de reserva es obligatorio");
        }
        String cleanCode = code.trim().toLowerCase();
        List<Booking> bookings = bookingRepository.findByReservationGroupCodePrefix(cleanCode);
        if (bookings.isEmpty()) {
            throw new java.util.NoSuchElementException("No se encontró ninguna reserva con el código: " + code.trim());
        }

        Booking first = bookings.get(0);
        Guest guest = guestRepository.findById(first.getGuestId()).orElse(null);

        List<ReservationDetailsDto.RoomSummaryDto> roomSummaries = new ArrayList<>();
        BigDecimal totalGroupPrice = BigDecimal.ZERO;

        for (Booking b : bookings) {
            Room room = roomRepository.findById(b.getRoomId()).orElse(null);
            totalGroupPrice = totalGroupPrice.add(b.getTotalPrice() != null ? b.getTotalPrice() : BigDecimal.ZERO);
            if (room != null) {
                roomSummaries.add(ReservationDetailsDto.RoomSummaryDto.builder()
                        .id(room.getId())
                        .number(room.getNumber())
                        .name(room.getName())
                        .type(room.getType())
                        .pricePerNight(room.getPricePerNight())
                        .build());
            }
        }

        long nights = ChronoUnit.DAYS.between(first.getCheckIn(), first.getCheckOut());
        String codePrefix = first.getReservationGroupId() != null
                ? first.getReservationGroupId().toString().substring(0, 8).toUpperCase()
                : "RES-" + first.getId();

        BigDecimal totalPaidAmount = bookings.stream()
                .map(b -> b.getPaidAmount() != null ? b.getPaidAmount() : BigDecimal.ZERO)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal pendingBalance = totalGroupPrice.subtract(totalPaidAmount);

        // Política de reembolso RN-03:
        // Check-in se toma a las 15:00 del día de llegada
        LocalDateTime checkInDateTime = first.getCheckIn().atTime(15, 0);
        LocalDateTime now = LocalDateTime.now();
        long hoursUntilCheckIn = ChronoUnit.HOURS.between(now, checkInDateTime);

        int refundPct;
        String policyDesc;
        if (hoursUntilCheckIn > 72) {
            refundPct = 100;
            policyDesc = "Reembolso del 100% (+72h antes del check-in)";
        } else if (hoursUntilCheckIn >= 24) {
            refundPct = 50;
            policyDesc = "Reembolso del 50% (entre 24h y 72h antes del check-in)";
        } else {
            refundPct = 0;
            policyDesc = "Sin reembolso (menos de 24h antes del check-in)";
        }

        BigDecimal estimatedRefund = totalGroupPrice.multiply(BigDecimal.valueOf(refundPct))
                .divide(BigDecimal.valueOf(100), 2, java.math.RoundingMode.HALF_UP);

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
            case "pending" -> "Pendiente de pago";
            case "refunded" -> "Reembolsada";
            case "refund_pending" -> "Reembolso en trámite";
            case "cancelled" -> "Cancelada";
            case "no_refund" -> "Sin reembolso";
            default -> first.getPaymentStatus();
        };

        return ReservationDetailsDto.builder()
                .code(codePrefix)
                .reservationGroupId(first.getReservationGroupId())
                .guestName(guest != null ? guest.getName() : null)
                .guestPhone(guest != null ? guest.getWhatsappPhone() : null)
                .guestDocument(guest != null ? guest.getDocumentNumber() : null)
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
                        .hoursUntilCheckin(hoursUntilCheckIn)
                        .refundPercentage(refundPct)
                        .estimatedRefund(estimatedRefund)
                        .policyDescription(policyDesc)
                        .build())
                .build();
    }

    /**
     * Cancela todas las habitaciones asociadas a un código de reserva grupal,
     * liberando la disponibilidad en base de datos para nuevas reservas y calculando
     * el reembolso aplicable según las horas de antelación al check-in (RN-03).
     *
     * @param code Código o prefijo de reserva
     * @return DTO con el resultado de la cancelación y montos a reembolsar
     * @throws NoSuchElementException Si el código no existe
     * @throws IllegalStateException Si la reserva ya fue cancelada previamente
     */
    @Transactional
    public CancellationResponseDto cancelReservationGroupByCode(String code) {
        if (code == null || code.trim().isBlank()) {
            throw new IllegalArgumentException("El código de reserva es obligatorio");
        }
        String cleanCode = code.trim().toLowerCase();
        List<Booking> bookings = bookingRepository.findByReservationGroupCodePrefix(cleanCode);
        if (bookings.isEmpty()) {
            throw new java.util.NoSuchElementException("No se encontró ninguna reserva con el código: " + code.trim());
        }

        Booking first = bookings.get(0);
        if ("cancelled".equalsIgnoreCase(first.getStatus())) {
            throw new IllegalStateException("Esta reserva ya se encuentra cancelada");
        }

        // Calcular política de reembolso RN-03 (15:00 del día de llegada)
        LocalDateTime checkInDateTime = first.getCheckIn().atTime(15, 0);
        LocalDateTime now = LocalDateTime.now();
        long hoursUntilCheckIn = ChronoUnit.HOURS.between(now, checkInDateTime);

        int refundPct;
        String policyDesc;
        if (hoursUntilCheckIn > 72) {
            refundPct = 100;
            policyDesc = "Reembolso del 100% (+72h antes del check-in)";
        } else if (hoursUntilCheckIn >= 24) {
            refundPct = 50;
            policyDesc = "Reembolso del 50% (entre 24h y 72h antes del check-in)";
        } else {
            refundPct = 0;
            policyDesc = "Sin reembolso (menos de 24h antes del check-in)";
        }

        BigDecimal totalGroupPrice = BigDecimal.ZERO;
        BigDecimal totalPaidForGroup = BigDecimal.ZERO;
        List<Long> cancelledIds = new ArrayList<>();
        List<String> roomNumbers = new ArrayList<>();

        for (Booking b : bookings) {
            totalGroupPrice = totalGroupPrice.add(b.getTotalPrice() != null ? b.getTotalPrice() : BigDecimal.ZERO);
            totalPaidForGroup = totalPaidForGroup.add(b.getPaidAmount() != null ? b.getPaidAmount() : BigDecimal.ZERO);
        }

        String newPaymentStatus;
        if ("partial".equalsIgnoreCase(first.getPaymentStatus()) || "paid".equalsIgnoreCase(first.getPaymentStatus())) {
            newPaymentStatus = refundPct > 0 ? "refunded" : "paid";
        } else {
            newPaymentStatus = "pending";
        }

        for (Booking b : bookings) {
            b.setStatus("cancelled");
            b.setPaymentStatus(newPaymentStatus);
            cancelledIds.add(b.getId());

            Room room = roomRepository.findById(b.getRoomId()).orElse(null);
            if (room != null) {
                roomNumbers.add(room.getNumber());
            }
        }

        bookingRepository.saveAll(bookings);
        bookingRepository.flush();

        BigDecimal refundAmount = totalPaidForGroup.multiply(BigDecimal.valueOf(refundPct))
                .divide(BigDecimal.valueOf(100), 2, java.math.RoundingMode.HALF_UP);

        String codePrefix = first.getReservationGroupId() != null
                ? first.getReservationGroupId().toString().substring(0, 8).toUpperCase()
                : "RES-" + first.getId();

        return CancellationResponseDto.builder()
                .code(codePrefix)
                .reservationGroupId(first.getReservationGroupId())
                .status("cancelled")
                .paymentStatus(newPaymentStatus)
                .totalPrice(totalGroupPrice)
                .paidAmount(totalPaidForGroup)
                .refundPercentage(refundPct)
                .refundAmount(refundAmount)
                .policyDescription(policyDesc)
                .cancelledBookingIds(cancelledIds)
                .freedRoomNumbers(roomNumbers)
                .cancelledAt(LocalDateTime.now())
                .message("Tu reserva ha sido cancelada exitosamente y las habitaciones han sido liberadas.")
                .build();
    }

    /**
     * Liquida el saldo pendiente de una reserva que pagó inicialmente el 50% de abono.
     * Actualiza el estado de pago a 'paid' y el monto pagado al total de la reserva.
     *
     * @param code Código o prefijo de reserva
     * @return DTO con la confirmación de la actualización del saldo a cero
     * @throws NoSuchElementException Si la reserva no existe
     * @throws IllegalStateException Si la reserva está cancelada o no tiene saldo pendiente
     */
    @Transactional
    public BookingBatchResponseDto payRemainingBalance(String code) {
        if (code == null || code.trim().isBlank()) {
            throw new IllegalArgumentException("El código de reserva es obligatorio");
        }
        String cleanCode = code.trim().toLowerCase();
        List<Booking> bookings = bookingRepository.findByReservationGroupCodePrefix(cleanCode);
        if (bookings.isEmpty()) {
            throw new java.util.NoSuchElementException("No se encontró ninguna reserva con el código: " + code.trim());
        }
        Booking first = bookings.get(0);
        if (!"partial".equalsIgnoreCase(first.getPaymentStatus())) {
            throw new IllegalStateException("Esta reserva no tiene un saldo pendiente o ya fue pagada completamente");
        }
        if ("cancelled".equalsIgnoreCase(first.getStatus())) {
            throw new IllegalStateException("Esta reserva está cancelada");
        }
        BigDecimal totalGroupPrice = BigDecimal.ZERO;
        for (Booking b : bookings) {
            b.setPaymentStatus("paid");
            b.setPaidAmount(b.getTotalPrice() != null ? b.getTotalPrice() : BigDecimal.ZERO);
            totalGroupPrice = totalGroupPrice.add(b.getTotalPrice() != null ? b.getTotalPrice() : BigDecimal.ZERO);
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
                BigDecimal.ZERO);
    }
}
