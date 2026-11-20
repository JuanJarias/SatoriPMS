package com.satoripms.api.conversation;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface ConversationRepository extends JpaRepository<Conversation, Long> {

    @Query("SELECT c FROM Conversation c JOIN FETCH c.guest ORDER BY c.updatedAt DESC")
    List<Conversation> findAllWithGuestOrderByUpdatedAtDesc();

    // Conversación en curso (activa o ya escalada) de un número de WhatsApp.
    @Query("SELECT c FROM Conversation c JOIN FETCH c.guest g " +
           "WHERE g.whatsappPhone = :phone AND c.status IN ('active', 'escalated') " +
           "ORDER BY c.updatedAt DESC")
    List<Conversation> findOpenByWhatsappPhone(@org.springframework.data.repository.query.Param("phone") String phone);
}
