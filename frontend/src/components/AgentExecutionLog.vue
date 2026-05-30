<script setup lang="ts">
import { ref, watch } from 'vue'
import { fetchAgentLogs } from '@/api/question'
import type { AgentLogEntry } from '@/api/question'

const props = defineProps<{ questionId: number | null; answer?: unknown }>()
const emit = defineEmits<{ 'has-logs': [boolean] }>()

const logs = ref<AgentLogEntry[]>([])

const agentLabel: Record<string, string> = {
  RouterAgent: '질문 판별',
  ResearchAgent: '정보 수집',
  SummaryAgent: '답변 생성',
}

function formatDuration(ms: number | null): string {
  if (ms == null) return '-'
  if (ms === 0) return '< 1s'   // MySQL DATETIME 초 단위 정밀도로 인한 반올림
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

function totalMs(): number {
  return logs.value.reduce((acc, l) => acc + (l.durationMs ?? 0), 0)
}

watch(
  () => [props.questionId, props.answer],
  async ([id]) => {
    if (!id) { logs.value = []; emit('has-logs', false); return }
    try {
      logs.value = await fetchAgentLogs(id as number)
    } catch {
      logs.value = []
    }
    emit('has-logs', logs.value.length > 0)
  },
  { immediate: true },
)
</script>

<template>
  <div class="card">
    <p class="title">실행 로그</p>

    <!-- 로그 목록 -->
    <ul class="list">
      <li v-for="log in logs" :key="log.id" class="item" :class="log.status.toLowerCase()">
        <div class="item-header">
          <span class="agent-name">{{ agentLabel[log.agentName] ?? log.agentName }}</span>
          <span class="status-dot" :class="log.status.toLowerCase()" />
        </div>
        <div class="item-footer">
          <span class="badge" :class="log.status.toLowerCase()">
            {{ log.status === 'SUCCESS' ? '완료' : log.status === 'FAIL' ? '실패' : '실행 중' }}
          </span>
          <span class="duration">{{ formatDuration(log.durationMs) }}</span>
        </div>
      </li>
    </ul>

    <!-- 합계 -->
    <div v-if="logs.length > 0" class="total">
      <span>총 소요</span>
      <span class="total-val">{{ formatDuration(totalMs()) }}</span>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1.5px solid #e2e8f0;
}
.title {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 16px;
}
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.item {
  border-radius: 8px;
  padding: 10px 12px;
  border: 1px solid #f1f5f9;
  background: #f8fafc;
}
.item.success { background: #f0fdf4; border-color: #bbf7d0; }
.item.fail    { background: #fef2f2; border-color: #fecaca; }
.item.running {
  background: #fffbeb;
  border-color: #fde68a;
  animation: pulse-item 1.6s ease-in-out infinite;
}
@keyframes pulse-item {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.7; }
}

.item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}
.agent-name {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}
.item.fail .agent-name    { color: #991b1b; }

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.success { background: #22c55e; }
.status-dot.fail    { background: #ef4444; }
.status-dot.running {
  background: #f59e0b;
  animation: blink 1s ease-in-out infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.3; }
}

.item-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 99px;
}
.badge.success { color: #16a34a; background: #dcfce7; }
.badge.fail    { color: #dc2626; background: #fee2e2; }
.badge.running { color: #d97706; background: #fef9e7; }

.duration {
  font-size: 12px;
  color: #64748b;
  font-variant-numeric: tabular-nums;
}

.total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
  font-size: 12px;
  color: #94a3b8;
}
.total-val {
  font-weight: 600;
  color: #475569;
}
</style>
