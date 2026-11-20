package com.satoripms.api.security;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * Crea un administrador inicial al arrancar si se definen SATORI_ADMIN_USERNAME y
 * SATORI_ADMIN_PASSWORD y ese usuario todavía no existe. Nunca modifica usuarios existentes.
 */
@Component
public class AdminBootstrap implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(AdminBootstrap.class);
    private static final int MIN_PASSWORD_LENGTH = 8;

    private final JdbcTemplate jdbcTemplate;
    private final PasswordEncoder passwordEncoder;
    private final String username;
    private final String password;
    private final String name;

    public AdminBootstrap(JdbcTemplate jdbcTemplate,
                          PasswordEncoder passwordEncoder,
                          @Value("${satori.bootstrap.admin-username:}") String username,
                          @Value("${satori.bootstrap.admin-password:}") String password,
                          @Value("${satori.bootstrap.admin-name:Administrador}") String name) {
        this.jdbcTemplate = jdbcTemplate;
        this.passwordEncoder = passwordEncoder;
        this.username = username == null ? "" : username.trim().toLowerCase();
        this.password = password == null ? "" : password;
        this.name = name;
    }

    @Override
    public void run(ApplicationArguments args) {
        if (username.isEmpty() || password.isEmpty()) {
            return;
        }
        if (password.length() < MIN_PASSWORD_LENGTH) {
            log.warn("SATORI_ADMIN_PASSWORD debe tener al menos {} caracteres; no se creó el administrador inicial.",
                    MIN_PASSWORD_LENGTH);
            return;
        }
        Integer existing = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM system_users WHERE LOWER(username) = ?", Integer.class, username);
        if (existing != null && existing > 0) {
            return;
        }
        jdbcTemplate.update(
                "INSERT INTO system_users (username, password_hash, role, name, active) VALUES (?, ?, 'admin', ?, TRUE)",
                username, passwordEncoder.encode(password), name);
        log.info("Administrador inicial '{}' creado.", username);
    }
}
