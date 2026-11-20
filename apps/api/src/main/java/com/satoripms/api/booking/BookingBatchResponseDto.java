package com.satoripms.api.booking;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

/**
 * Record DTO de respuesta para operaciones de confirmación o liquidación de reservas por lote.
 *
 * @param reservationGroupId Identificador único del grupo de habitaciones reservadas
 * @param totalPrice         Precio total acumulado de las habitaciones y recargos
 * @param bookingIds         Lista de identificadores de las reservas individuales generadas
 * @param roomIds            Lista de identificadores de las habitaciones reservadas
 * @param status             Estado operativo de la reserva ('confirmed', 'pending_payment', 'cancelled')
 * @param paymentStatus      Estado de pago ('paid', 'partial', 'pending')
 * @param paidAmount         Monto pagado o abonado hasta el momento
 * @param pendingBalance     Saldo pendiente por liquidar (totalPrice - paidAmount)
 * @param code               Código público de la reserva (ej. TS-7K4Q)
 */
public record BookingBatchResponseDto(
        UUID reservationGroupId,
        BigDecimal totalPrice,
        List<Long> bookingIds,
        List<Long> roomIds,
        String status,
        String paymentStatus,
        BigDecimal paidAmount,
        BigDecimal pendingBalance,
        String code) {
}
