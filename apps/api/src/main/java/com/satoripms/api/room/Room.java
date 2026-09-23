package com.satoripms.api.room;

import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;

@Entity
@Table(name = "room")
@Data
public class Room {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String number;

    @Column(nullable = false)
    private String name;

    private String description;

    @Column(nullable = false)
    private String type;

    @Column(name = "base_adults_capacity", nullable = false)
    private Integer baseAdultsCapacity;

    @Column(name = "max_adults_capacity", nullable = false)
    private Integer maxAdultsCapacity;

    @Column(name = "children_capacity", nullable = false)
    private Integer childrenCapacity;

    @Column(name = "extra_guest_price", nullable = false)
    private BigDecimal extraGuestPrice;

    @Column(name = "allows_pets", nullable = false)
    private Boolean allowsPets;

    @Column(name = "price_per_night", nullable = false)
    private BigDecimal pricePerNight;

    @Column(nullable = false)
    private String status; // available | occupied | cleaning | maintenance

    @Column(nullable = false)
    private Boolean active;
}