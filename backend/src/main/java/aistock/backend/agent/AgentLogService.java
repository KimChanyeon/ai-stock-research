package aistock.backend.agent;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class AgentLogService {

    private final AgentExecutionLogRepository repository;

    public void logStart(Long questionId, String runId, String agentName) {
        AgentExecutionLog entry = new AgentExecutionLog();
        entry.setQuestionId(questionId);
        entry.setRunId(runId);
        entry.setAgentName(agentName);
        entry.setStatus("RUNNING");
        entry.setStartedAt(LocalDateTime.now());
        repository.save(entry);
    }

    public void logEnd(String runId, String agentName, String status) {
        repository.findByRunIdAndAgentName(runId, agentName).ifPresent(entry -> {
            entry.setStatus(status);
            entry.setFinishedAt(LocalDateTime.now());
            repository.save(entry);
        });
    }
}
