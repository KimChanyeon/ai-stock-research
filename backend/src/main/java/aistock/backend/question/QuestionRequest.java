package aistock.backend.question;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;

@Getter
public class QuestionRequest {

    @NotBlank
    private String userKey;

    @NotBlank
    private String question;
}
