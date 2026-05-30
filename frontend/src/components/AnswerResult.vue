<script setup lang="ts">
import type { Answer } from '@/stores/question'

defineProps<{ answer: Answer; isHistory?: boolean }>()
</script>

<template>
  <div class="card">
    <div class="card-header">
      <p class="card-title">분석 결과</p>
      <span v-if="isHistory" class="history-badge">이전 분석</span>
    </div>

    <!-- 티커 + 매수의견 -->
    <div v-if="answer.ticker && answer.recommendation" class="recommendation-row">
      <span class="ticker">{{ answer.ticker }}</span>
      <span class="rec-badge" :class="answer.recommendation.toLowerCase()">
        <span class="rec-icon">
          <template v-if="answer.recommendation === 'BUY'">▲</template>
          <template v-else-if="answer.recommendation === 'SELL'">▼</template>
          <template v-else>━</template>
        </span>
        {{ answer.recommendation === 'BUY' ? '매수' : answer.recommendation === 'SELL' ? '매도' : '중립' }} 의견
      </span>
    </div>

    <div class="section">
      <h4 class="section-label">요약</h4>
      <p class="summary">{{ answer.summary }}</p>
    </div>

    <div class="section">
      <h4 class="section-label positive">긍정 요인</h4>
      <ul class="list">
        <li v-for="(item, i) in answer.positives" :key="i" class="item positive">
          {{ item }}
        </li>
      </ul>
    </div>

    <div class="section">
      <h4 class="section-label risk">리스크</h4>
      <ul class="list">
        <li v-for="(item, i) in answer.risks" :key="i" class="item risk">
          {{ item }}
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  border: 1.5px solid #e2e8f0;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}
.card-title {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.history-badge {
  font-size: 11px;
  font-weight: 500;
  color: #6366f1;
  background: #eef2ff;
  border-radius: 99px;
  padding: 2px 8px;
}

/* 매수의견 */
.recommendation-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 14px 16px;
  border-radius: 10px;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
}
.ticker {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: 0.04em;
}
.rec-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: 99px;
}
.rec-badge.buy  { color: #15803d; background: #dcfce7; }
.rec-badge.hold { color: #6b7280; background: #f3f4f6; }
.rec-badge.sell { color: #dc2626; background: #fee2e2; }
.rec-icon { font-size: 11px; }

.section { margin-bottom: 20px; }
.section:last-child { margin-bottom: 0; }

.section-label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 10px;
}
.section-label.positive { color: #16a34a; }
.section-label.risk     { color: #dc2626; }

.summary {
  font-size: 15px;
  color: #334155;
  line-height: 1.7;
}
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.item {
  font-size: 14px;
  padding: 9px 13px;
  border-radius: 7px;
  line-height: 1.5;
  border-left: 3px solid transparent;
}
.item.positive {
  color: #166534;
  background: #f0fdf4;
  border-left-color: #22c55e;
}
.item.risk {
  color: #991b1b;
  background: #fef2f2;
  border-left-color: #ef4444;
}
</style>
