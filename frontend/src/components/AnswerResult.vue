<script setup lang="ts">
import type { Answer } from '@/stores/question'

defineProps<{ answer: Answer }>()
</script>

<template>
  <div class="card">
    <p class="card-title">분석 결과</p>

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
.card-title {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 20px;
}
.section {
  margin-bottom: 20px;
}
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
