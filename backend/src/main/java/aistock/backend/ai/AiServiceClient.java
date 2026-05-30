package aistock.backend.ai;

import aistock.backend.common.AppProperties;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Map;
import java.util.function.BiConsumer;

@Component
@Slf4j
public class AiServiceClient {

    private final AppProperties appProperties;
    private final RestClient restClient;

    public AiServiceClient(AppProperties appProperties, RestClient.Builder builder) {
        this.appProperties = appProperties;
        this.restClient = builder.build();
    }

    public void startRun(String runId, String question) {
        restClient.post()
                .uri(appProperties.getUrl() + "/api/v1/agents/run")
                .body(Map.of("runId", runId, "question", question))
                .retrieve()
                .toBodilessEntity();
    }

    public void streamEvents(String runId, BiConsumer<String, String> handler) throws Exception {
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(appProperties.getUrl() + "/api/v1/agents/stream/" + runId))
                .header("Accept", "text/event-stream")
                .GET()
                .build();

        HttpResponse<java.util.stream.Stream<String>> response = client.send(
                request, HttpResponse.BodyHandlers.ofLines());

        String currentEvent = null;
        String currentData = null;

        try (var lines = response.body()) {
            for (String line : (Iterable<String>) lines::iterator) {
                if (line.startsWith("event:")) {
                    currentEvent = line.substring(6).trim();
                } else if (line.startsWith("data:")) {
                    currentData = line.substring(5).trim();
                } else if (line.isEmpty() && currentEvent != null && currentData != null) {
                    handler.accept(currentEvent, currentData);
                    if ("complete".equals(currentEvent)) break;
                    currentEvent = null;
                    currentData = null;
                }
            }
        }
    }
}
