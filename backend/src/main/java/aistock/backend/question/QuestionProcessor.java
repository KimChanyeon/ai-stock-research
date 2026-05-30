package aistock.backend.question;

import aistock.backend.ai.AiServiceClient;
import aistock.backend.cache.CacheService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.UUID;

@Component
@RequiredArgsConstructor
@Slf4j
public class QuestionProcessor {

    private final QuestionRepository questionRepository;
    private final CacheService cacheService;
    private final AiServiceClient aiServiceClient;

    @Async
    public void process(Long questionId, SseEmitter emitter) {
        Question q = questionRepository.findById(questionId).orElse(null);
        if (q == null) {
            emitter.complete();
            return;
        }

        q.setStatus(QuestionStatus.RUNNING);
        questionRepository.save(q);

        String runId = UUID.randomUUID().toString();
        try {
            aiServiceClient.startRun(runId, q.getQuestion());

            aiServiceClient.streamEvents(runId, (event, data) -> {
                try {
                    emitter.send(SseEmitter.event().name(event).data(data));
                } catch (IOException e) {
                    log.warn("Failed to forward event to client, questionId={}", questionId);
                }

                if ("complete".equals(event)) {
                    q.setStatus(QuestionStatus.SUCCESS);
                    q.setAnswer(data);
                    questionRepository.save(q);
                    cacheService.set(q.getQuestion(), data);
                }
            });

            emitter.complete();

        } catch (Exception e) {
            log.error("Agent processing failed, questionId={}", questionId, e);
            q.setStatus(QuestionStatus.FAIL);
            questionRepository.save(q);
            emitter.completeWithError(e);
        }
    }
}
