<script setup lang="ts">
import { computed } from 'vue'
import type { AgentState } from '@/stores/question'

const props = defineProps<{ agents: AgentState[]; isNotStock: boolean }>()

const isAnyRunning = computed(() => props.agents.some((a) => a.status === 'running'))
const isAllDone = computed(() => props.agents.every((a) => a.status === 'success' || a.status === 'fail'))

const cardTitle = computed(() => {
  if (isAnyRunning.value) return 'AI 분석 진행 중'
  if (isAllDone.value) return '분석 완료'
  return '분석 준비 중'
})

const descMap: Record<string, Record<string, string>> = {
  RouterAgent: {
    running: '질문이 주식 관련인지 파악하고 있어요',
    success: '주식 관련 질문으로 확인됐습니다',
    fail: '질문 분류에 실패했습니다',
  },
  ResearchAgent: {
    running: '최신 시장 데이터를 검색 중이에요',
    success: '시장 데이터 수집이 완료됐습니다',
    fail: '데이터 수집에 실패했습니다',
  },
  SummaryAgent: {
    running: '투자 분석 리포트를 작성 중이에요',
    success: '분석 리포트가 완성됐습니다',
    fail: '리포트 작성에 실패했습니다',
  },
}

function desc(agent: AgentState): string {
  return descMap[agent.name]?.[agent.status] ?? ''
}
</script>

<template>
  <div class="card">
    <!-- 실행 중 shimmer 바 -->
    <div class="progress-track">
      <div v-if="isAnyRunning" class="progress-bar" />
    </div>

    <!-- 헤더 -->
    <div class="header">
      <span class="card-title">{{ cardTitle }}</span>
      <span v-if="isAnyRunning" class="live-badge">
        <span class="live-dot" />
        LIVE
      </span>
      <span v-if="isAllDone && !isNotStock" class="done-badge">✓ 완료</span>
    </div>

    <!-- 비주식 -->
    <div v-if="isNotStock" class="not-stock">
      주식 관련 질문이 아닙니다. 종목명이나 티커를 포함해서 다시 질문해주세요.
    </div>

    <!-- 타임라인 스텝 -->
    <div v-else class="steps">
      <div
        v-for="(agent, idx) in agents"
        :key="agent.name"
        class="step"
      >
        <!-- 좌측: 스텝 인디케이터 + 연결선 -->
        <div class="track">
          <div class="dot" :class="agent.status">
            <span v-if="agent.status === 'running'" class="dot-spinner" />
            <span v-else-if="agent.status === 'success'" class="dot-icon">✓</span>
            <span v-else-if="agent.status === 'fail'" class="dot-icon fail">✕</span>
            <span v-else class="dot-num">{{ idx + 1 }}</span>
          </div>
          <div
            v-if="idx < agents.length - 1"
            class="connector"
            :class="{ lit: agent.status === 'success' }"
          />
        </div>

        <!-- 우측: 텍스트 -->
        <div class="body" :class="agent.status">
          <div class="row">
            <span class="label">{{ agent.label }}</span>
            <span class="badge" :class="agent.status">
              <span v-if="agent.status === 'running'" class="dots">분석 중</span>
              <template v-else-if="agent.status === 'success'">완료</template>
              <template v-else-if="agent.status === 'fail'">실패</template>
              <template v-else>대기</template>
            </span>
          </div>
          <p v-if="desc(agent)" class="step-desc" :class="agent.status">{{ desc(agent) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: #fff;
  border-radius: 14px;
  border: 1.5px solid #e2e8f0;
  overflow: hidden;
}

/* shimmer */
.progress-track { height: 3px; background: #f1f5f9; }
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

/* 헤더 */
.header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 22px 14px;
}
.card-title {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
  flex: 1;
  letter-spacing: 0.01em;
}
.live-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 700;
  color: #ef4444;
  letter-spacing: 0.05em;
}
.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ef4444;
  animation: blink 1.1s ease-in-out infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.4; transform: scale(0.8); }
}
.done-badge {
  font-size: 11px;
  font-weight: 600;
  color: #16a34a;
  background: #dcfce7;
  border-radius: 99px;
  padding: 2px 9px;
}

/* 스텝 목록 */
.steps {
  padding: 0 22px 20px;
  display: flex;
  flex-direction: column;
}
.step {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

/* 좌측 트랙 */
.track {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  padding-top: 2px;
}

/* 스텝 원 */
.dot {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
  transition: all 0.3s;
}
.dot.idle,
.dot.pending {
  background: #f8fafc;
  color: #94a3b8;
  border: 2px solid #e2e8f0;
}
.dot.running {
  background: #fef3c7;
  border: 2px solid #f59e0b;
  box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.15), 0 0 16px rgba(245, 158, 11, 0.25);
  animation: glow-pulse 1.6s ease-in-out infinite;
}
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 0 4px rgba(245,158,11,.15), 0 0 16px rgba(245,158,11,.25); }
  50%       { box-shadow: 0 0 0 7px rgba(245,158,11,.22), 0 0 24px rgba(245,158,11,.35); }
}
.dot.success {
  background: #dcfce7;
  border: 2px solid #22c55e;
}
.dot.fail {
  background: #fee2e2;
  border: 2px solid #ef4444;
}
.dot-num { color: #94a3b8; font-size: 13px; }
.dot-icon { font-size: 15px; color: #16a34a; font-weight: 700; }
.dot-icon.fail { color: #ef4444; }

/* 스피너 */
.dot-spinner {
  width: 18px;
  height: 18px;
  border: 2.5px solid #fde68a;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 연결선 */
.connector {
  width: 2px;
  flex: 1;
  min-height: 22px;
  background: #e2e8f0;
  margin: 5px 0 5px;
  border-radius: 1px;
  transition: background 0.4s;
}
.connector.lit { background: #22c55e; }

/* 우측 본문 */
.body {
  flex: 1;
  padding: 6px 0 20px;
  min-height: 42px;
}
.body:last-child { padding-bottom: 4px; }
.row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.label {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  flex: 1;
}
.body.idle .label,
.body.pending .label { color: #94a3b8; font-weight: 500; }

/* 배지 */
.badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 99px;
  white-space: nowrap;
}
.badge.success { color: #16a34a; background: #dcfce7; }
.badge.running  { color: #d97706; background: #fef9e7; }
.badge.fail     { color: #dc2626; background: #fee2e2; }
.badge.idle,
.badge.pending  { color: #cbd5e1; background: #f8fafc; }

/* 설명 텍스트 */
.step-desc {
  font-size: 12px;
  margin: 4px 0 0;
  line-height: 1.5;
}
.step-desc.running  { color: #92400e; }
.step-desc.success  { color: #15803d; }
.step-desc.fail     { color: #b91c1c; }

/* 타이핑 점 */
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

/* 비주식 */
.not-stock {
  font-size: 13px;
  color: #92400e;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 12px 14px;
  margin: 0 22px 20px;
  line-height: 1.6;
}
</style>
