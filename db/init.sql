USE app;

CREATE TABLE IF NOT EXISTS question_history (
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_key   VARCHAR(36)                              NOT NULL COMMENT '브라우저 UUID',
    question   TEXT                                     NOT NULL,
    answer     JSON                                     NULL     COMMENT '{"ticker":"","recommendation":"","summary":"","positives":[],"risks":[]}',
    status     ENUM ('PENDING', 'RUNNING', 'SUCCESS', 'FAIL') NOT NULL DEFAULT 'PENDING',
    created_at DATETIME                                 NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_key (user_key),
    INDEX idx_created_at (created_at)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS agent_execution_log (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    question_id BIGINT      NOT NULL,
    run_id      VARCHAR(36) NOT NULL,
    agent_name  VARCHAR(50) NOT NULL,
    status      ENUM ('RUNNING', 'SUCCESS', 'FAIL') NOT NULL,
    started_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME    NULL,
    INDEX idx_question_id (question_id),
    INDEX idx_run_id (run_id),
    CONSTRAINT fk_agent_log_question FOREIGN KEY (question_id) REFERENCES question_history (id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
