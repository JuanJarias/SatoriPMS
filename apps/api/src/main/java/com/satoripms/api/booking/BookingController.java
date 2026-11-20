package com.satoripms.api.booking;

import com.satoripms.api.guest.Guest;
import com.satoripms.api.guest.GuestRepository;
import com.satoripms.api.room.Room;
import com.satoripms.api.room.RoomRepository;
import com.satoripms.api.security.Roles;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Controlador REST principal para el módulo de Reservas y Disponibilidad de SatoriPMS.
 * 
 * Gestiona el ciclo de vida completo de las reservas del hotel:
 * 1. Consulta de disponibilidad con filtros de fechas, capacidad y mascotas.
 * 2. Bloqueo temporal en Redis (anti-doble reserva con TTL de 15 minutos) y liberación inmediata.
 * 3. Confirmación atómica por lote con soporte de abono parcial (50%) o total (100%).
 * 4. Consulta de detalles de reserva por código público TS-XXXX o UUID (con verificación de documento para el chatbot).
 * 5. Liquidación de saldo restante para reservas parciales.
 * 6. Cancelación con cálculo de política de reembolso proporcional sobre lo pagado (RN-03).
 * 7. Vista administrativa de depuración en tiempo real.
 */
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

    /**
     * Consulta las habitaciones disponibles que cumplen los criterios de fechas y capacidad.
     * Valida que no tengan reservas confirmadas en PostgreSQL (restricción EXCLUDE)
     * ni bloqueos temporales activos en Redis (TTL 15 min).
     *
     * @param checkIn  Fecha de llegada (YYYY-MM-DD)
     * @param checkOut Fecha de salida (YYYY-MM-DD)
     * @param adults   Cantidad de adultos
     * @param children Cantidad de niños (por defecto 0)
     * @param pet      Indica si viaja con mascota (por defecto false)
     * @return Lista de habitaciones disponibles con tarifas y capacidades
     */
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

    /**
     * Genera un bloqueo temporal en memoria (Redis) con un TTL de 15 minutos (900s)
     * para una habitación seleccionada mientras el huésped completa sus datos o el pago.
     * Previene colisiones concurrentes antes de la persistencia definitiva (RN-02).
     *
     * @param request Datos de la habitación y fechas a bloquear
     * @return Token de bloqueo (UUID), tiempo de expiración y precio cotizado
     */
    @PostMapping("/bookings/lock")
    public ResponseEntity<?> lockRoom(@RequestBody LockRequestDto request) {
        try {
            String token = bookingService.createTemporaryLock(request.getRoomId(), request.getCheckIn(), request.getCheckOut());
            Room room = roomRepository.findById(request.getRoomId()).orElseThrow();
            BigDecimal totalPrice = bookingService.quoteRoomStay(room, request.getCheckIn(), request.getCheckOut());

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

    /**
     * Libera de forma inmediata uno o varios bloqueos temporales en memoria (Redis)
     * cuando el huésped cancela antes de pagar, reinicia su sesión en el chatbot
     * o la sesión se limpia por inactividad.
     *
     * @param body Objeto con un bloqueo individual ({roomId, lockToken}) o una lista ({locks: [...]})
     * @return Cantidad de bloqueos liberados
     */
    @PostMapping("/bookings/unlock")
    public ResponseEntity<?> unlockRooms(@RequestBody(required = false) Map<String, Object> body) {
        if (body == null || body.isEmpty()) {
            return ResponseEntity.ok(Map.of("released", 0));
        }
        List<BookingRoomLockDto> locksToRelease = new ArrayList<>();
        Object locksObj = body.get("locks");
        if (locksObj instanceof List<?> list) {
            for (Object item : list) {
                if (item instanceof Map<?, ?> map) {
                    Object rId = map.get("roomId");
                    Object token = map.get("lockToken");
                    if (rId != null && token != null) {
                        BookingRoomLockDto dto = new BookingRoomLockDto();
                        dto.setRoomId(Long.valueOf(String.valueOf(rId)));
                        dto.setLockToken(String.valueOf(token));
                        locksToRelease.add(dto);
                    }
                }
            }
        } else if (body.get("roomId") != null && body.get("lockToken") != null) {
            BookingRoomLockDto dto = new BookingRoomLockDto();
            dto.setRoomId(Long.valueOf(String.valueOf(body.get("roomId"))));
            dto.setLockToken(String.valueOf(body.get("lockToken")));
            locksToRelease.add(dto);
        }
        int released = bookingService.releaseTemporaryLocks(locksToRelease);
        return ResponseEntity.ok(Map.of("released", released));
    }

    /**
     * Endpoint de confirmación batch principal para el Chatbot de WhatsApp y la Web.
     * Crea las reservas en PostgreSQL agrupadas bajo un único reservationGroupId,
     * libera los bloqueos temporales de Redis y persiste la modalidad de pago elegida:
     * - paymentOption = "deposit": Estado confirmed, payment_status partial, paid_amount = 50%.
     * - paymentOption = "full": Estado confirmed, payment_status paid, paid_amount = 100%.
     *
     * @param request DTO con datos del huésped, acompañantes, habitaciones con lockTokens y modalidad de pago
     * @return DTO de respuesta con reservationGroupId, IDs creados, total, abonado y saldo pendiente
     */
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

    /**
     * Endpoint de confirmación inmediata con pago completo simulado para entornos de prueba.
     * Solo disponible cuando 'satori.booking.test-payment-enabled' es true.
     *
     * @param request DTO con datos de reserva batch
     * @return DTO de respuesta con estado confirmado y pagado
     */
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

    /**
     * Consulta la información completa de una reserva por su código público exacto (TS-XXXX)
     * o el UUID del grupo. Incluye habitaciones, huésped, total, monto pagado, saldo pendiente
     * y política de cancelación (RN-03).
     *
     * Cuando llama el chatbot (rol SERVICE) es obligatorio el encabezado X-Guest-Document con el
     * documento del titular; si no coincide se responde 404 como si la reserva no existiera, y el
     * documento se devuelve enmascarado. El personal del hotel no necesita el documento.
     *
     * @param code     Código público o UUID de la reserva
     * @param document Documento del titular (obligatorio para el chatbot)
     * @return DTO con todos los detalles de la reserva y elegibilidad de acciones
     */
    @GetMapping("/bookings/group/{code}")
    public ResponseEntity<?> getReservationDetails(
            @PathVariable String code,
            @RequestHeader(value = "X-Guest-Document", required = false) String document) {
        try {
            boolean isService = Roles.currentCallerIsService();
            return ResponseEntity.ok(bookingService.getReservationDetailsByCode(
                    code, requiredDocumentFor(isService, document), isService));
        } catch (java.util.NoSuchElementException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", e.getMessage()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Cancela todas las habitaciones asociadas a un código de reserva de grupo.
     * Calcula la devolución proporcional basada estrictamente en lo abonado (paid_amount)
     * según la anticipación respecto a la hora de check-in (RN-03):
     * - > 72h: Reembolso del 100% de lo pagado.
     * - 24h a 72h: Reembolso del 50% de lo pagado.
     * - < 24h o no-show: 0% de reembolso.
     * Libera de inmediato las fechas en PostgreSQL al cambiar el estado a 'cancelled'.
     *
     * Cuando llama el chatbot (rol SERVICE) el cuerpo debe incluir {"document": "..."} con el
     * documento del titular.
     *
     * @param code Código de la reserva de grupo
     * @param body Cuerpo opcional con el documento del titular
     * @return DTO de cancelación con porcentaje y monto devuelto estimado
     */
    @PostMapping("/bookings/group/{code}/cancellation")
    public ResponseEntity<?> cancelReservationGroup(@PathVariable String code,
                                                    @RequestBody(required = false) GuestVerificationDto body) {
        try {
            return ResponseEntity.ok(bookingService.cancelReservationGroupByCode(
                    code, requiredDocumentFor(Roles.currentCallerIsService(), body == null ? null : body.document())));
        } catch (java.util.NoSuchElementException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", e.getMessage()));
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", e.getMessage()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Liquida el saldo pendiente de una reserva que fue abonada parcialmente al 50%.
     * Actualiza payment_status a 'paid', paid_amount al valor total de la estancia
     * y fija el saldo pendiente en $0.00.
     *
     * Cuando llama el chatbot (rol SERVICE) el cuerpo debe incluir {"document": "..."} con el
     * documento del titular.
     *
     * @param code Código de la reserva de grupo
     * @param body Cuerpo opcional con el documento del titular
     * @return DTO de respuesta con la reserva completamente pagada
     */
    @PostMapping("/bookings/group/{code}/pay-remaining")
    public ResponseEntity<?> payRemainingBalance(@PathVariable String code,
                                                 @RequestBody(required = false) GuestVerificationDto body) {
        try {
            return ResponseEntity.ok(bookingService.payRemainingBalance(
                    code, requiredDocumentFor(Roles.currentCallerIsService(), body == null ? null : body.document())));
        } catch (java.util.NoSuchElementException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", e.getMessage()));
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", e.getMessage()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Endpoint para conciliación y confirmación asíncrona de pagos externos (ej. Webhook de Wompi).
     * Transiciona la reserva de 'pending_payment' a 'confirmed' y registra el abono parcial (50%)
     * o total (100%) en la base de datos de PostgreSQL.
     *
     * @param code Código de la reserva de grupo (TS-XXXX) o UUID
     * @param confirmation DTO con los detalles del pago reportado por la pasarela
     * @return DTO de respuesta con la reserva confirmada y su nuevo estado de pago
     */
    @PostMapping("/bookings/group/{code}/confirm-external-payment")
    public ResponseEntity<?> confirmExternalPaymentByGroupCode(
            @PathVariable String code,
            @RequestBody(required = false) ExternalPaymentConfirmationDto confirmation) {
        try {
            return ResponseEntity.ok(bookingService.confirmExternalPayment(code, confirmation));
        } catch (java.util.NoSuchElementException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", e.getMessage()));
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", e.getMessage()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Variante del endpoint de confirmación de pago externo que recibe el código en el cuerpo JSON.
     * Facilita la invocación directa desde webhooks o microservicios de conciliación.
     *
     * @param confirmation DTO con el código de reserva y datos del pago
     * @return DTO de respuesta con la reserva confirmada y conciliada
     */
    @PostMapping("/bookings/confirm-external-payment")
    public ResponseEntity<?> confirmExternalPayment(
            @RequestBody ExternalPaymentConfirmationDto confirmation) {
        if (confirmation == null || confirmation.getReservationCode() == null || confirmation.getReservationCode().isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("error", "El campo reservationCode es obligatorio"));
        }
        try {
            return ResponseEntity.ok(bookingService.confirmExternalPayment(confirmation.getReservationCode(), confirmation));
        } catch (java.util.NoSuchElementException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", e.getMessage()));
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", e.getMessage()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Endpoint de auditoría y depuración en tiempo real.
     * Retorna todas las reservas del sistema con metadatos del huésped y de la habitación.
     * Es consumido por el panel web 'ReservasDebug.tsx' para monitoreo administrativo.
     *
     * @return Lista detallada de todas las reservas ordenadas descendentemente por fecha de creación
     */
    @GetMapping("/bookings/debug")
    public ResponseEntity<List<Map<String, Object>>> listDebugBookings() {
        List<Map<String, Object>> rows = new ArrayList<>();

        for (Booking booking : bookingRepository.findAllByOrderByCreatedAtDesc()) {
            Guest guest = guestRepository.findById(booking.getGuestId()).orElse(null);
            Room room = roomRepository.findById(booking.getRoomId()).orElse(null);

            Map<String, Object> row = new HashMap<>();
            row.put("id", booking.getId());
            row.put("reservationGroupId", booking.getReservationGroupId());

            row.put("bookingCode", booking.getBookingCode());

            row.put("status", booking.getStatus());
            row.put("paymentStatus", booking.getPaymentStatus());
            row.put("paidAmount", booking.getPaidAmount());
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

    /**
     * Documento a verificar: obligatorio para el chatbot; el personal del hotel puede omitirlo
     * (se verifica solo si lo envía).
     */
    private static String requiredDocumentFor(boolean isService, String document) {
        boolean missing = document == null || document.isBlank();
        if (isService && missing) {
            throw new IllegalArgumentException("El documento del titular es obligatorio");
        }
        return missing ? null : document;
    }

    /** Cuerpo con el documento del titular para operaciones sobre una reserva existente. */
    public record GuestVerificationDto(String document) {
    }
}
