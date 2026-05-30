<script setup lang="ts">
const props = defineProps<{ elapsedMs?: number | null }>()

function formatMs(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(2)}s`
}
</script>

<template>
  <div class="card">
    <p class="title">응답 방식</p>

    <div class="badge">
      <span class="bolt">⚡</span>
      캐시된 분석 결과
    </div>

    <p class="desc">
      동일한 질문에 대해 저장된 분석 결과를
      에이전트 실행 과정 없이 불러왔습니다.
    </p>

    <div v-if="props.elapsedMs != null" class="metric">
      <span class="metric-label">응답 시간</span>
      <span class="metric-value">{{ formatMs(props.elapsedMs) }}</span>
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
.badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 700;
  color: #b45309;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border: 1px solid #fde68a;
  border-radius: 10px;
  padding: 10px 12px;
  margin-bottom: 14px;
}
.bolt {
  font-size: 16px;
  line-height: 1;
}
.desc {
  font-size: 12.5px;
  color: #64748b;
  line-height: 1.65;
  margin-bottom: 16px;
}
.metric {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 14px;
  border-top: 1px solid #f1f5f9;
}
.metric-label {
  font-size: 12px;
  color: #94a3b8;
}
.metric-value {
  font-size: 15px;
  font-weight: 700;
  color: #16a34a;
  font-variant-numeric: tabular-nums;
}
</style>
