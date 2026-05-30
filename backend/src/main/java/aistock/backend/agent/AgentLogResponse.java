package aistock.backend.agent;

import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class AgentLogResponse {
    private final Long id;
    private final String agentName;
    private final String status;
    private final LocalDateTime startedAt;
    private final LocalDateTime finishedAt;
    private final Long durationMs;

    public AgentLogResponse(AgentExecutionLog e) {
        this.id = e.getId();
        this.agentName = e.getAgentName();
        this.status = e.getStatus();
        this.startedAt = e.getStartedAt();
        this.finishedAt = e.getFinishedAt();
        this.durationMs = (e.getStartedAt() != null && e.getFinishedAt() != null)
                ? java.time.Duration.between(e.getStartedAt(), e.getFinishedAt()).toMillis()
                : null;
    }
}
