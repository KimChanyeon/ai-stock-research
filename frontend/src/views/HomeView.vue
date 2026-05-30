<script setup lang="ts">
import { onMounted } from 'vue'
import { useQuestionStore } from '@/stores/question'
import { submitQuestion, fetchHistory, fetchQuestionDetail } from '@/api/question'
import type { HistoryItem } from '@/api/question'
import { useSSE } from '@/composables/useSSE'
import QuestionInput from '@/components/QuestionInput.vue'
import AgentStatus from '@/components/AgentStatus.vue'
import AnswerResult from '@/components/AnswerResult.vue'
import QuestionHistory from '@/components/QuestionHistory.vue'
import AgentExecutionLog from '@/components/AgentExecutionLog.vue'

const store = useQuestionStore()
const { connect, close } = useSSE()

onMounted(async () => {
  try {
    store.history = await fetchHistory()
  } catch {
    // 백엔드 미연결 시 무시
  }
})

async function onSubmit(question: string) {
  store.reset()
  store.isLoading = true
  store.currentQuestion = question

  try {
    const { questionId, cached } = await submitQuestion(question)
    store.currentQuestionId = questionId
    if (cached) store.isHistoryResult = true
    connectStream(questionId)
  } catch {
    store.isLoading = false
    store.error = '서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.'
  }
}

async function onHistorySelect(item: HistoryItem) {
  close()
  store.reset()
  store.currentQuestion = item.question

  try {
    const detail = await fetchQuestionDetail(item.id)
    if (detail.answer && detail.status === 'SUCCESS') {
      store.isHistoryResult = true
      store.currentQuestionId = item.id
      store.answer = detail.answer
    } else {
      // 답변 없으면 새로 실행
      await onSubmit(item.question)
    }
  } catch {
    await onSubmit(item.question)
  }
}

function connectStream(questionId: number) {
  connect(
    `/api/v1/questions/stream/${questionId}`,
    {
      agent_status: (data: unknown) => {
        const { agent, status, result } = data as { agent: string; status: string; result?: string }
        store.setAgentStatus(agent, status.toLowerCase() as never)
        if (agent === 'RouterAgent' && result === 'not_stock') {
          store.isNotStock = true
          store.isLoading = false
          refreshHistory()
          close()
        }
      },
      complete: (data: unknown) => {
        store.answer = data as never
        store.isLoading = false
        refreshHistory()
        close()
      },
    },
    () => {
      store.isLoading = false
      store.error = 'AI 분석 중 연결이 끊어졌습니다. 다시 시도해 주세요.'
    },
  )
}

async function refreshHistory() {
  try {
    store.history = await fetchHistory()
  } catch {}
}
</script>

<template>
  <div class="layout">
    <QuestionHistory :history="store.history" @select="onHistorySelect" />

    <main class="main">
      <header class="header">
        <h1 class="logo">Stock Agent Hub</h1>
        <p class="desc">멀티 에이전트 기반 주식 분석 서비스</p>
      </header>

      <div class="notice">
        <span class="notice-version">v1 Beta</span>
        <p>
          현재 버전은 <strong>질문별 독립 분석</strong> 방식으로 동작합니다.
        </p>
        <p>
          이전 질문과의 맥락은 아직 이어지지 않으니, 분석받고 싶은 종목을 질문 안에 함께 담아주세요.
        </p>
        <span class="notice-example">예) "테슬라 지금 사도 될까?", "NVDA 단기 전망 알려줘"</span>
      </div>

      <QuestionInput :disabled="store.isLoading" @submit="onSubmit" />

      <div v-if="store.error" class="error-banner">
        {{ store.error }}
      </div>

      <template v-if="store.currentQuestion && !store.error">
        <p class="current-question">"{{ store.currentQuestion }}"</p>
        <div class="results">
          <!-- 실시간 분석 중: 에이전트 상태 -->
          <AgentStatus
            v-if="!store.isHistoryResult"
            :agents="store.agents"
            :is-not-stock="store.isNotStock"
          />

          <!-- 이전 조회 결과 — 비주식 -->
          <div v-if="store.isHistoryResult && store.answer?.not_stock" class="not-stock-history">
            <span class="not-stock-icon">🔍</span>
            <div>
              <p class="not-stock-title">주식 관련 질문이 아닙니다</p>
              <p class="not-stock-sub">
                종목명이나 티커를 포함해서 다시 질문해보세요.<br />예) "테슬라 지금 매수해도 될까?",
                "NVDA 전망 알려줘"
              </p>
            </div>
          </div>

          <!-- 분석 결과 -->
          <AnswerResult
            v-if="store.answer && !store.answer.not_stock"
            :answer="store.answer"
            :is-history="store.isHistoryResult"
          />

        </div>
      </template>
    </main>

    <!-- 오른쪽 사이드바: 실행 로그 -->
    <aside class="log-sidebar">
      <AgentExecutionLog :question-id="store.currentQuestionId" />
    </aside>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  gap: 24px;
  padding: 40px 32px;
  max-width: 1280px;
  margin: 0 auto;
  align-items: flex-start;
}
.log-sidebar {
  width: 220px;
  flex-shrink: 0;
  position: sticky;
  top: 32px;
}
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}
.header {
  margin-bottom: 4px;
}
.logo {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}
.desc {
  font-size: 13px;
  color: #94a3b8;
}

.notice {
  font-size: 13px;
  color: #475569;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 10px;
  padding: 12px 16px;
  line-height: 1.7;
}
.notice strong {
  color: #0369a1;
}
.notice-version {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  color: #0369a1;
  background: #e0f2fe;
  border-radius: 4px;
  padding: 1px 6px;
  margin-right: 6px;
  letter-spacing: 0.04em;
  vertical-align: middle;
}
.notice-example {
  font-size: 12px;
  color: #64748b;
}

.error-banner {
  font-size: 14px;
  color: #991b1b;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  padding: 12px 16px;
}
.current-question {
  font-size: 14px;
  color: #64748b;
}
.results {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.not-stock-history {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: #fffbeb;
  border: 1.5px solid #fde68a;
  border-radius: 12px;
  padding: 18px 20px;
}
.not-stock-icon {
  font-size: 22px;
  line-height: 1;
  margin-top: 2px;
}
.not-stock-title {
  font-size: 14px;
  font-weight: 600;
  color: #92400e;
  margin-bottom: 6px;
}
.not-stock-sub {
  font-size: 13px;
  color: #b45309;
  line-height: 1.6;
}
</style>
