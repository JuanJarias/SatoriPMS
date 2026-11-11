package com.satoripms.api.restaurant;

import lombok.Data;
import java.math.BigDecimal;
import java.util.List;

@Data
public class RestaurantOrderDto {
    private Long bookingId;
    private Long roomId;
    private String customerName;
    private String destination; // room | counter | mirador | table
    private String paymentStatus; // paid | charged_to_room | pending
    private String paymentMethod; // cash | card | transfer | room_charge
    private String notes;
    private List<OrderItemDto> items;

    @Data
    public static class OrderItemDto {
        private Long menuItemId;
        private String itemName;
        private BigDecimal unitPrice;
        private Integer quantity;
    }
}
