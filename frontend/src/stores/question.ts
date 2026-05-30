import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { HistoryItem } from '@/api/question'

export type AgentStatus = 'idle' | 'pending' | 'running' | 'success' | 'fail'

export interface AgentState {
  name: string
  label: string
  status: AgentStatus
}

export interface Answer {
  ticker?: string | null
  recommendation?: 'BUY' | 'HOLD' | 'SELL' | null
  summary: string
  positives: string[]
  risks: string[]
  not_stock?: boolean
}

export const useQuestionStore = defineStore('question', () => {
  const currentQuestion = ref('')
  const currentQuestionId = ref<number | null>(null)
  const isLoading = ref(false)
  const isNotStock = ref(false)
  const isHistoryResult = ref(false)
  const error = ref<string | null>(null)
  const answer = ref<Answer | null>(null)
  const history = ref<HistoryItem[]>([])

  const agents = ref<AgentState[]>([
    { name: 'RouterAgent', label: '질문 판별', status: 'idle' },
    { name: 'ResearchAgent', label: '정보 수집', status: 'idle' },
    { name: 'SummaryAgent', label: '답변 생성', status: 'idle' },
  ])

  function reset() {
    agents.value.forEach((a) => (a.status = 'idle'))
    answer.value = null
    currentQuestionId.value = null
    isNotStock.value = false
    isHistoryResult.value = false
    error.value = null
  }

  function setAgentStatus(name: string, status: AgentStatus) {
    const agent = agents.value.find((a) => a.name === name)
    if (agent) agent.status = status
  }

  return { currentQuestion, currentQuestionId, isLoading, isNotStock, isHistoryResult, error, answer, history, agents, reset, setAgentStatus }
})
