package aistock.backend.question;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.List;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class QuestionController {

    private final QuestionService questionService;

    @PostMapping("/questions")
    public ResponseEntity<QuestionResponse> submit(@Valid @RequestBody QuestionRequest req) {
        QuestionResponse response = questionService.submit(req);
        if (!response.isCached()) {
            questionService.startStream(response.getQuestionId());
        }
        return ResponseEntity.ok(response);
    }

    @GetMapping(value = "/questions/stream/{questionId}", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter stream(@PathVariable Long questionId) {
        return questionService.stream(questionId);
    }

    @GetMapping("/history")
    public ResponseEntity<List<HistoryResponse>> history(@RequestParam String userKey) {
        return ResponseEntity.ok(questionService.getHistory(userKey));
    }
}
