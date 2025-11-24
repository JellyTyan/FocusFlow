<template>
  <div class="min-h-screen theme-bg-primary text-text-primary relative overflow-hidden">
    <div class="absolute inset-0 theme-bg-gradient-overlay" style="opacity: 0.95;"></div>
    <div class="absolute inset-0 pointer-events-none">
      <div class="w-[15rem] sm:w-[22rem] lg:w-[28rem] h-[15rem] sm:h-[22rem] lg:h-[28rem] bg-sea-mint/15 rounded-full blur-3xl absolute -top-8 sm:-top-12 lg:-top-16 left-0"></div>
      <div class="w-[10rem] sm:w-[15rem] lg:w-[18rem] h-[10rem] sm:h-[15rem] lg:h-[18rem] bg-soft-coral/15 rounded-full blur-3xl absolute bottom-4 right-4 sm:right-6 lg:right-8"></div>
    </div>

    <div class="absolute top-3 left-3 sm:top-4 sm:left-4 z-20">
      <router-link
        to="/"
        class="inline-flex items-center gap-1 sm:gap-1.5 px-2.5 py-1.5 sm:px-3 sm:py-1.5 rounded-lg border border-white/20 bg-white/10 text-[0.625rem] sm:text-xs text-soft-ice hover:border-white/40 hover:bg-white/20 transition-colors backdrop-blur-sm"
      >
        <span aria-hidden="true">←</span>
        <span class="hidden sm:inline">Wróć na stronę główną</span>
        <span class="sm:hidden">Wróć</span>
      </router-link>
    </div>

    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-14 lg:py-12 xl:py-16 grid gap-8 sm:gap-10 lg:grid-cols-[0.95fr_1.05fr] items-center min-h-screen">
      <div class="space-y-4 sm:space-y-5 lg:space-y-6 order-2 lg:order-1">
        <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.6em] text-text-secondary">Create account</p>
        <h1 class="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold leading-[1.1] sm:leading-tight">
          Skonfiguruj swój <span class="text-transparent bg-clip-text bg-gradient-to-r from-sea-mint to-soft-coral">Study Flow</span>
          pod styl egzaminu.
        </h1>
        <p class="text-text-secondary text-base sm:text-lg lg:text-xl">
          FocusFlow pomaga strukturyzować egzaminy w siatce Bento, śledzić postęp i utrzymywać uwagę rytmem Pomodoro.
        </p>

        <div class="space-y-3 sm:space-y-4">
          <div
            v-for="step in onboarding"
            :key="step.title"
            class="flex gap-3 sm:gap-4 p-3 sm:p-4 !rounded-lg sm:rounded-2xl bg-white/5 border border-white/10"
          >
            <div class="w-8 h-8 sm:w-10 sm:h-10 !rounded-lg sm:rounded-2xl bg-white/10 flex items-center justify-center text-soft-ice font-semibold text-sm sm:text-base flex-shrink-0">
              {{ step.id }}
            </div>
            <div class="min-w-0">
              <p class="text-sm sm:text-base text-soft-ice font-semibold">{{ step.title }}</p>
              <p class="text-xs sm:text-sm text-text-secondary">{{ step.subtitle }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="glass-card p-4 sm:p-6 lg:p-8 !rounded-lg border border-white/10 shadow-2xl shadow-sea-mint/10 order-1 lg:order-2 w-full">
        <div class="space-y-2 mb-4 sm:mb-5 lg:mb-6">
          <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">Rejestracja</p>
          <h2 class="text-2xl sm:text-3xl font-bold">Złóż swoje skoncentrowane środowisko</h2>
          <p class="text-text-secondary text-xs sm:text-sm">Imię, email i hasło — resztę zrobimy razem.</p>
        </div>

        <div v-if="authStore.error" class="mb-4 sm:mb-5 lg:mb-6 p-3 bg-soft-coral/15 border border-soft-coral/30 !rounded-lg text-soft-coral text-xs sm:text-sm">
          {{ authStore.error }}
        </div>

        <form @submit.prevent="handleRegister" class="space-y-3 sm:space-y-4">
          <label class="block space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
            <span class="text-text-secondary">Imię</span>
            <input
              v-model="name"
              type="text"
              required
              :disabled="authStore.loading"
              class="w-full px-3 sm:px-4 py-2.5 sm:py-3 text-sm sm:text-base bg-deep-indigo/50 !rounded-lg border border-white/10 focus:border-sea-mint outline-none disabled:opacity-50"
            />
          </label>

          <label class="block space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
            <span class="text-text-secondary">Email</span>
            <input
              v-model="email"
              type="email"
              required
              :disabled="authStore.loading"
              class="w-full px-3 sm:px-4 py-2.5 sm:py-3 text-sm sm:text-base bg-deep-indigo/50 !rounded-lg sm:rounded-2xl border border-white/10 focus:border-sea-mint outline-none disabled:opacity-50"
            />
          </label>

          <label class="block space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
            <span class="text-text-secondary">Hasło</span>
            <input
              v-model="password"
              type="password"
              minlength="6"
              required
              :disabled="authStore.loading"
              class="w-full px-3 sm:px-4 py-2.5 sm:py-3 text-sm sm:text-base bg-deep-indigo/50 !rounded-lg sm:rounded-2xl border border-white/10 focus:border-sea-mint outline-none disabled:opacity-50"
            />
          </label>

          <div class="flex flex-row items-start sm:items-center justify-between gap-2 sm:gap-0 text-[0.625rem] sm:text-xs text-text-secondary">
            <span class="hidden sm:inline">🔐 Szyfrujemy transmisję danych</span>
            <span class="sm:hidden">🔐 Szyfrowane</span>
            <router-link to="/auth/login" class="text-sea-mint hover:underline whitespace-nowrap">
              Masz już konto?
            </router-link>
          </div>

          <button
            type="submit"
            :disabled="authStore.loading"
            class="w-full py-2.5 sm:py-3 !rounded-lg bg-gradient-to-r from-sea-mint to-soft-coral text-deep-indigo font-semibold text-sm sm:text-base hover:scale-[1.02] transition-transform disabled:opacity-50 disabled:hover:scale-100"
          >
            {{ authStore.loading ? 'Rejestracja...' : 'Zarejestruj się' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const name = ref('');
const email = ref('');
const password = ref('');
const onboarding = [
  { id: 1, title: 'Zaplanuj egzaminy', subtitle: 'Dodaj przedmioty, deadline\'y i tematy' },
  { id: 2, title: 'Skupiaj się z Pomodoro', subtitle: 'Sesje z podpowiedziami i asystentem AI' },
  { id: 3, title: 'Śledź postęp', subtitle: 'Statystyki, seria i tematy utknięcia' },
];

const handleRegister = async () => {
  try {
    await authStore.register({
      name: name.value,
      email: email.value,
      password: password.value,
    });
    router.push('/dashboard');
  } catch (e) {
    // Error handled in store
  }
};
</script>
