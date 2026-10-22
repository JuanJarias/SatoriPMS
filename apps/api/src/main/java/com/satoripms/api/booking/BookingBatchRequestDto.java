package com.satoripms.api.booking;

import lombok.Data;
import java.time.LocalDate;
import java.util.List;

/**
 * DTO para la solicitud de confirmación de reserva por lote (una o varias habitaciones).
 * Soporta registro de datos de huésped, acompañantes, opción de pago y tokens de bloqueo de Redis.
 */
@Data
public class BookingBatchRequestDto {
    /** Número de teléfono o identificador de WhatsApp del huésped */
    private String waId;
    /** Nombre completo del titular de la reserva */
    private String guestName;
    /** Documento de identidad del titular (6 a 10 dígitos) */
    private String guestDocument;
    /** Nombres o lista de acompañantes registrados */
    private String companions;
    /** Fecha de check-in (llegada) */
    private LocalDate checkIn;
    /** Fecha de check-out (salida) */
    private LocalDate checkOut;
    /** Cantidad total de adultos */
    private Integer adults;
    /** Cantidad total de niños */
    private Integer children;
    /** Indica si viaja con mascota */
    private Boolean hasPet;
    /** Lista de habitaciones seleccionadas con sus respectivos tokens de bloqueo en Redis */
    private List<BookingRoomLockDto> rooms;
    /** Opción de pago: 'deposit' (abono del 50%) o 'full' (pago total del 100%) */
    private String paymentOption;
    /** Monto pagado especificado manualmente si aplica */
    private java.math.BigDecimal paidAmount;
}
