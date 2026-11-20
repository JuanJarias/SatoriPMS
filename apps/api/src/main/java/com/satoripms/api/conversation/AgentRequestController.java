package com.satoripms.api.conversation;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * Recibe el aviso del chatbot cuando un huésped pide hablar con una persona de recepción.
 *
 * Marca como escalada la conversación en curso de ese número, para que la bandeja de
 * conversaciones de la aplicación web la muestre como pendiente de atención humana.
 */
@RestController
@RequestMapping("/api/notifications")
public class AgentRequestController {

    private static final Logger log = LoggerFactory.getLogger(AgentRequestController.class);

    private final ConversationRepository conversationRepository;

    public AgentRequestController(ConversationRepository conversationRepository) {
        this.conversationRepository = conversationRepository;
    }

    /** Cuerpo enviado por n8n: número de WhatsApp, nombre del perfil y contexto libre. */
    public record AgentRequestDto(@NotBlank String wa_id, String name, String context) {}

    @PostMapping("/agent-request")
    @Transactional
    public ResponseEntity<Map<String, Object>> agentRequest(@Valid @RequestBody AgentRequestDto request) {
        var open = conversationRepository.findOpenByWhatsappPhone(request.wa_id());
        boolean marked = false;
        if (!open.isEmpty()) {
            Conversation conversation = open.get(0);
            conversation.setStatus("escalated");
            conversation.setUpdatedAt(LocalDateTime.now());
            conversationRepository.save(conversation);
            marked = true;
        }
        log.info("Solicitud de agente humano recibida (conversación marcada: {})", marked);
        return ResponseEntity.accepted().body(Map.of("received", true, "conversationEscalated", marked));
    }
}
