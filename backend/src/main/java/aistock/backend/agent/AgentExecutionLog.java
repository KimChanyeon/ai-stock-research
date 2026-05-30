package aistock.backend.agent;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "agent_execution_log")
@Data
@NoArgsConstructor
public class AgentExecutionLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "question_id", nullable = false)
    private Long questionId;

    @Column(name = "run_id", nullable = false, length = 36)
    private String runId;

    @Column(name = "agent_name", nullable = false, length = 50)
    private String agentName;

    @Column(nullable = false, length = 10)
    private String status;

    @Column(name = "started_at", nullable = false)
    private LocalDateTime startedAt;

    @Column(name = "finished_at")
    private LocalDateTime finishedAt;
}
