package com.satoripms.api.booking;

import lombok.Data;
import java.time.LocalDate;

@Data
public class LockRequestDto {
    private String waId;
    private Long roomId;
    private LocalDate checkIn;
    private LocalDate checkOut;
}
