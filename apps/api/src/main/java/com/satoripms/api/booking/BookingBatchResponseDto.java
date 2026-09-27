package com.satoripms.api.booking;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

public record BookingBatchResponseDto(
        UUID reservationGroupId,
        BigDecimal totalPrice,
        List<Long> bookingIds,
        List<Long> roomIds,
        String status,
        String paymentStatus) {
}