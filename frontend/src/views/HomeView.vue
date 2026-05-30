<script setup lang="ts">
import { onMounted } from 'vue'
import { useQuestionStore } from '@/stores/question'
import { submitQuestion, fetchHistory } from '@/api/question'
import { useSSE } from '@/composables/useSSE'
import QuestionInput from '@/components/QuestionInput.vue'
import AgentStatus from '@/components/AgentStatus.vue'
import AnswerResult from '@/components/AnswerResult.vue'
import QuestionHistory from '@/components/QuestionHistory.vue'

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
    const { questionId } = await submitQuestion(question)
    connectStream(questionId)
  } catch {
    store.isLoading = false
  }
}

function connectStream(questionId: number) {
  connect(`/api/v1/questions/stream/${questionId}`, {
    agent_status: (data: unknown) => {
      const { agent, status, result } = data as { agent: string; status: string; result?: string }
      store.setAgentStatus(agent, status as never)
      if (agent === 'RouterAgent' && result === 'not_stock') {
        store.isNotStock = true
        store.isLoading = false
        close()
      }
    },
    complete: (data: unknown) => {
      store.answer = data as never
      store.isLoading = false
      refreshHistory()
      close()
    },
  })
}

async function refreshHistory() {
  try {
    store.history = await fetchHistory()
  } catch {}
}
</script>

<template>
  <div class="layout">
    <QuestionHistory :history="store.history" @select="onSubmit" />

    <main class="main">
      <header class="header">
        <h1 class="logo">Stock Agent Hub</h1>
        <p class="desc">멀티 에이전트 기반 주식 분석 서비스</p>
      </header>

      <QuestionInput :disabled="store.isLoading" @submit="onSubmit" />

      <template v-if="store.currentQuestion">
        <p class="current-question">"{{ store.currentQuestion }}"</p>
        <div class="results">
          <AgentStatus :agents="store.agents" :is-not-stock="store.isNotStock" />
          <AnswerResult v-if="store.answer" :answer="store.answer" />
        </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  gap: 24px;
  padding: 40px 32px;
  max-width: 1080px;
  margin: 0 auto;
  align-items: flex-start;
}
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}
.header { margin-bottom: 4px; }
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
.current-question {
  font-size: 14px;
  color: #64748b;
}
.results {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
</style>
