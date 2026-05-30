USE app;

CREATE TABLE IF NOT EXISTS question_history (
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_key   VARCHAR(36)                              NOT NULL COMMENT '브라우저 UUID',
    question   TEXT                                     NOT NULL,
    answer     JSON                                     NULL     COMMENT '{"summary":"","positives":[],"risks":[]}',
    status     ENUM ('PENDING', 'RUNNING', 'SUCCESS', 'FAIL') NOT NULL DEFAULT 'PENDING',
    created_at DATETIME                                 NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_key (user_key),
    INDEX idx_created_at (created_at)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
