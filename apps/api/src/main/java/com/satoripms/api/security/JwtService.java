package com.satoripms.api.security;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.JwsHeader;
import org.springframework.security.oauth2.jwt.JwtClaimsSet;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.JwtEncoderParameters;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;

/** Emite los tokens JWT (HS256) del personal del hotel. */
@Service
public class JwtService {

    public static final String ISSUER = "satoripms";

    private final JwtEncoder encoder;
    private final long expirationMs;

    public JwtService(JwtEncoder encoder, @Value("${satori.jwt.expiracion-ms:28800000}") long expirationMs) {
        this.encoder = encoder;
        this.expirationMs = expirationMs;
    }

    public IssuedToken issue(String username, String name, String role) {
        Instant now = Instant.now();
        Instant expiresAt = now.plusMillis(expirationMs);
        JwtClaimsSet claims = JwtClaimsSet.builder()
                .issuer(ISSUER)
                .subject(username)
                .issuedAt(now)
                .expiresAt(expiresAt)
                .claim("name", name == null ? username : name)
                .claim("roles", List.of(role))
                .build();
        String token = encoder.encode(JwtEncoderParameters.from(
                JwsHeader.with(MacAlgorithm.HS256).build(), claims)).getTokenValue();
        return new IssuedToken(token, expiresAt);
    }

    public record IssuedToken(String value, Instant expiresAt) {
    }
}
