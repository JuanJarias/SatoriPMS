package com.satoripms.api.security;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

/**
 * Roles reconocidos por la API.
 *
 * - ADMIN y RECEPTIONIST: personal del hotel autenticado con JWT (tabla system_users).
 * - SERVICE: el orquestador del chatbot (n8n), autenticado con la llave X-Service-Key.
 */
public final class Roles {

    public static final String ADMIN = "ADMIN";
    public static final String RECEPTIONIST = "RECEPTIONIST";
    public static final String SERVICE = "SERVICE";

    private Roles() {
    }

    /** Convierte el rol guardado en system_users ('admin', 'receptionist') al rol de la API. */
    public static String fromDatabaseRole(String dbRole) {
        if (dbRole == null) {
            return null;
        }
        return switch (dbRole.trim().toLowerCase()) {
            case "admin" -> ADMIN;
            case "receptionist" -> RECEPTIONIST;
            default -> null;
        };
    }

    /** true si la petición actual viene del orquestador del chatbot (llave de servicio). */
    public static boolean currentCallerIsService() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return auth != null && auth.getAuthorities().stream()
                .anyMatch(a -> ("ROLE_" + SERVICE).equals(a.getAuthority()));
    }
}
