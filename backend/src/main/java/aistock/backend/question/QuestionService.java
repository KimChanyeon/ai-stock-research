package aistock.backend.question;

import aistock.backend.cache.CacheService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class QuestionService {

    private final QuestionRepository questionRepository;
    private final CacheService cacheService;
    private final QuestionProcessor questionProcessor;

    private final Map<Long, SseEmitter> emitters = new ConcurrentHashMap<>();

    public QuestionResponse submit(QuestionRequest req) {
        Optional<String> cached = cacheService.get(req.getQuestion());

        Question question = Question.of(req.getUserKey(), req.getQuestion());

        if (cached.isPresent()) {
            question.setStatus(QuestionStatus.SUCCESS);
            question.setAnswer(cached.get());
            questionRepository.save(question);
            return new QuestionResponse(question.getId(), true);
        }

        questionRepository.save(question);
        return new QuestionResponse(question.getId(), false);
    }

    public void startStream(Long questionId) {
        SseEmitter emitter = new SseEmitter(300_000L);
        emitters.put(questionId, emitter);
        emitter.onCompletion(() -> emitters.remove(questionId));
        emitter.onTimeout(() -> emitters.remove(questionId));
        emitter.onError(e -> emitters.remove(questionId));
        questionProcessor.process(questionId, emitter);
    }

    public SseEmitter stream(Long questionId) {
        // 진행 중인 경우: 등록된 emitter 반환
        SseEmitter existing = emitters.get(questionId);
        if (existing != null) {
            return existing;
        }

        // 캐시 히트로 이미 완료된 경우: 즉시 complete 이벤트 전송
        SseEmitter emitter = new SseEmitter(30_000L);
        questionRepository.findById(questionId).ifPresentOrElse(
                q -> {
                    if (q.getStatus() == QuestionStatus.SUCCESS && q.getAnswer() != null) {
                        try {
                            emitter.send(SseEmitter.event().name("complete").data(q.getAnswer()));
                        } catch (IOException e) {
                            log.warn("Failed to send cached answer for questionId={}", questionId);
                        }
                    }
                    emitter.complete();
                },
                emitter::complete
        );
        return emitter;
    }

    public List<HistoryResponse> getHistory(String userKey) {
        return questionRepository.findTop10ByUserKeyOrderByCreatedAtDesc(userKey)
                .stream()
                .map(q -> new HistoryResponse(q.getId(), q.getQuestion(), q.getCreatedAt()))
                .collect(Collectors.toList());
    }
}
