package aistock.backend.agent;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AgentExecutionLogRepository extends JpaRepository<AgentExecutionLog, Long> {
    Optional<AgentExecutionLog> findByRunIdAndAgentName(String runId, String agentName);
    List<AgentExecutionLog> findByQuestionIdOrderByStartedAt(Long questionId);
}
