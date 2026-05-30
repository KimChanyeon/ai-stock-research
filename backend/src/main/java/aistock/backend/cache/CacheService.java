package aistock.backend.cache;

import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Duration;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class CacheService {

    private static final String PREFIX = "cache:answer:";
    private static final Duration TTL = Duration.ofHours(24);

    private final StringRedisTemplate redis;

    public Optional<String> get(String question) {
        return Optional.ofNullable(redis.opsForValue().get(PREFIX + hash(question)));
    }

    public void set(String question, String answerJson) {
        redis.opsForValue().set(PREFIX + hash(question), answerJson, TTL);
    }

    private String hash(String text) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] bytes = md.digest(text.strip().toLowerCase().getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : bytes) sb.append(String.format("%02x", b));
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }
}
