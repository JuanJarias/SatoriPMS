package com.satoripms.api.security;

import com.nimbusds.jose.jwk.source.ImmutableSecret;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.core.DelegatingOAuth2TokenValidator;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.JwtValidators;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.oauth2.jwt.NimbusJwtEncoder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;
import org.springframework.security.oauth2.server.resource.authentication.JwtGrantedAuthoritiesConverter;
import org.springframework.security.oauth2.server.resource.web.authentication.BearerTokenAuthenticationFilter;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;

import static com.satoripms.api.security.Roles.ADMIN;
import static com.satoripms.api.security.Roles.RECEPTIONIST;
import static com.satoripms.api.security.Roles.SERVICE;

/**
 * Seguridad de la API.
 *
 * - Personal del hotel: JWT HS256 emitido por POST /api/auth/login (roles ADMIN / RECEPTIONIST).
 * - Chatbot (n8n): llave de servicio en el encabezado X-Service-Key (rol SERVICE).
 * - Sin sesión de servidor (stateless) y CORS restringido a los orígenes configurados.
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private static final int MIN_SECRET_BYTES = 32;

    @Value("${satori.jwt.secret}")
    private String jwtSecret;

    @Value("${satori.security.service-key:}")
    private String serviceKey;

    @Value("${satori.security.cors-allowed-origins:http://localhost:5173}")
    private String corsAllowedOrigins;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .addFilterBefore(new ServiceKeyAuthenticationFilter(serviceKey), BearerTokenAuthenticationFilter.class)
            .oauth2ResourceServer(oauth -> oauth
                .jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthenticationConverter()))
                .authenticationEntryPoint((req, res, ex) ->
                        SecurityErrorWriter.write(res, 401, "Autenticación requerida o token no válido"))
                .accessDeniedHandler((req, res, ex) ->
                        SecurityErrorWriter.write(res, 403, "No tiene permisos para esta operación")))
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint((req, res, e) ->
                        SecurityErrorWriter.write(res, 401, "Autenticación requerida o token no válido"))
                .accessDeniedHandler((req, res, e) ->
                        SecurityErrorWriter.write(res, 403, "No tiene permisos para esta operación")))
            .authorizeHttpRequests(auth -> auth
                // Públicos
                .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                .requestMatchers(HttpMethod.POST, "/api/auth/login").permitAll()
                .requestMatchers("/swagger-ui/**", "/swagger-ui.html", "/api-docs/**", "/v3/api-docs/**", "/error").permitAll()

                // Flujo de reservas: chatbot y personal del hotel
                .requestMatchers(HttpMethod.GET, "/api/rooms/availability").hasAnyRole(SERVICE, ADMIN, RECEPTIONIST)
                .requestMatchers(HttpMethod.POST, "/api/bookings/lock", "/api/bookings/unlock", "/api/bookings/confirm")
                    .hasAnyRole(SERVICE, ADMIN, RECEPTIONIST)
                .requestMatchers(HttpMethod.GET, "/api/bookings/group/*").hasAnyRole(SERVICE, ADMIN, RECEPTIONIST)
                .requestMatchers(HttpMethod.POST, "/api/bookings/group/*/cancellation", "/api/bookings/group/*/pay-remaining")
                    .hasAnyRole(SERVICE, ADMIN, RECEPTIONIST)
                .requestMatchers(HttpMethod.GET, "/api/bookings/debug").hasAnyRole(SERVICE, ADMIN, RECEPTIONIST)
                .requestMatchers(HttpMethod.GET, "/api/events/active").hasAnyRole(SERVICE, ADMIN, RECEPTIONIST)
                .requestMatchers(HttpMethod.POST, "/api/conversations/*/escalation", "/api/notifications/agent-request")
                    .hasAnyRole(SERVICE, ADMIN, RECEPTIONIST)

                // Conciliación de pagos externos: chatbot (webhook Wompi verificado) o administrador
                .requestMatchers(HttpMethod.POST, "/api/bookings/group/*/confirm-external-payment",
                        "/api/bookings/confirm-external-payment").hasAnyRole(SERVICE, ADMIN)

                // Solo administrador
                .requestMatchers(HttpMethod.POST, "/api/bookings/test-paid").hasRole(ADMIN)
                .requestMatchers(HttpMethod.POST, "/api/rooms").hasRole(ADMIN)
                .requestMatchers(HttpMethod.PUT, "/api/rooms/*").hasRole(ADMIN)
                .requestMatchers(HttpMethod.DELETE, "/api/rooms/*").hasRole(ADMIN)
                .requestMatchers(HttpMethod.POST, "/api/events").hasRole(ADMIN)
                .requestMatchers(HttpMethod.PUT, "/api/events/*").hasRole(ADMIN)
                .requestMatchers(HttpMethod.DELETE, "/api/events/*").hasRole(ADMIN)
                .requestMatchers(HttpMethod.POST, "/api/restaurant/menu").hasRole(ADMIN)
                .requestMatchers(HttpMethod.PUT, "/api/restaurant/menu/*").hasRole(ADMIN)
                .requestMatchers(HttpMethod.DELETE, "/api/restaurant/menu/*").hasRole(ADMIN)

                // Resto de la API: personal del hotel
                .requestMatchers("/api/**").hasAnyRole(ADMIN, RECEPTIONIST)
                .anyRequest().permitAll()
            );
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public JwtEncoder jwtEncoder() {
        return new NimbusJwtEncoder(new ImmutableSecret<>(secretKey()));
    }

    @Bean
    public JwtDecoder jwtDecoder() {
        NimbusJwtDecoder decoder = NimbusJwtDecoder.withSecretKey(secretKey())
                .macAlgorithm(MacAlgorithm.HS256)
                .build();
        decoder.setJwtValidator(new DelegatingOAuth2TokenValidator<>(
                JwtValidators.createDefaultWithIssuer(JwtService.ISSUER)));
        return decoder;
    }

    private JwtAuthenticationConverter jwtAuthenticationConverter() {
        JwtGrantedAuthoritiesConverter authorities = new JwtGrantedAuthoritiesConverter();
        authorities.setAuthoritiesClaimName("roles");
        authorities.setAuthorityPrefix("ROLE_");
        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(authorities);
        return converter;
    }

    private SecretKey secretKey() {
        byte[] bytes = jwtSecret == null ? new byte[0] : jwtSecret.getBytes(StandardCharsets.UTF_8);
        if (bytes.length < MIN_SECRET_BYTES) {
            throw new IllegalStateException("JWT_SECRET debe tener al menos " + MIN_SECRET_BYTES + " caracteres");
        }
        return new SecretKeySpec(bytes, "HmacSHA256");
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        List<String> origins = Arrays.stream(corsAllowedOrigins.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .toList();
        configuration.setAllowedOrigins(origins);
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"));
        configuration.setAllowedHeaders(List.of("Authorization", "Content-Type", "X-Guest-Document"));
        configuration.setAllowCredentials(false);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
