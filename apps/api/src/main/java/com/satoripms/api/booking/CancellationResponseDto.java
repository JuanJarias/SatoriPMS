package com.satoripms.api.booking;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CancellationResponseDto {
    private String code;
    private UUID reservationGroupId;
    private String status;
    private String paymentStatus;
    private BigDecimal totalPrice;
    private int refundPercentage;
    private BigDecimal refundAmount;
    private String policyDescription;
    private List<Long> cancelledBookingIds;
    private List<String> freedRoomNumbers;
    private LocalDateTime cancelledAt;
    private String message;
}

