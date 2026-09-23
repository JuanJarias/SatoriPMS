package com.satoripms.api.conversation;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface ConversationRepository extends JpaRepository<Conversation, Long> {

    @Query("SELECT c FROM Conversation c JOIN FETCH c.guest ORDER BY c.updatedAt DESC")
    List<Conversation> findAllWithGuestOrderByUpdatedAtDesc();

    // Al ser el whatsapp_phone único por conversación activa (índice
    // uq_active_conversation_guest en el schema), esto sirve para que n8n
    // recupere el estado en curso de un número dado.
    @Query("SELECT c FROM Conversation c JOIN FETCH c.guest " +
           "WHERE c.guest.whatsappPhone = :phone AND c.status = 'active'")
    Optional<Conversation> findActiveByWhatsappPhone(@Param("phone") String phone);
}
