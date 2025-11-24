<template>
  <div
    :class="[
      'glass-card p-6 transition-all duration-200',
      urgent ? 'bg-soft-coral/20 border-2 border-soft-coral' : '',
      hoverable ? 'hover:scale-105 cursor-pointer' : '',
    ]"
    v-bind="$attrs"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  urgent?: boolean;
  hoverable?: boolean;
}>();
</script>
