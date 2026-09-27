package com.satoripms.api.booking;

import lombok.Data;
import java.time.LocalDate;
import java.util.List;

@Data
public class BookingBatchRequestDto {
    private String waId;
    private String guestName;
    private String guestDocument;
    private String companions;
    private LocalDate checkIn;
    private LocalDate checkOut;
    private Integer adults;
    private Integer children;
    private Boolean hasPet;
    private List<BookingRoomLockDto> rooms;
}