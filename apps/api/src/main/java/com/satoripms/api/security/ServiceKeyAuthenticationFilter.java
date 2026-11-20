package com.satoripms.api.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.List;

/**
 * Autentica al orquestador del chatbot (n8n) mediante el encabezado {@code X-Service-Key}.
 *
 * - Sin encabezado: la petición sigue su curso (puede autenticarse con JWT).
 * - Encabezado con la llave correcta: se autentica con el rol SERVICE.
 * - Encabezado con llave incorrecta, o llave no configurada en el servidor: 401.
 *
 * No se registra como bean para que Spring Boot no lo agregue además a la cadena de servlets.
 */
public class ServiceKeyAuthenticationFilter extends OncePerRequestFilter {

    public static final String HEADER = "X-Service-Key";

    private final byte[] expectedKey;

    public ServiceKeyAuthenticationFilter(String serviceKey) {
        this.expectedKey = serviceKey == null ? new byte[0] : serviceKey.trim().getBytes(StandardCharsets.UTF_8);
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String provided = request.getHeader(HEADER);
        if (provided == null) {
            chain.doFilter(request, response);
            return;
        }
        byte[] providedBytes = provided.trim().getBytes(StandardCharsets.UTF_8);
        if (expectedKey.length == 0 || !MessageDigest.isEqual(expectedKey, providedBytes)) {
            SecurityErrorWriter.write(response, HttpServletResponse.SC_UNAUTHORIZED, "Llave de servicio no válida");
            return;
        }
        UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
                "chatbot-n8n", null, List.of(new SimpleGrantedAuthority("ROLE_" + Roles.SERVICE)));
        SecurityContextHolder.getContext().setAuthentication(auth);
        chain.doFilter(request, response);
    }
}
