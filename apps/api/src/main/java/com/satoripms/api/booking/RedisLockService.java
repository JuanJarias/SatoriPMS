package com.satoripms.api.booking;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RedisLockService {

    private final StringRedisTemplate redisTemplate;
    private final long lockTtlSeconds;

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

        /** Registra el intervalo solo si no se solapa con otro lock activo. */
        public boolean tryLock(Long roomId, java.time.LocalDate checkIn,
                   java.time.LocalDate checkOut, String token) {
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

        public boolean isValid(Long roomId, String token) {
        List<Object> values = redisTemplate.opsForHash()
            .multiGet(buildMetadataPrefix(roomId) + token, List.of("checkIn", "checkOut"));
        return values != null && values.size() == 2
            && values.get(0) != null && values.get(1) != null;
        }

        /** Solo libera el intervalo si todavía pertenece al token indicado. */
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
}