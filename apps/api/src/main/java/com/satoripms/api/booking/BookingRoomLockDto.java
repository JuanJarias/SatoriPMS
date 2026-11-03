package com.satoripms.api.booking;

import lombok.Data;

/**
 * DTO que representa la asociación de una habitación con su respectivo token de bloqueo temporal en Redis.
 */
@Data
public class BookingRoomLockDto {
    /** Identificador de la habitación bloqueada */
    private Long roomId;
    /** Token UUID emitido por Redis al adquirir el bloqueo */
    private String lockToken;
}
