<script setup lang="ts">
import type { HistoryItem } from '@/api/question'

defineProps<{ history: HistoryItem[] }>()
const emit = defineEmits<{ select: [item: HistoryItem] }>()
</script>

<template>
  <aside class="sidebar">
    <p class="sidebar-title">최근 질문</p>
    <p v-if="history.length === 0" class="empty">아직 질문 이력이 없습니다.</p>
    <ul v-else class="list">
      <li
        v-for="item in history"
        :key="item.id"
        class="item"
        @click="emit('select', item)"
      >
        {{ item.question }}
      </li>
    </ul>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1.5px solid #e2e8f0;
  position: sticky;
  top: 32px;
}
.sidebar-title {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 14px;
}
.empty {
  font-size: 13px;
  color: #cbd5e1;
}
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.item {
  font-size: 13px;
  color: #475569;
  padding: 8px 10px;
  border-radius: 7px;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: background 0.15s, color 0.15s;
}
.item:hover {
  background: #f1f5f9;
  color: #1e293b;
}
</style>
