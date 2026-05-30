<script setup lang="ts">
import { computed } from 'vue'
import type { AgentState } from '@/stores/question'

const props = defineProps<{ agents: AgentState[]; isNotStock: boolean }>()
const isAnyRunning = computed(() => props.agents.some((a) => a.status === 'running'))
</script>

<template>
  <div class="card">
    <!-- 실행 중 진행 표시줄 -->
    <div class="progress-track">
      <div v-if="isAnyRunning" class="progress-bar" />
    </div>

    <p class="card-title">Agent 진행 상태</p>

    <div v-if="isNotStock" class="not-stock">
      주식 관련 질문이 아닙니다. 주식에 관한 질문을 입력해 주세요.
    </div>

    <ul v-else class="list">
      <li v-for="agent in agents" :key="agent.name" class="item" :class="agent.status">
        <!-- 스피너 (running) / 아이콘 (기타) -->
        <span class="icon-wrap">
          <span v-if="agent.status === 'running'" class="spinner" />
          <span v-else class="icon" :class="agent.status">
            <template v-if="agent.status === 'success'">✔</template>
            <template v-else-if="agent.status === 'fail'">✖</template>
            <template v-else>○</template>
          </span>
        </span>

        <span class="label">{{ agent.label }}</span>

        <span class="badge" :class="agent.status">
          <template v-if="agent.status === 'running'">
            <span class="dots">분석 중</span>
          </template>
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
  padding: 0;
  border: 1.5px solid #e2e8f0;
  overflow: hidden;
}

/* 상단 진행 표시줄 */
.progress-track {
  height: 3px;
  background: #f1f5f9;
}
.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 40%, #fde68a 60%, #f59e0b 100%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.card-title {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 20px 24px 16px;
  margin: 0;
}
.list {
  list-style: none;
  padding: 0 24px 20px;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 행 */
.item {
  display: flex;
  align-items: center;
  gap: 12px;
  border-radius: 8px;
  padding: 10px 12px;
  transition: background 0.2s;
}
.item.running {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border: 1px solid #fde68a;
  box-shadow: 0 1px 6px rgba(245, 158, 11, 0.12);
}
.item.success { background: #f0fdf4; }
.item.fail    { background: #fef2f2; }
.item.idle,
.item.pending { background: #f8fafc; }

/* 스피너 */
.icon-wrap {
  width: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2.5px solid #fde68a;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.icon {
  font-size: 14px;
  width: 16px;
  text-align: center;
}
.icon.success { color: #22c55e; }
.icon.fail    { color: #ef4444; }
.icon.idle,
.icon.pending { color: #cbd5e1; }

.label {
  flex: 1;
  font-size: 14px;
  color: #1e293b;
  font-weight: 500;
}
.item.idle .label,
.item.pending .label { color: #94a3b8; }

/* 배지 */
.badge {
  font-size: 12px;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 99px;
}
.badge.success { color: #16a34a; background: #dcfce7; }
.badge.running  { color: #d97706; background: #fef9e7; }
.badge.fail     { color: #dc2626; background: #fee2e2; }
.badge.idle,
.badge.pending  { color: #94a3b8; background: #f1f5f9; }

/* 타이핑 점 애니메이션 */
.dots::after {
  content: '';
  animation: typing-dots 1.2s steps(3, end) infinite;
}
@keyframes typing-dots {
  0%   { content: ''; }
  33%  { content: '.'; }
  66%  { content: '..'; }
  100% { content: '...'; }
}

.not-stock {
  font-size: 14px;
  color: #92400e;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 12px 14px;
  margin: 0 24px 20px;
}
</style>
