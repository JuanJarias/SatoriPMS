package com.satoripms.api.auth;

import com.satoripms.api.security.JwtService;
import com.satoripms.api.security.Roles;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * Autenticación del personal del hotel (Administrador y Recepcionista).
 *
 * Valida las credenciales contra la tabla system_users (contraseñas BCrypt) y emite un JWT
 * que la aplicación web debe enviar en el encabezado {@code Authorization: Bearer <token>}.
 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private static final String INVALID_CREDENTIALS = "Usuario o contraseña no válidos";

    private final JdbcTemplate jdbcTemplate;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    /** Hash de referencia para igualar el tiempo de respuesta cuando el usuario no existe. */
    private final String dummyHash;

    public AuthController(JdbcTemplate jdbcTemplate, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.jdbcTemplate = jdbcTemplate;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
        this.dummyHash = passwordEncoder.encode("satori-usuario-inexistente");
    }

    public record LoginRequest(String username, String password) {}

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody(required = false) LoginRequest req) {
        if (req == null || req.username() == null || req.username().isBlank()
                || req.password() == null || req.password().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Usuario y contraseña son obligatorios"));
        }

        List<Map<String, Object>> users = jdbcTemplate.queryForList(
                "SELECT username, password_hash, role, name FROM system_users WHERE LOWER(username) = ? AND active = TRUE",
                req.username().trim().toLowerCase());
        if (users.isEmpty()) {
            // Se compara contra un hash ficticio para no revelar por tiempo de respuesta si el usuario existe.
            passwordEncoder.matches(req.password(), dummyHash);
            return unauthorized();
        }

        Map<String, Object> user = users.get(0);
        String hash = String.valueOf(user.get("password_hash"));
        String role = Roles.fromDatabaseRole(String.valueOf(user.get("role")));
        if (role == null || !passwordEncoder.matches(req.password(), hash)) {
            return unauthorized();
        }

        String username = String.valueOf(user.get("username"));
        String name = String.valueOf(user.get("name"));
        JwtService.IssuedToken token = jwtService.issue(username, name, role);
        return ResponseEntity.ok(Map.of(
                "token", token.value(),
                "tokenType", "Bearer",
                "expiresAt", token.expiresAt().toString(),
                "username", username,
                "name", name,
                "role", role.toLowerCase()
        ));
    }

    /** Datos de la sesión actual a partir del token. */
    @GetMapping("/me")
    public ResponseEntity<?> me(@AuthenticationPrincipal Jwt jwt) {
        if (jwt == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "Sesión no válida"));
        }
        List<String> roles = jwt.getClaimAsStringList("roles");
        return ResponseEntity.ok(Map.of(
                "username", jwt.getSubject(),
                "name", String.valueOf(jwt.getClaimAsString("name")),
                "role", roles == null || roles.isEmpty() ? "" : roles.get(0).toLowerCase(),
                "expiresAt", String.valueOf(jwt.getExpiresAt())
        ));
    }

    private ResponseEntity<?> unauthorized() {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", INVALID_CREDENTIALS));
    }
}
