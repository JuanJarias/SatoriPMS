package com.satoripms.api.conversation;

import com.satoripms.api.guest.Guest;
import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "conversation")
@Data
public class Conversation {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "guest_id", nullable = false)
    private Guest guest;

    @Column(nullable = false)
    private String status; // active | escalated | cancelled | completed | expired

    @Column(nullable = false)
    private String step; // welcome | dates | room_selection | occupancy | pet | review

    @Column(name = "check_in")
    private LocalDate checkIn;

    @Column(name = "check_out")
    private LocalDate checkOut;

    @Column(name = "selected_room_id")
    private Long selectedRoomId;

    private Integer adults;

    @Column(nullable = false)
    private Integer children;

    @Column(name = "with_pet")
    private Boolean withPet;

    // Nota: la sección 7 del contexto describe esta columna como "quoted_total"
    // en la prosa, pero la migración V1 realmente aplicada (documento del schema)
    // la creó como total_price. Sigo el SQL real, que es la fuente de verdad.
    @Column(name = "total_price")
    private BigDecimal totalPrice;

    @Column(name = "lock_token")
    private String lockToken;

    @Column(name = "lock_expires_at")
    private LocalDateTime lockExpiresAt;

    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
