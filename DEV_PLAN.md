# Stock Agent Hub — 개발 기획서

> 기획서: [Stock_Agent_Hub_MVP.md](./Stock_Agent_Hub_MVP.md)

---

## 1. 기술 스택

| 레이어 | 기술 | 버전 | 비고 |
|---|---|---|---|
| Frontend | Vue 3 + TypeScript | Vue 3.5 / TS 6.0 | Vite 빌드, Pinia 상태관리 |
| Backend | Spring Boot | 4.0.6 / Java 21 | REST API, SSE, Redis 캐시 |
| AI Service | FastAPI + crewAI | Python 3.11+ | Gemini API 연동, SSE 스트리밍 |
| DB | MySQL | 8.4 | 질문 이력 저장 |
| Cache | Redis | 8 | 완전 일치 캐시, Semantic Cache |
| 컨테이너 | Docker Compose | - | 로컬 개발 환경 |
| AI 모델 | Google Gemini | gemini-2.0-flash | crewAI LLM 백엔드 |
| 패키지 관리 | npm / Gradle / uv | - | 서비스별 독립 관리 |

---

## 2. 서비스 아키텍처

```
Browser
  │
  ├── REST  ──▶  Backend (Spring Boot :8080)
  │                  │
  │                  ├── MySQL (이력 저장)
  │                  ├── Redis (캐시 조회/저장)
  │                  └── AI Service (HTTP 위임)
  │
  └── SSE   ──▶  Backend (Spring Boot :8080)
                     └── AI Service (:8000) SSE 프록시
```

- 프론트엔드는 백엔드 단일 오리진으로만 통신
- 백엔드는 캐시 히트 시 AI Service 호출 없이 즉시 반환
- 실시간 에이전트 상태는 SSE(Server-Sent Events)로 스트리밍

---

## 3. 디렉토리 구조

### 3-1. Frontend

```
frontend/
├── src/
│   ├── api/
│   │   └── question.ts          # Axios API 호출 함수
│   ├── components/
│   │   ├── QuestionInput.vue     # 질문 입력 컴포넌트
│   │   ├── AgentStatus.vue       # 에이전트 진행 상태 표시
│   │   ├── AnswerResult.vue      # 최종 답변 출력
│   │   └── QuestionHistory.vue  # 최근 질문 이력
│   ├── stores/
│   │   └── question.ts           # Pinia: 질문/답변 상태
│   ├── composables/
│   │   └── useSSE.ts             # SSE 연결 훅
│   ├── views/
│   │   └── HomeView.vue          # 메인 화면 (단일 페이지)
│   └── utils/
│       └── userKey.ts            # UUID 생성/LocalStorage 관리
```

### 3-2. Backend

```
backend/src/main/java/aistock/backend/
├── question/
│   ├── QuestionController.java   # POST /api/v1/questions, GET /stream/{id}
│   ├── QuestionService.java      # 캐시 체크 → AI 호출 → 저장 로직
│   ├── QuestionRepository.java   # JPA Repository
│   └── Question.java             # @Entity
├── history/
│   ├── HistoryController.java    # GET /api/v1/history
│   └── HistoryService.java
├── cache/
│   └── CacheService.java         # Redis 캐시 read/write
├── ai/
│   └── AiServiceClient.java      # AI Service HTTP 클라이언트 (WebClient)
└── common/
    ├── config/
    │   ├── RedisConfig.java
    │   └── WebConfig.java        # CORS 설정
    └── dto/
        ├── QuestionRequest.java
        └── QuestionResponse.java
```

### 3-3. AI Service

```
ai-service/
├── main.py                        # FastAPI 앱 진입점
├── routers/
│   └── agents.py                  # POST /api/v1/agents/run, GET /stream/{run_id}
├── agents/
│   ├── router_agent.py            # Router Agent (주식 질문 판별)
│   ├── research_agent.py          # Research Agent (정보 수집)
│   └── summary_agent.py           # Summary Agent (답변 생성)
├── crew/
│   └── stock_crew.py              # crewAI Crew 조합 및 실행
├── schemas/
│   └── agent.py                   # Pydantic 스키마
├── core/
│   ├── config.py                  # pydantic-settings 환경 변수
│   └── gemini.py                  # Gemini LLM 초기화
└── db/
    ├── database.py                # SQLAlchemy 엔진 설정
    └── models.py                  # ORM 모델
```

---

## 4. API 명세

### Backend REST API

#### 질문 제출
```
POST /api/v1/questions
Content-Type: application/json

{
  "userKey": "uuid-string",
  "question": "엔비디아 전망 알려줘"
}

Response 200:
{
  "questionId": 1,
  "cached": false
}
```

#### 에이전트 상태 SSE 스트림
```
GET /api/v1/questions/stream/{questionId}
Accept: text/event-stream

event: agent_status
data: {"agent": "RouterAgent", "status": "RUNNING"}

event: agent_status
data: {"agent": "RouterAgent", "status": "SUCCESS", "result": "stock_related"}

event: agent_status
data: {"agent": "ResearchAgent", "status": "RUNNING"}

event: agent_status
data: {"agent": "ResearchAgent", "status": "SUCCESS"}

event: agent_status
data: {"agent": "SummaryAgent", "status": "RUNNING"}

event: complete
data: {"summary": "...", "positives": [...], "risks": [...]}
```

#### 질문 이력 조회
```
GET /api/v1/history?userKey={uuid}

Response 200:
[
  {"id": 1, "question": "엔비디아 전망", "createdAt": "2026-05-30T10:00:00"}
]
```

### AI Service Internal API

```
POST /api/v1/agents/run
{
  "runId": "uuid",
  "question": "엔비디아 전망 알려줘"
}

GET /api/v1/agents/stream/{runId}   # SSE (Backend가 프록시)
```

---

## 5. DB 스키마

```sql
CREATE TABLE question_history (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_key    VARCHAR(36)  NOT NULL COMMENT '브라우저 UUID',
  question    TEXT         NOT NULL,
  answer      JSON         NULL     COMMENT '{"summary":"","positives":[],"risks":[]}',
  status      ENUM('PENDING','RUNNING','SUCCESS','FAIL') DEFAULT 'PENDING',
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_key (user_key),
  INDEX idx_created_at (created_at)
);
```

---

## 6. crewAI 멀티 에이전트 설계

### LLM 설정 (Gemini via LiteLLM)
```python
from crewai import LLM

llm = LLM(
    model="gemini/gemini-2.0-flash",
    api_key=settings.GOOGLE_API_KEY
)
```

### Agent 역할 정의

| Agent | 역할 | 입력 | 출력 |
|---|---|---|---|
| RouterAgent | 주식 관련 질문 여부 판별 | 사용자 질문 | `"stock_related"` / `"not_stock"` |
| ResearchAgent | 종목/기업 정보 수집 | 질문 | 수집된 정보 (뉴스, 재무, 이슈) |
| SummaryAgent | 수집 정보 기반 답변 생성 | 수집 정보 | `{summary, positives, risks}` |

### Crew 실행 흐름

```python
# RouterAgent 먼저 단독 실행 (비주식 시 조기 종료)
router_result = router_agent.execute(question)
if router_result != "stock_related":
    return {"error": "not_stock_question"}

# Research → Summary 순차 실행
crew = Crew(
    agents=[research_agent, summary_agent],
    tasks=[research_task, summary_task],
    process=Process.sequential
)
result = crew.kickoff(inputs={"question": question})
```

### SSE 상태 전파 방식
- crewAI `step_callback`으로 각 Agent 완료 시 이벤트 발행
- `asyncio.Queue` → `sse-starlette` EventSourceResponse로 스트리밍

---

## 7. 캐시 전략

### 1차: 완전 일치 캐시 (Redis, TTL 24시간)

```
Key:   cache:answer:{SHA256(question.lower().strip())}
Value: JSON string (answer)
TTL:   86400초 (24h)
```

### 2차: Semantic Cache (MVP 경량 구현)

```
Key:    cache:embedding:{hash}
Value:  {vector: [...], answer: {...}}

- 최근 100건 대상 코사인 유사도 계산
- 유사도 ≥ 0.92 이면 캐시 반환
- 벡터는 Gemini Embedding API 사용
```

캐시 처리 위치: **Backend CacheService** (AI Service 호출 전 체크)

---

## 8. 환경 변수

### Root `.env` (docker-compose용)
```
GOOGLE_API_KEY=your_key
```

### AI Service 내부 (`ai-service/.env`, 로컬 개발용)
```
GOOGLE_API_KEY=your_key
DB_HOST=localhost
DB_PORT=3306
DB_NAME=app
DB_USER=root
DB_PASSWORD=root
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Backend 내부 (로컬 개발 시 IDE 환경변수 또는 `application-local.yaml`)
```
SPRING_DATASOURCE_URL=jdbc:mysql://localhost:3306/app?serverTimezone=UTC
SPRING_DATASOURCE_USERNAME=root
SPRING_DATASOURCE_PASSWORD=root
SPRING_DATA_REDIS_HOST=localhost
AI_SERVICE_URL=http://localhost:8000
```

---

## 9. 개발 순서

### Phase 1: 기반 구축
1. AI Service — FastAPI 앱 기본 구조 + crewAI 에이전트 3종 구현
2. AI Service — SSE 스트리밍 엔드포인트 구현
3. Backend — DB 엔티티 + Repository + 기본 REST API
4. Backend — Redis CacheService 구현
5. Backend — AI Service 클라이언트 + SSE 프록시

### Phase 2: 프론트엔드 연동
6. Frontend — Pinia 스토어 + Axios API 모듈
7. Frontend — SSE 연결 composable (useSSE)
8. Frontend — QuestionInput / AgentStatus / AnswerResult 컴포넌트

### Phase 3: 통합 검증
9. Docker Compose 전체 연동 테스트
10. 캐시 동작 검증 (완전 일치)
11. Semantic Cache 구현

---

## 10. 로컬 개발 실행

```bash
# 인프라만 실행 (개발 시)
docker compose up mysql redis -d

# 전체 실행
cp .env.example .env   # GOOGLE_API_KEY 입력
docker compose up --build

# 개별 서비스 로컬 실행
cd ai-service && uv run uvicorn main:app --reload --port 8000
cd backend && ./gradlew bootRun
cd frontend && npm run dev
```
