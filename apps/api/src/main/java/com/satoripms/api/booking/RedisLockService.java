package com.satoripms.api.booking;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

/**
 * Servicio de gestión de bloqueos temporales concurrentes utilizando Redis y scripts atómicos en Lua.
 *
 * Implementa la regla de negocio anti-doble reserva (RN-02): cuando un usuario inicia el proceso
 * de selección de habitación, se genera un bloqueo de 15 minutos en memoria para evitar que
 * otros huéspedes concurrentes reserven la misma habitación en fechas solapadas.
 */
@Service
public class RedisLockService {

    private final StringRedisTemplate redisTemplate;
    private final long lockTtlSeconds;

    /**
     * Constructor con inyección del template de Redis y TTL configurable.
     *
     * @param redisTemplate  Template de operaciones Redis en formato String
     * @param lockTtlSeconds Tiempo de vida del bloqueo en segundos (por defecto 900s = 15 minutos)
     */
    public RedisLockService(StringRedisTemplate redisTemplate,
                            @Value("${satori.redis.bloqueo-ttl-segundos:900}") long lockTtlSeconds) {
        this.redisTemplate = redisTemplate;
        this.lockTtlSeconds = lockTtlSeconds;
    }

    private String buildIntervalsKey(Long roomId) {
        return "lock:room:%d:intervals".formatted(roomId);
    }

    private String buildMetadataPrefix(Long roomId) {
        return "lock:room:%d:metadata:".formatted(roomId);
    }

    /**
     * Intenta adquirir un bloqueo atómico sobre una habitación para un rango de fechas dado.
     * Ejecuta un script Lua en Redis que limpia tokens expirados y valida si el nuevo rango
     * se solapa con algún intervalo previamente bloqueado.
     *
     * @param roomId   Identificador de la habitación
     * @param checkIn  Fecha de llegada
     * @param checkOut Fecha de salida
     * @param token    Token UUID único identificador del bloqueo del usuario
     * @return true si el bloqueo fue adquirido exitosamente, false si hay solapamiento
     */
    public boolean tryLock(Long roomId, LocalDate checkIn, LocalDate checkOut, String token) {
        DefaultRedisScript<Long> script = new DefaultRedisScript<>(
            "local members = redis.call('zrange', KEYS[1], 0, -1) "
                + "for _, existingToken in ipairs(members) do "
                + "local metadataKey = KEYS[2] .. existingToken "
                + "local existing = redis.call('hmget', metadataKey, 'checkIn', 'checkOut') "
                + "if not existing[1] or not existing[2] then "
                + "redis.call('zrem', KEYS[1], existingToken) "
                + "elseif tonumber(existing[2]) > tonumber(ARGV[3]) "
                + "and tonumber(existing[1]) < tonumber(ARGV[4]) then "
                + "return 0 end end "
                + "redis.call('zadd', KEYS[1], ARGV[3], ARGV[1]) "
                + "redis.call('hset', KEYS[2] .. ARGV[1], 'checkIn', ARGV[3], 'checkOut', ARGV[4]) "
                + "redis.call('expire', KEYS[2] .. ARGV[1], ARGV[2]) "
                + "return 1",
            Long.class);
        Long acquired = redisTemplate.execute(
            script,
            List.of(buildIntervalsKey(roomId), buildMetadataPrefix(roomId)),
            token,
            String.valueOf(lockTtlSeconds),
            String.valueOf(checkIn.toEpochDay()),
            String.valueOf(checkOut.toEpochDay()));
        return Long.valueOf(1L).equals(acquired);
    }

    /**
     * Comprueba si un token de bloqueo específico sigue siendo válido y activo en Redis.
     *
     * @param roomId Identificador de la habitación
     * @param token  Token UUID del bloqueo
     * @return true si la metadata del bloqueo existe con fechas de check-in y check-out válidas
     */
    public boolean isValid(Long roomId, String token) {
        List<Object> values = redisTemplate.opsForHash()
            .multiGet(buildMetadataPrefix(roomId) + token, List.of("checkIn", "checkOut"));
        return values != null && values.size() == 2
            && values.get(0) != null && values.get(1) != null;
    }

    /**
     * Libera un bloqueo temporal previamente adquirido, eliminando su clave en el Sorted Set
     * y su Hash de metadatos en Redis.
     *
     * @param roomId Identificador de la habitación
     * @param token  Token UUID del bloqueo
     * @return true si el bloqueo fue liberado exitosamente, false si ya no existía
     */
    public boolean release(Long roomId, String token) {
        DefaultRedisScript<Long> script = new DefaultRedisScript<>(
            "local metadataKey = KEYS[2] .. ARGV[1] "
                + "if redis.call('exists', metadataKey) == 1 then "
                + "redis.call('del', metadataKey) "
                + "return redis.call('zrem', KEYS[1], ARGV[1]) "
                + "else return 0 end",
            Long.class);
        Long released = redisTemplate.execute(
            script,
            List.of(buildIntervalsKey(roomId), buildMetadataPrefix(roomId)),
            token);
        return Long.valueOf(1L).equals(released);
    }

    /**
     * Verifica si una habitación se encuentra actualmente bloqueada por cualquier token activo
     * en un rango de fechas específico.
     *
     * @param roomId   Identificador de la habitación
     * @param checkIn  Fecha de llegada
     * @param checkOut Fecha de salida
     * @return true si existe al menos un bloqueo activo que se solape con el rango consultado
     */
    public boolean isLocked(Long roomId, LocalDate checkIn, LocalDate checkOut) {
        DefaultRedisScript<Long> script = new DefaultRedisScript<>(
            "local members = redis.call('zrange', KEYS[1], 0, -1) "
            + "for _, existingToken in ipairs(members) do "
            + "  local metadataKey = KEYS[2] .. existingToken "
            + "  local existing = redis.call('hmget', metadataKey, 'checkIn', 'checkOut') "
            + "  if existing[1] and existing[2] then "
            + "    if tonumber(existing[2]) > tonumber(ARGV[1]) and tonumber(existing[1]) < tonumber(ARGV[2]) then "
            + "      return 1 "
            + "    end "
            + "  else "
            + "    redis.call('zrem', KEYS[1], existingToken) "
            + "  end "
            + "end "
            + "return 0",
            Long.class
        );

        Long locked = redisTemplate.execute(
            script,
            List.of(buildIntervalsKey(roomId), buildMetadataPrefix(roomId)),
            String.valueOf(checkIn.toEpochDay()),
            String.valueOf(checkOut.toEpochDay())
        );

        return Long.valueOf(1L).equals(locked);
    }
}
