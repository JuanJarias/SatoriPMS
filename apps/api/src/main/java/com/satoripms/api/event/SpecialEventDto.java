package com.satoripms.api.event;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;

@Data
public class SpecialEventDto {
    private Long id;
    private String name;
    private String description;
    private LocalDate startDate;
    private LocalDate endDate;
    private BigDecimal discountPercentage;
    private BigDecimal surchargePercentage;
    private Boolean isActive;
    private String createdBy;
}
