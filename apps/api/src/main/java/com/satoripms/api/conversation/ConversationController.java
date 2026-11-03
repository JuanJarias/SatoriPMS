package com.satoripms.api.conversation;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Controlador REST para el monitoreo y gestión de conversaciones de soporte del chatbot.
 *
 * Proporciona endpoints para que el panel administrativo de la aplicación web visualice
 * los chats en curso y gestione la escalada a agentes humanos.
 */
@RestController
@RequestMapping("/api/conversations")
public class ConversationController {

    private final ConversationRepository conversationRepository;

    /**
     * Constructor con inyección del repositorio de conversaciones.
     *
     * @param conversationRepository Repositorio JPA de conversaciones
     */
    public ConversationController(ConversationRepository conversationRepository) {
        this.conversationRepository = conversationRepository;
    }

    /**
     * Obtiene el listado de conversaciones activas e históricas con sus huéspedes asociados,
     * ordenadas por la fecha de última interacción.
     *
     * @return Lista de conversaciones formateadas para la vista de bandeja de entrada
     */
    @GetMapping
    public ResponseEntity<List<ConversationResponse>> getConversations() {
        List<ConversationResponse> response = conversationRepository
                .findAllWithGuestOrderByUpdatedAtDesc()
                .stream()
                .map(ConversationResponse::from)
                .toList();
        return ResponseEntity.ok(response);
    }

    /**
     * Registra la solicitud de escalamiento de una conversación para atención humana.
     *
     * @param id Identificador de la conversación
     * @return Respuesta HTTP 200 confirmando la solicitud de escalada
     */
    @PostMapping("/{id}/escalation")
    public ResponseEntity<?> escalateToHuman(@PathVariable Long id) {
        // En un paso posterior se notificará a los recepcionistas vía WebSocket (STOMP).
        return ResponseEntity.ok().build();
    }
}
