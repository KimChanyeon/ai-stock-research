package aistock.backend.question;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@AllArgsConstructor
public class HistoryResponse {
    private Long id;
    private String question;
    private LocalDateTime createdAt;
}
