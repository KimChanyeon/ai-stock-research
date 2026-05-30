<script setup lang="ts">
import type { AgentState } from '@/stores/question'

defineProps<{ agents: AgentState[]; isNotStock: boolean }>()
</script>

<template>
  <div class="card">
    <p class="card-title">Agent 진행 상태</p>

    <div v-if="isNotStock" class="not-stock">
      주식 관련 질문이 아닙니다. 주식에 관한 질문을 입력해 주세요.
    </div>

    <ul v-else class="list">
      <li v-for="agent in agents" :key="agent.name" class="item" :class="agent.status">
        <span class="icon" :class="agent.status">
          <template v-if="agent.status === 'success'">✔</template>
          <template v-else-if="agent.status === 'running'">⏳</template>
          <template v-else-if="agent.status === 'fail'">✖</template>
          <template v-else>○</template>
        </span>
        <span class="label">{{ agent.label }}</span>
        <span class="badge" :class="agent.status">
          <template v-if="agent.status === 'running'">진행 중</template>
          <template v-else-if="agent.status === 'success'">완료</template>
          <template v-else-if="agent.status === 'fail'">실패</template>
          <template v-else-if="agent.status === 'pending'">대기 중</template>
        </span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  border: 1.5px solid #e2e8f0;
}
.card-title {
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
  gap: 14px;
}
.item {
  display: flex;
  align-items: center;
  gap: 12px;
  border-radius: 8px;
  padding: 4px 6px;
  margin: -4px -6px;
  transition: background 0.2s;
}
.item.running {
  background: #fffbeb;
  animation: pulse-row 1.8s ease-in-out infinite;
}
@keyframes pulse-row {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
.icon {
  width: 22px;
  text-align: center;
  font-size: 15px;
}
.icon.success { color: #22c55e; }
.icon.running  { color: #f59e0b; }
.icon.fail     { color: #ef4444; }
.icon.idle,
.icon.pending  { color: #cbd5e1; }

.label {
  flex: 1;
  font-size: 15px;
  color: #1e293b;
}
.badge {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 99px;
}
.badge.success { color: #16a34a; background: #f0fdf4; }
.badge.running  { color: #d97706; background: #fffbeb; }
.badge.fail     { color: #dc2626; background: #fef2f2; }
.badge.idle,
.badge.pending  { color: #94a3b8; background: #f1f5f9; }

.not-stock {
  font-size: 14px;
  color: #92400e;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 12px 14px;
}
</style>
