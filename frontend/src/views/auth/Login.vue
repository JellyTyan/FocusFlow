<template>
  <div class="min-h-screen theme-bg-primary text-text-primary relative overflow-hidden">
    <div class="absolute inset-0 theme-bg-gradient-overlay"></div>
    <div class="absolute inset-0 pointer-events-none">
      <div class="w-[15rem] sm:w-[25rem] lg:w-96 h-[15rem] sm:h-[25rem] lg:h-96 bg-soft-coral/20 rounded-full blur-3xl absolute -top-10 sm:-top-16 lg:-top-20 -right-5 sm:-right-8 lg:-right-12"></div>
      <div class="w-[12rem] sm:w-[20rem] lg:w-80 h-[12rem] sm:h-[20rem] lg:h-80 bg-sea-mint/10 rounded-full blur-3xl absolute bottom-0 left-3 sm:left-5 lg:left-6"></div>
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


    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-14 lg:py-12 xl:py-16 grid gap-8 sm:gap-10 lg:gap-12 lg:grid-cols-[1.1fr_0.9fr] items-center min-h-screen">
      <div class="space-y-4 sm:space-y-5 lg:space-y-6 order-2 lg:order-1">
        <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.6em] text-text-secondary">Welcome back</p>
        <h1 class="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold leading-[1.1] sm:leading-tight">
          Zaloguj się do <span class="text-transparent bg-clip-text bg-gradient-to-r from-sea-mint to-soft-coral">Focus Flow</span>
          i kontynuuj przygotowania bez porażek.
        </h1>
        <p class="text-text-secondary text-base sm:text-lg lg:text-xl">
          Study Flow zbiera egzaminy, Pomodoro, statystyki i asystenta AI w jeden szklany panel. Kontynuuj tam, gdzie skończyłeś.
        </p>

        <div class="grid sm:grid-cols-2 gap-3 sm:gap-4">
          <div
            v-for="feature in highlights"
            :key="feature.title"
            class="p-3 sm:p-4 !rounded-lg bg-white/5 border border-white/10 backdrop-blur-md"
          >
            <p class="text-sm sm:text-base text-soft-ice font-semibold mb-1">{{ feature.title }}</p>
            <p class="text-xs sm:text-sm text-text-secondary">{{ feature.subtitle }}</p>
          </div>
        </div>
      </div>

      <div class="glass-card p-4 sm:p-6 lg:p-8 !rounded-lg border border-white/10 shadow-2xl shadow-soft-coral/5 order-1 lg:order-2 w-full">
        <div class="space-y-2 mb-4 sm:mb-5 lg:mb-6">
          <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">Logowanie</p>
          <h2 class="text-2xl sm:text-3xl font-bold">Kontynuuj przepływ</h2>
          <p class="text-text-secondary text-xs sm:text-sm">Skoncentruj się na sesji — interfejs Cię wspiera.</p>
        </div>

        <div v-if="authStore.error" class="mb-4 sm:mb-5 lg:mb-6 p-3 bg-soft-coral/15 border border-soft-coral/30 !rounded-lg text-soft-coral text-xs sm:text-sm">
          {{ authStore.error }}
        </div>

        <form @submit.prevent="handleLogin" class="space-y-3 sm:space-y-4">
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
              required
              :disabled="authStore.loading"
              class="w-full px-3 sm:px-4 py-2.5 sm:py-3 text-sm sm:text-base bg-deep-indigo/50 !rounded-lg sm:rounded-2xl border border-white/10 focus:border-sea-mint outline-none disabled:opacity-50"
            />
          </label>

          <div class="flex flex-row items-start sm:items-center justify-between gap-2 sm:gap-0 text-[0.625rem] sm:text-xs text-text-secondary">
            <span class="hidden sm:inline">🔐 Szyfrujemy transmisję danych</span>
            <span class="sm:hidden">🔐 Szyfrowane</span>
            <router-link to="/auth/register" class="text-sea-mint hover:underline whitespace-nowrap">
              Nie masz konta?
            </router-link>
          </div>

          <button
            type="submit"
            :disabled="authStore.loading"
            class="w-full py-2.5 sm:py-3 !rounded-lg sm:rounded-2xl bg-gradient-to-r from-sea-mint to-soft-coral text-deep-indigo font-semibold text-sm sm:text-base hover:scale-[1.02] transition-transform disabled:opacity-50 disabled:hover:scale-100"
          >
            {{ authStore.loading ? 'Logowanie...' : 'Zaloguj się' }}
          </button>
        </form>

        <div class="mt-4 sm:mt-5 text-center text-text-secondary text-[0.625rem] sm:text-xs lg:text-sm">
          Kontynuując, akceptujesz filozofię FocusFlow: małe zwycięstwa są codzienne.
        </div>
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
const email = ref('');
const password = ref('');
const highlights = [
  { title: 'Bento Dashboard', subtitle: 'Kontrola egzaminów, tematów i deadline\'ów w jednej siatce' },
  { title: 'Pomodoro + AI', subtitle: 'Sesje z podpowiedziami i natychmiastowy czat-asystent' },
  { title: 'Statystyki', subtitle: 'Seria fokusu, momenty utknięcia i postęp' },
  { title: 'Personalizacja', subtitle: 'Tematy, nastrój, motywacja — wszystko się konfiguruje' },
];

const handleLogin = async () => {
  try {
    await authStore.login({ email: email.value, password: password.value });
    router.push('/dashboard');
  } catch (e) {
    // Error handled in store
  }
};
</script>
