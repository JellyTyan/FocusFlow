<template>
  <RouterView v-slot="{ Component, route }">
    <transition name="page" mode="out-in">
      <component :is="Component" :key="route.fullPath" />
    </transition>
  </RouterView>
</template>

<script setup lang="ts">
import { watch, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { usePreferencesStore } from './stores/preferences';

const preferencesStore = usePreferencesStore();
const { settings } = storeToRefs(preferencesStore);

const applyTheme = (theme: string) => {
  if (typeof document === 'undefined') return;
  
  const body = document.body;
  body.className = body.className
    .replace(/theme-\w+/g, '')
    .trim();
  body.classList.add(`theme-${theme}`);
};

onMounted(() => {
  applyTheme(settings.value.focusTheme);
});

watch(
  () => settings.value.focusTheme,
  (newTheme) => {
    applyTheme(newTheme);
  },
  { immediate: false }
);
</script>
