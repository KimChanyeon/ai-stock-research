package aistock.backend.question;

import com.fasterxml.jackson.annotation.JsonRawValue;
import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@AllArgsConstructor
public class QuestionDetailResponse {
    private Long id;
    private String question;
    @JsonRawValue
    private String answer;
    private String status;
    private LocalDateTime createdAt;
}
