package com.satoripms.api.booking;

import lombok.Data;
import java.math.BigDecimal;

/**
 * DTO para la confirmación asíncrona de pagos externos (ej. pasarela Wompi vía webhook).
 */
@Data
public class ExternalPaymentConfirmationDto {
    /** Código de reserva (ej. TS-4156) o identificador de grupo (UUID) */
    private String reservationCode;
    /** Identificador de la transacción externa en la pasarela (ej. id de Wompi) */
    private String transactionId;
    /** Modalidad de pago: 'deposit' (50%), 'full' (100%) o 'remaining' */
    private String paymentOption;
    /** Monto pagado reportado por la pasarela en pesos colombianos (COP) */
    private BigDecimal amount;
    /** Método de pago utilizado (ej. CARD, NEQUI, PSE, BANCOLOMBIA_TRANSFER) */
    private String paymentMethod;
    /** Estado reportado por la pasarela (ej. APPROVED, DECLINED) */
    private String status;
}
