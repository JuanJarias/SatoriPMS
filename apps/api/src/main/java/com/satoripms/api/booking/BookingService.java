package com.satoripms.api.booking;

import com.satoripms.api.room.Room;
import com.satoripms.api.room.RoomRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@Service
public class BookingService {

    private final BookingRepository bookingRepository;
    private final RoomRepository roomRepository;
    private final RedisLockService redisLockService;

    public BookingService(BookingRepository bookingRepository,
                           RoomRepository roomRepository,
                           RedisLockService redisLockService) {
        this.bookingRepository = bookingRepository;
        this.roomRepository = roomRepository;
        this.redisLockService = redisLockService;
    }

    public boolean isAvailable(Long roomId, LocalDate checkIn, LocalDate checkOut) {
        return bookingRepository.countConflictingBookings(roomId, checkIn, checkOut) == 0;
    }

    public List<Room> listAvailableRooms(LocalDate checkIn, LocalDate checkOut,
                                          Integer adults, Integer children, Boolean pet) {
        return roomRepository.findAvailableRooms(checkIn, checkOut, adults, children, pet);
    }

    /**
     * Valida contra Postgres (fuente de verdad) y, si está libre, crea el
    * bloqueo del rango en Redis con TTL 900s. Los rangos solapados se
    * rechazan de forma atómica y los rangos contiguos permanecen permitidos.
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

    public void confirmBooking() {
        // TODO: validar el token con redisLockService.isValid(roomId, token),
        // calcular el precio (RN-01 incluida), crear la reserva dentro de una
        // transacción (@Transactional) y, solo si Postgres la acepta, liberar
        // el lock con redisLockService.release(roomId). Si la restricción
        // EXCLUDE rechaza el insert, lanzar IllegalStateException (ya se
        // traduce a 409 vía ApiExceptionHandler).
        throw new UnsupportedOperationException("confirmBooking aún no implementado");
    }

    public void cancelBooking() {
        // RN-03 (política de cancelación, según el documento de requerimientos):
        //   +72h antes del check-in → 100% de reembolso
        //   24h-72h antes del check-in → 50% de reembolso
        //   -24h antes o no-show → 0% de reembolso
        // Pago está fuera de alcance en esta fase — se deja sin implementar
        // a propósito. TODO: implementar cuando se retome MercadoPago.
        throw new UnsupportedOperationException("cancelBooking aún no implementado");
    }
}