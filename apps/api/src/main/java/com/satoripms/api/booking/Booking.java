package com.satoripms.api.booking;

import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entidad JPA representativa de una reserva de habitación en SatoriPMS.
 *
 * Mapea a la tabla `booking` en PostgreSQL, que cuenta con una restricción de exclusión
 * temporal `EXCLUDE USING gist (room_id WITH =, daterange(check_in, check_out, '[)') WITH &&)`
 * para garantizar a nivel de motor de base de datos la no concurrencia ni sobreventa.
 */
@Entity
@Table(name = "booking")
@Data
public class Booking {

    /** Identificador único autoincremental de la reserva */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Identificador del huésped titular */
    @Column(name = "guest_id", nullable = false)
    private Long guestId;

    /** Identificador de la habitación reservada */
    @Column(name = "room_id", nullable = false)
    private Long roomId;

    /** Fecha de check-in (llegada) */
    @Column(name = "check_in", nullable = false)
    private LocalDate checkIn;

    /** Fecha de check-out (salida) */
    @Column(name = "check_out", nullable = false)
    private LocalDate checkOut;

    /** Estado operativo: 'pending_payment', 'confirmed', 'finished', 'cancelled' */
    @Column(nullable = false)
    private String status;

    /** Estado del pago: 'pending', 'paid', 'refunded', 'partial' */
    @Column(name = "payment_status", nullable = false)
    private String paymentStatus;

    /** Cantidad de adultos */
    @Column(nullable = false)
    private Integer adults;

    /** Cantidad de niños */
    @Column(nullable = false)
    private Integer children;

    /** Indica si se hospeda con mascota */
    @Column(name = "with_pet", nullable = false)
    private Boolean withPet;

    /** Precio total imputado a esta habitación */
    @Column(name = "total_price", nullable = false)
    private BigDecimal totalPrice;

    /** Monto efectivamente abonado o pagado para esta habitación */
    @Column(name = "paid_amount", nullable = false)
    private BigDecimal paidAmount;

    /** Canal origen de la reserva: 'chatbot', 'web' */
    @Column(nullable = false)
    private String source;

    /** Token UUID de bloqueo en Redis con el que fue reservada */
    @Column(name = "lock_id")
    private String lockId;

    /** Identificador UUID de grupo para reservas multi-habitación */
    @Column(name = "reservation_group_id")
    private UUID reservationGroupId;

    /** Nombres de los acompañantes registrados */
    @Column(name = "companions")
    private String companions;

    /** Fecha y hora de creación del registro en base de datos */
    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;

    /** Fecha y hora de última actualización del registro */
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        LocalDateTime now = LocalDateTime.now();
        this.updatedAt = now;
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}