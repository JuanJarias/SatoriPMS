package com.satoripms.api.security;

import com.satoripms.api.booking.BookingController;
import com.satoripms.api.booking.BookingRepository;
import com.satoripms.api.booking.BookingService;
import com.satoripms.api.booking.ReservationDetailsDto;
import com.satoripms.api.guest.GuestRepository;
import com.satoripms.api.room.RoomRepository;
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
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = BookingController.class)
@Import({SecurityConfig.class, JwtService.class})
@TestPropertySource(properties = {
        "satori.security.service-key=test-service-key",
        "satori.jwt.secret=test-secret-key-de-al-menos-32-caracteres-123"
})
class SecurityRulesTest {

    private static final String SERVICE_KEY = "test-service-key";

    @Autowired
    private MockMvc mvc;

    @Autowired
    private JwtService jwtService;

    @MockBean
    private BookingService bookingService;
    @MockBean
    private RoomRepository roomRepository;
    @MockBean
    private GuestRepository guestRepository;
    @MockBean
    private BookingRepository bookingRepository;

    @Test
    void anonymousRequestsAreRejected() throws Exception {
        mvc.perform(get("/api/bookings/debug")).andExpect(status().isUnauthorized());
        mvc.perform(post("/api/bookings/group/TS-ABCD/cancellation")).andExpect(status().isUnauthorized());
    }

    @Test
    void wrongServiceKeyIsRejected() throws Exception {
        mvc.perform(get("/api/bookings/debug").header(ServiceKeyAuthenticationFilter.HEADER, "otra-llave"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void serviceKeyGrantsChatbotEndpoints() throws Exception {
        given(bookingRepository.findAllByOrderByCreatedAtDesc()).willReturn(List.of());
        mvc.perform(get("/api/bookings/debug").header(ServiceKeyAuthenticationFilter.HEADER, SERVICE_KEY))
                .andExpect(status().isOk());
    }

    @Test
    void chatbotMustSendHolderDocumentAndReceivesMaskedData() throws Exception {
        mvc.perform(get("/api/bookings/group/TS-ABCD").header(ServiceKeyAuthenticationFilter.HEADER, SERVICE_KEY))
                .andExpect(status().isBadRequest());

        given(bookingService.getReservationDetailsByCode(anyString(), anyString(), anyBoolean()))
                .willReturn(ReservationDetailsDto.builder().code("TS-ABCD").build());
        mvc.perform(get("/api/bookings/group/TS-ABCD")
                        .header(ServiceKeyAuthenticationFilter.HEADER, SERVICE_KEY)
                        .header("X-Guest-Document", "1234567"))
                .andExpect(status().isOk());
        verify(bookingService).getReservationDetailsByCode(eq("TS-ABCD"), eq("1234567"), eq(true));

        mvc.perform(post("/api/bookings/group/TS-ABCD/cancellation")
                        .header(ServiceKeyAuthenticationFilter.HEADER, SERVICE_KEY))
                .andExpect(status().isBadRequest());
    }

    @Test
    void staffCanQueryWithoutDocument() throws Exception {
        given(bookingService.getReservationDetailsByCode(anyString(), any(), anyBoolean()))
                .willReturn(ReservationDetailsDto.builder().code("TS-ABCD").build());
        mvc.perform(get("/api/bookings/group/TS-ABCD").header("Authorization", bearer(Roles.RECEPTIONIST)))
                .andExpect(status().isOk());
        verify(bookingService).getReservationDetailsByCode(eq("TS-ABCD"), eq(null), eq(false));
    }

    @Test
    void adminOnlyEndpointsRejectReceptionistAndService() throws Exception {
        mvc.perform(post("/api/bookings/test-paid").header("Authorization", bearer(Roles.RECEPTIONIST))
                        .contentType(MediaType.APPLICATION_JSON).content("{}"))
                .andExpect(status().isForbidden());
        mvc.perform(post("/api/bookings/test-paid").header(ServiceKeyAuthenticationFilter.HEADER, SERVICE_KEY)
                        .contentType(MediaType.APPLICATION_JSON).content("{}"))
                .andExpect(status().isForbidden());
    }

    @Test
    void forgedTokenIsRejected() throws Exception {
        String token = bearer(Roles.ADMIN);
        String tampered = token.substring(0, token.length() - 3) + "abc";
        mvc.perform(get("/api/bookings/debug").header("Authorization", tampered))
                .andExpect(status().isUnauthorized());
    }

    private String bearer(String role) {
        return "Bearer " + jwtService.issue("usuario.prueba", "Usuario Prueba", role).value();
    }
}
