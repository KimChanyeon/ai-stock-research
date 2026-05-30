import axios from 'axios'
import { getUserKey } from '@/utils/userKey'
import type { Answer } from '@/stores/question'

const api = axios.create({ baseURL: '/api/v1' })

export interface QuestionResponse {
  questionId: number
  cached: boolean
}

export interface HistoryItem {
  id: number
  question: string
  createdAt: string
}

export interface QuestionDetail {
  id: number
  question: string
  answer: Answer | null
  status: string
  createdAt: string
}

export async function submitQuestion(question: string): Promise<QuestionResponse> {
  const { data } = await api.post<QuestionResponse>('/questions', {
    userKey: getUserKey(),
    question,
  })
  return data
}

export async function fetchHistory(): Promise<HistoryItem[]> {
  const { data } = await api.get<HistoryItem[]>('/history', {
    params: { userKey: getUserKey() },
  })
  return data
}

export async function fetchQuestionDetail(id: number): Promise<QuestionDetail> {
  const { data } = await api.get<QuestionDetail>(`/questions/${id}`)
  return data
}
