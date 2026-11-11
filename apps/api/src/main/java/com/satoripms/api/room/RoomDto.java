package com.satoripms.api.room;

import lombok.Data;
import java.math.BigDecimal;

@Data
public class RoomDto {
    private Long id;
    private String number;
    private String name;
    private String description;
    private String type;
    private Integer baseAdultsCapacity;
    private Integer maxAdultsCapacity;
    private Integer childrenCapacity;
    private BigDecimal extraGuestPrice;
    private Boolean allowsPets;
    private BigDecimal pricePerNight;
    private String status;
    private Boolean active;
}
