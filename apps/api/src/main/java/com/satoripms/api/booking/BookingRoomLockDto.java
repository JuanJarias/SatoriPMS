package com.satoripms.api.booking;

import lombok.Data;

@Data
public class BookingRoomLockDto {
    private Long roomId;
    private String lockToken;
}