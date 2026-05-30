package aistock.backend.ai;

import aistock.backend.common.AppProperties;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.function.BiConsumer;

@Component
@Slf4j
public class AiServiceClient {

    private final AppProperties appProperties;
    private final HttpClient httpClient = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .build();

    public AiServiceClient(AppProperties appProperties) {
        this.appProperties = appProperties;
    }

    @SneakyThrows
    public void startRun(String runId, String question) {
        String escaped = question.replace("\\", "\\\\").replace("\"", "\\\"");
        String body = "{\"runId\":\"" + runId + "\",\"question\":\"" + escaped + "\"}";
        byte[] bodyBytes = body.getBytes(java.nio.charset.StandardCharsets.UTF_8);
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(appProperties.getUrl() + "/api/v1/agents/run"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofByteArray(bodyBytes))
                .build();
        httpClient.send(request, HttpResponse.BodyHandlers.discarding());
    }

    public void streamEvents(String runId, BiConsumer<String, String> handler) throws Exception {
        HttpClient client = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();
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
