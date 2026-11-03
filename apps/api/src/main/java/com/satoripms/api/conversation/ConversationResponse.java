package com.satoripms.api.conversation;

import java.math.BigDecimal;
import java.time.LocalDate;

// Nombres de campo alineados a lo que Conversations.tsx ya espera
// (whatsappPhone, quotedTotal, etc.), aunque en la entidad/columna real
// el precio se llama totalPrice/total_price — ver nota en Conversation.java.
public record ConversationResponse(
        Long id,
        String whatsappPhone,
        String status,
        String step,
        LocalDate checkIn,
        LocalDate checkOut,
        Long selectedRoomId,
        Integer adults,
        Integer children,
        Boolean withPet,
        BigDecimal quotedTotal
) {
    public static ConversationResponse from(Conversation c) {
        return new ConversationResponse(
                c.getId(),
                c.getGuest() != null ? c.getGuest().getWhatsappPhone() : null,
                c.getStatus(),
                c.getStep(),
                c.getCheckIn(),
                c.getCheckOut(),
                c.getSelectedRoomId(),
                c.getAdults(),
                c.getChildren(),
                c.getWithPet(),
                c.getTotalPrice()
        );
    }
}
