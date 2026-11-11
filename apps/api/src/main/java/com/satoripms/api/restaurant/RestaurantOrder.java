package com.satoripms.api.restaurant;

import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "restaurant_orders")
@Data
public class RestaurantOrder {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "order_code", nullable = false, unique = true)
    private String orderCode;

    @Column(name = "booking_id")
    private Long bookingId;

    @Column(name = "room_id")
    private Long roomId;

    @Column(name = "customer_name", nullable = false)
    private String customerName;

    @Column(nullable = false)
    private String destination = "room"; // room | counter | mirador | table

    @Column(name = "total_amount", nullable = false)
    private BigDecimal totalAmount = BigDecimal.ZERO;

    @Column(name = "payment_status", nullable = false)
    private String paymentStatus = "charged_to_room"; // paid | charged_to_room | pending | cancelled

    @Column(name = "payment_method")
    private String paymentMethod = "room_charge"; // cash | card | transfer | room_charge

    private String notes;

    @Column(name = "created_by")
    private String createdBy = "recepcion@torresatori.co";

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt = LocalDateTime.now();

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<RestaurantOrderItem> items = new ArrayList<>();

    @PreUpdate
    public void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
