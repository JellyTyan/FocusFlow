<template>
  <div class="flex gap-1">
    <button
      type="button"
      v-for="star in 5"
      :key="star"
      @click="handleClick(star)"
      :disabled="readonly"
      class="text-2xl transition-transform hover:scale-110 disabled:cursor-default disabled:hover:scale-100"
      :class="star <= modelValue ? 'text-sea-mint' : 'text-soft-ice/20'"
    >
      {{ star <= modelValue ? '⭐' : '☆' }}
    </button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: number;
  readonly?: boolean;
}>();

const emit = defineEmits<{
  update: [value: number];
}>();

function handleClick(star: number) {
  if (!props.readonly) {
    emit('update', star);
  }
}
</script>
