<template>
  <header class="glass-card px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between gap-3 sm:gap-4 mb-4 sm:mb-6 border border-white/10">
    <div class="min-w-0 flex-1">
      <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary truncate">FocusFlow</p>
      <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold gradient-text truncate">Study Flow</h1>
    </div>
    <div class="flex items-center gap-2 sm:gap-3 lg:gap-4 flex-shrink-0">
      <div class="text-right hidden sm:block min-w-0">
        <p class="text-xs sm:text-sm font-semibold text-soft-ice truncate max-w-[120px] lg:max-w-none">{{ authStore.user?.name }}</p>
        <p class="text-[0.625rem] sm:text-xs text-text-secondary hidden lg:block">Gotowy do fokusu?</p>
      </div>
      <button
        @click="() => router.push('/profile')"
        class="w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-soft-ice/10 border border-white/10 flex items-center justify-center text-xl sm:text-2xl flex-shrink-0"
        aria-label="Profil"
      >
        {{ avatarEmoji }}
      </button>
      <button
        @click="handleLogout"
        class="btn-ghost text-xs sm:text-sm px-3 sm:px-6 py-2 sm:py-3 hidden md:inline-flex"
      >
        Wyloguj się
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import { usePreferencesStore } from '../../stores/preferences';

const router = useRouter();
const authStore = useAuthStore();
const preferencesStore = usePreferencesStore();
const { settings } = storeToRefs(preferencesStore);

const avatarEmoji = computed(() => settings.value.avatarEmoji || '🧠');

const handleLogout = async () => {
  await authStore.logout();
  router.push('/auth/login');
};
</script>
