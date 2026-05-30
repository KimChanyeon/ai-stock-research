package aistock.backend.question;

import aistock.backend.agent.AgentLogService;
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
    private final AgentLogService agentLogService;

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
                // DB 기록 먼저 → 그 후 SSE 전송 (순서 보장으로 프론트 조회 시 최신 상태 반영)
                if ("agent_status".equals(event)) {
                    String agentName = extractJsonString(data, "agent");
                    String agentStatus = extractJsonString(data, "status");
                    if (agentName != null && agentStatus != null) {
                        if ("RUNNING".equals(agentStatus)) {
                            agentLogService.logStart(questionId, runId, agentName);
                        } else {
                            agentLogService.logEnd(runId, agentName, agentStatus);
                        }
                    }
                }

                if ("complete".equals(event)) {
                    q.setStatus(QuestionStatus.SUCCESS);
                    q.setAnswer(data);
                    questionRepository.save(q);
                    if (!data.contains("\"not_stock\"")) {
                        cacheService.set(q.getQuestion(), data);
                    }
                }

                try {
                    emitter.send(SseEmitter.event().name(event).data(data));
                } catch (IOException e) {
                    log.warn("Failed to forward event to client, questionId={}", questionId);
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

    private String extractJsonString(String json, String key) {
        // json.dumps는 "key": "value" (콜론 뒤 공백) 형식으로 직렬화하므로
        // 콜론까지만 찾은 뒤 첫 따옴표를 기준으로 값 추출
        String searchKey = "\"" + key + "\":";
        int keyPos = json.indexOf(searchKey);
        if (keyPos == -1) return null;
        int valStart = json.indexOf("\"", keyPos + searchKey.length());
        if (valStart == -1) return null;
        int valEnd = json.indexOf("\"", valStart + 1);
        return valEnd == -1 ? null : json.substring(valStart + 1, valEnd);
    }
}
