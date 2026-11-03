package com.satoripms.api.booking;

import lombok.Data;
import java.time.LocalDate;

/**
 * DTO para la solicitud de bloqueo temporal de habitación antes de la confirmación de reserva.
 */
@Data
public class LockRequestDto {
    /** Identificador de WhatsApp del solicitante */
    private String waId;
    /** Identificador de la habitación deseada */
    private Long roomId;
    /** Fecha de check-in */
    private LocalDate checkIn;
    /** Fecha de check-out */
    private LocalDate checkOut;
}
