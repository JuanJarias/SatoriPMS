package com.satoripms.api.security;

import com.satoripms.api.conversation.AgentRequestController;
import com.satoripms.api.conversation.Conversation;
import com.satoripms.api.conversation.ConversationRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = AgentRequestController.class)
@Import({SecurityConfig.class, JwtService.class})
@TestPropertySource(properties = {
        "satori.security.service-key=test-service-key",
        "satori.jwt.secret=test-secret-key-de-al-menos-32-caracteres-123"
})
class AgentRequestSecurityTest {

    private static final String BODY = "{\"wa_id\":\"573001112233\",\"name\":\"Ana\",\"context\":\"prueba\"}";

    @Autowired
    private MockMvc mvc;

    @MockBean
    private ConversationRepository conversationRepository;

    @Test
    void anonymousRequestIsRejected() throws Exception {
        mvc.perform(post("/api/notifications/agent-request").contentType(MediaType.APPLICATION_JSON).content(BODY))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void chatbotMarksOpenConversationAsEscalated() throws Exception {
        Conversation conversation = new Conversation();
        conversation.setStatus("active");
        given(conversationRepository.findOpenByWhatsappPhone("573001112233")).willReturn(List.of(conversation));

        mvc.perform(post("/api/notifications/agent-request")
                        .header(ServiceKeyAuthenticationFilter.HEADER, "test-service-key")
                        .contentType(MediaType.APPLICATION_JSON).content(BODY))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.conversationEscalated").value(true));
        verify(conversationRepository).save(any(Conversation.class));
    }

    @Test
    void missingPhoneIsRejected() throws Exception {
        mvc.perform(post("/api/notifications/agent-request")
                        .header(ServiceKeyAuthenticationFilter.HEADER, "test-service-key")
                        .contentType(MediaType.APPLICATION_JSON).content("{\"name\":\"Ana\"}"))
                .andExpect(status().isBadRequest());
    }
}
