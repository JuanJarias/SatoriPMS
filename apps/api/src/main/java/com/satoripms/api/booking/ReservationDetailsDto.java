package com.satoripms.api.booking;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

/**
 * DTO detallado que representa el estado y desglose completo de una reserva para visualización
 * en el chatbot de WhatsApp y en el panel de administración.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReservationDetailsDto {
    /** Código de reserva formateado (ej. 'RES-12' o prefijo UUID de 8 caracteres) */
    private String code;
    /** Identificador UUID del grupo de reservas */
    private UUID reservationGroupId;
    /** Nombre del huésped titular */
    private String guestName;
    /** Teléfono celular / WhatsApp del titular */
    private String guestPhone;
    /** Documento de identidad del titular */
    private String guestDocument;
    /** Fecha de check-in */
    private LocalDate checkIn;
    /** Fecha de check-out */
    private LocalDate checkOut;
    /** Cantidad total de noches de estadía */
    private long nights;
    /** Cantidad de adultos */
    private Integer adults;
    /** Cantidad de niños */
    private Integer children;
    /** Nombres de acompañantes registrados */
    private String companions;
    /** Indica si viaja con mascota */
    private Boolean withPet;
    /** Valor total del hospedaje */
    private BigDecimal totalPrice;
    /** Monto pagado o abonado hasta la fecha */
    private BigDecimal paidAmount;
    /** Saldo pendiente por pagar */
    private BigDecimal pendingBalance;
    /** Estado operativo ('confirmed', 'pending_payment', 'cancelled') */
    private String status;
    /** Etiqueta amigable en español del estado operativo */
    private String statusLabel;
    /** Estado financiero del pago ('paid', 'partial', 'pending', 'refunded') */
    private String paymentStatus;
    /** Etiqueta amigable en español del estado de pago */
    private String paymentStatusLabel;
    /** Resumen de habitaciones incluidas en la reserva */
    private List<RoomSummaryDto> rooms;
    /** Indica si la reserva cumple las condiciones para ser cancelada */
    private boolean canCancel;
    /** Indica si la reserva tiene saldo pendiente y puede ser pagada */
    private boolean canPayRemaining;
    /** Desglose de la política de reembolso aplicable en tiempo real (RN-03) */
    private RefundPolicyDto refundPolicy;

    /**
     * Resumen de una habitación reservada dentro del grupo.
     */
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

    /**
     * Detalle de la estimación de reembolso en caso de cancelación.
     */
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
