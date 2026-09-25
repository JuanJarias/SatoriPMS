package com.satoripms.api.booking;

import lombok.Data;
import java.time.LocalDate;

@Data
public class BookingRequestDto {
    private String waId;
    private Long roomId;
    private LocalDate checkIn;
    private LocalDate checkOut;
    private Integer adults;
    private Integer children;
    private Boolean hasPet;
    private String lockToken;
}
