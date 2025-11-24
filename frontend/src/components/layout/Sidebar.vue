<template>
  <aside class="hidden lg:flex flex-col glass-card p-4 lg:p-6 xl:p-7 space-y-6 lg:space-y-8 xl:space-y-10 min-h-[calc(100vh-2rem)]">
    <div class="space-y-3">
      <p class="text-[0.65rem] uppercase tracking-[0.5em] text-text-secondary pl-1">Nawigacja</p>
      <nav class="flex flex-col gap-2">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-semibold transition-all w-full"
          :class="[
            route.path === item.to
              ? 'bg-white/10 text-white'
              : 'text-text-secondary hover:bg-white/5'
          ]"
        >
          <span class="text-lg">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </div>

    <div class="space-y-2">
      <p class="text-[0.65rem] uppercase tracking-[0.5em] text-text-secondary pl-1">Focus Streak</p>
      <div class="flex items-center gap-3 p-4 rounded-2xl bg-soft-coral/10 border border-soft-coral/30">
        <span class="text-2xl animate-pulse">🔥</span>
        <div>
          <p class="text-sm text-text-secondary">Seria dni w fokusie</p>
          <p class="text-xl font-bold text-soft-ice">{{ streak }} dni</p>
        </div>
      </div>
    </div>

    <div class="mt-auto flex flex-col gap-4">
      <div class="p-4 rounded-2xl bg-white/5 border border-white/10">
        <p class="text-xs uppercase tracking-[0.4em] text-text-secondary mb-2">Rada</p>
        <p class="text-sm text-soft-ice">
          Zacznij od tematu, który wywołuje największy niepokój. Po pierwszym zwycięstwie wszystko pójdzie łatwiej.
        </p>
      </div>
      <RouterLink
        to="/profile"
        class="btn-ghost text-center w-full"
      >
        ✏️ Profil
      </RouterLink>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
import { useProjectsStore } from '../../stores/projects';
import { storeToRefs } from 'pinia';

const props = defineProps<{
  streak?: number;
}>();

const route = useRoute();
const projectsStore = useProjectsStore();
const { projects } = storeToRefs(projectsStore);

onMounted(() => {
  if (!Array.isArray(projects.value) || !projects.value.length) {
    projectsStore.fetchProjects().catch(() => {});
  }
});

const navItems = computed(() => [
  { to: '/dashboard', label: 'Dashboard', icon: '🏠' },
  { to: '/stats', label: 'Statystyki', icon: '📊' },
  { to: '/profile', label: 'Profil', icon: '👤' },
]);

const streak = computed(() => {
  if (typeof props.streak === 'number') {
    return props.streak;
  }
  if (!Array.isArray(projects.value)) {
    return 1;
  }
  const completed = projects.value.filter(project => project.completed).length;
  return Math.max(completed, 1);
});
</script>

