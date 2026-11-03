package com.satoripms.api.booking;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

/**
 * DTO que representa el resultado de la cancelación de una reserva grupal.
 * Contiene el desglose financiero, porcentaje y monto de reembolso según la política RN-03,
 * y la lista de habitaciones liberadas para nueva disponibilidad.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CancellationResponseDto {
    /** Código de reserva formateado (ej. 'RES-12' o prefijo UUID de 8 caracteres) */
    private String code;
    /** Identificador único del grupo de reservas cancelado */
    private UUID reservationGroupId;
    /** Estado final de la reserva ('cancelled') */
    private String status;
    /** Estado final del pago ('refunded', 'paid', 'pending') */
    private String paymentStatus;
    /** Precio total contratado de la reserva grupal */
    private BigDecimal totalPrice;
    /** Monto efectivamente abonado/pagado por el huésped */
    private BigDecimal paidAmount;
    /** Porcentaje de reembolso calculado según horas previas al check-in (100%, 50%, 0%) */
    private int refundPercentage;
    /** Monto monetario exacto a reembolsar al huésped */
    private BigDecimal refundAmount;
    /** Descripción textual explicativa de la regla de cancelación aplicada */
    private String policyDescription;
    /** Lista de identificadores individuales de reserva cancelados en base de datos */
    private List<Long> cancelledBookingIds;
    /** Números de habitación que quedaron inmediatamente liberadas */
    private List<String> freedRoomNumbers;
    /** Fecha y hora exacta de la cancelación */
    private LocalDateTime cancelledAt;
    /** Mensaje de confirmación para el usuario o chatbot */
    private String message;
}
