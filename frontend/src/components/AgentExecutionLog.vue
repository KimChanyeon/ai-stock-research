<script setup lang="ts">
import { ref, watch } from 'vue'
import { fetchAgentLogs } from '@/api/question'
import type { AgentLogEntry } from '@/api/question'

const props = defineProps<{ questionId: number | null }>()

const logs = ref<AgentLogEntry[]>([])
const open = ref(false)

const agentLabel: Record<string, string> = {
  RouterAgent: '질문 판별',
  ResearchAgent: '정보 수집',
  SummaryAgent: '답변 생성',
}

function formatDuration(ms: number | null): string {
  if (ms == null) return '-'
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

function totalMs(): number {
  return logs.value.reduce((acc, l) => acc + (l.durationMs ?? 0), 0)
}

watch(
  () => props.questionId,
  async (id) => {
    if (!id) { logs.value = []; open.value = false; return }
    try {
      logs.value = await fetchAgentLogs(id)
      open.value = logs.value.length > 0
    } catch {
      logs.value = []
    }
  },
  { immediate: true },
)
</script>

<template>
  <div v-if="logs.length > 0" class="log-wrap">
    <button class="toggle" @click="open = !open">
      <span class="toggle-icon">{{ open ? '▾' : '▸' }}</span>
      실행 로그
      <span class="total">총 {{ formatDuration(totalMs()) }}</span>
    </button>

    <div v-if="open" class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>에이전트</th>
            <th>상태</th>
            <th>소요시간</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td class="agent-name">{{ agentLabel[log.agentName] ?? log.agentName }}</td>
            <td>
              <span class="status-badge" :class="log.status.toLowerCase()">
                {{ log.status === 'SUCCESS' ? '완료' : log.status === 'FAIL' ? '실패' : '실행 중' }}
              </span>
            </td>
            <td class="duration">{{ formatDuration(log.durationMs) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.log-wrap {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
}
.toggle {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 11px 16px;
  background: #f8fafc;
  border: none;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  text-align: left;
}
.toggle:hover { background: #f1f5f9; }
.toggle-icon { font-size: 11px; color: #94a3b8; }
.total {
  margin-left: auto;
  font-size: 11px;
  font-weight: 500;
  color: #94a3b8;
}

.table-wrap { overflow-x: auto; }
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.table th {
  padding: 8px 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
  border-bottom: 1px solid #f1f5f9;
  background: #fafafa;
}
.table td {
  padding: 9px 16px;
  color: #334155;
  border-bottom: 1px solid #f8fafc;
}
.table tr:last-child td { border-bottom: none; }

.agent-name { font-weight: 500; }
.duration { color: #64748b; font-variant-numeric: tabular-nums; }

.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 99px;
}
.status-badge.success { color: #16a34a; background: #dcfce7; }
.status-badge.fail    { color: #dc2626; background: #fee2e2; }
.status-badge.running { color: #d97706; background: #fef9e7; }
</style>
