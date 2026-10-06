package com.satoripms.api.booking;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReservationDetailsDto {
    private String code;
    private UUID reservationGroupId;
    private String guestName;
    private String guestPhone;
    private String guestDocument;
    private LocalDate checkIn;
    private LocalDate checkOut;
    private long nights;
    private Integer adults;
    private Integer children;
    private String companions;
    private Boolean withPet;
    private BigDecimal totalPrice;
    private String status;
    private String statusLabel;
    private String paymentStatus;
    private String paymentStatusLabel;
    private List<RoomSummaryDto> rooms;
    private boolean canCancel;
    private RefundPolicyDto refundPolicy;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RoomSummaryDto {
        private Long id;
        private String number;
        private String name;
        private String type;
        private BigDecimal pricePerNight;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RefundPolicyDto {
        private long hoursUntilCheckin;
        private int refundPercentage;
        private BigDecimal estimatedRefund;
        private String policyDescription;
    }
}

