<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{ disabled: boolean }>()
const emit = defineEmits<{ submit: [question: string] }>()

const input = ref('')

function onSubmit() {
  const q = input.value.trim()
  if (!q || props.disabled) return
  emit('submit', q)
  input.value = ''
}
</script>

<template>
  <div class="wrap">
    <input
      v-model="input"
      type="text"
      placeholder="주식 관련 질문을 입력하세요. 예) 엔비디아 전망 알려줘"
      :disabled="disabled"
      @keyup.enter="onSubmit"
      class="input"
    />
    <button :disabled="disabled || !input.trim()" @click="onSubmit" class="btn">
      분석하기
    </button>
  </div>
</template>

<style scoped>
.wrap {
  display: flex;
  gap: 10px;
}
.input {
  flex: 1;
  padding: 13px 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  background: #fff;
  transition: border-color 0.2s;
}
.input:focus { border-color: #3b82f6; }
.input:disabled { background: #f8fafc; color: #94a3b8; }
.btn {
  padding: 13px 24px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}
.btn:hover:not(:disabled) { background: #2563eb; }
.btn:disabled { background: #bfdbfe; cursor: not-allowed; }
</style>
