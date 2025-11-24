<template>
  <div class="theme-bg-primary text-text-primary min-h-screen overflow-hidden">
    <div class="relative">
      <div class="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent"></div>
      <div class="absolute inset-0">
        <div class="w-[20rem] sm:w-[30rem] lg:w-[40rem] h-[20rem] sm:h-[30rem] lg:h-[40rem] rounded-full bg-sea-mint/5 blur-3xl absolute -top-20 sm:-top-32 lg:-top-40 -right-5 sm:-right-8 lg:-right-10"></div>
        <div class="w-[15rem] sm:w-[25rem] lg:w-[30rem] h-[15rem] sm:h-[25rem] lg:h-[30rem] rounded-full bg-soft-coral/10 blur-3xl absolute bottom-0 left-5 sm:left-8 lg:left-10"></div>
      </div>

      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 xl:px-10 py-8 sm:py-10 lg:py-12 xl:py-16 space-y-12 sm:space-y-16 lg:space-y-20">
        <header class="flex items-center justify-between gap-3 sm:gap-4 lg:gap-6 flex-wrap">
          <div class="flex items-center gap-2 sm:gap-3 min-w-0 flex-shrink-0">
            <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-xl sm:rounded-2xl bg-gradient-to-br from-sea-mint to-soft-coral flex items-center justify-center font-bold text-deep-indigo text-xs sm:text-sm flex-shrink-0">
              FF
            </div>
            <div class="min-w-0">
              <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary truncate">FocusFlow</p>
              <p class="text-xs sm:text-sm text-soft-ice truncate">Study Flow OS</p>
            </div>
          </div>
          <nav class="hidden md:flex items-center gap-4 lg:gap-6 text-sm text-text-secondary flex-shrink-0">
            <button @click="scrollTo('features')" class="hover:text-white transition-colors whitespace-nowrap">Funkcje</button>
            <button @click="scrollTo('flow')" class="hover:text-white transition-colors whitespace-nowrap">Jak działa</button>
            <button @click="scrollTo('cta')" class="hover:text-white transition-colors whitespace-nowrap">Zacznij</button>
          </nav>
          <div v-if="isAuthenticated" class="flex items-center gap-2 sm:gap-3 lg:gap-4 flex-shrink-0">
            <div class="hidden sm:flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-1.5 sm:py-2 rounded-xl sm:rounded-2xl bg-white/5 border border-white/10 min-w-0">
              <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-xl sm:rounded-2xl bg-gradient-to-br from-soft-coral to-sea-mint text-lg sm:text-xl lg:text-2xl flex items-center justify-center flex-shrink-0">
                {{ profileAvatar }}
              </div>
              <div class="min-w-0 hidden md:block">
                <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary truncate">wracasz do flow</p>
                <p class="text-xs sm:text-sm font-semibold text-soft-ice truncate max-w-[100px] lg:max-w-none">{{ displayName }}</p>
              </div>
            </div>
            <router-link to="/dashboard" class="btn-primary text-xs sm:text-sm px-3 sm:px-4 lg:px-5 py-1.5 sm:py-2 whitespace-nowrap">
              <span class="hidden sm:inline">Otwórz dashboard</span>
              <span class="sm:hidden">Dashboard</span>
            </router-link>
          </div>
          <router-link v-else to="/auth/login" class="btn-ghost text-xs sm:text-sm px-3 sm:px-4 lg:px-5 py-1.5 sm:py-2 whitespace-nowrap flex-shrink-0">
            Zaloguj się
          </router-link>
        </header>

        <!-- Hero -->
        <section class="grid lg:grid-cols-2 gap-8 lg:gap-10 xl:gap-12 items-center">
          <div class="space-y-4 sm:space-y-5 lg:space-y-6" v-lazy-show>
            <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">zintegrowane środowisko</p>
            <h1 class="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-semibold leading-[1.1] sm:leading-tight gradient-text">
              Study Flow, który nie pozwala wypaść z fokusu
            </h1>
            <p class="text-text-secondary text-base sm:text-lg lg:text-xl max-w-2xl">
              Utwórz egzamin, uruchom Pomodoro, naciśnij "🤯 utknąłem" — i otrzymaj odpowiedź od AI bez chaosu Google.
            </p>
            <div class="flex flex-wrap gap-3 sm:gap-4">
              <router-link to="/auth/register" class="btn-primary text-sm sm:text-base px-4 sm:px-6 py-2.5 sm:py-3">
                🚀 Zacznij za darmo
              </router-link>
              <router-link to="/auth/login" class="btn-ghost text-sm sm:text-base px-4 sm:px-6 py-2.5 sm:py-3">
                Zobacz dashboard
              </router-link>
            </div>
            <div class="flex items-center gap-6 sm:gap-8 text-text-secondary text-xs sm:text-sm">
              <div>
                <p class="text-xl sm:text-2xl font-bold text-soft-ice">25 min</p>
                <p>fokus bez rozpraszania</p>
              </div>
              <div>
                <p class="text-xl sm:text-2xl font-bold text-soft-ice">30 sek</p>
                <p>odpowiedź od AI</p>
              </div>
            </div>
          </div>
          <div class="glass-card p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-5 lg:space-y-6 border border-white/5" v-lazy-show>
            <div class="bg-soft-ice/5 rounded-2xl sm:rounded-3xl p-4 sm:p-5 lg:p-6 space-y-3 sm:space-y-4">
              <p class="text-xs sm:text-sm text-text-secondary">🔥 TERAZ</p>
              <div class="flex items-center justify-between gap-2 sm:gap-3">
                <div class="min-w-0 flex-1">
                  <p class="text-base sm:text-lg font-semibold truncate">Egzamin z biologii</p>
                  <p class="text-text-secondary text-xs sm:text-sm truncate">Fotosynteza — pewność 40%</p>
                </div>
                <span class="px-2 sm:px-3 py-0.5 sm:py-1 rounded-full bg-soft-coral/20 text-soft-coral text-[0.625rem] sm:text-xs whitespace-nowrap flex-shrink-0">Priorytet</span>
              </div>
              <div class="w-full bg-white/10 rounded-full h-1.5 sm:h-2">
                <div class="h-full bg-gradient-to-r from-soft-coral to-sea-mint rounded-full w-1/2"></div>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3 sm:gap-4 text-xs sm:text-sm text-text-secondary">
              <div class="bg-white/5 rounded-xl sm:rounded-2xl p-3 sm:p-4">
                <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em]">Pomodoro</p>
                <p class="text-2xl sm:text-3xl font-mono text-soft-ice">24:35</p>
              </div>
              <div class="bg-white/5 rounded-xl sm:rounded-2xl p-3 sm:p-4">
                <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em]">Status AI</p>
                <p class="text-sm sm:text-base text-soft-ice">gotowy do pytań</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Features -->
        <section class="space-y-6 sm:space-y-8" id="features">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">funkcje</p>
              <h2 class="text-2xl sm:text-3xl lg:text-4xl font-semibold text-soft-ice">Bento Grid produktywności</h2>
            </div>
          </div>
          <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6">
            <div
              v-for="feature in features"
              :key="feature.title"
              class="glass-card p-4 sm:p-5 lg:p-6 space-y-3 sm:space-y-4 border border-white/5"
              v-lazy-show
            >
              <p class="text-sm text-text-secondary">{{ feature.label }}</p>
              <h3 class="text-xl font-semibold text-soft-ice">{{ feature.title }}</h3>
              <p class="text-text-secondary text-sm">{{ feature.copy }}</p>
            </div>
          </div>
        </section>

        <!-- Steps -->
        <section class="glass-card p-4 sm:p-6 lg:p-8 rounded-2xl sm:rounded-3xl border border-white/5 space-y-4 sm:space-y-5 lg:space-y-6" id="flow" v-lazy-show>
          <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">jak działa</p>
          <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6">
            <div
              v-for="step in flow"
              :key="step.title"
              class="p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-white/5 space-y-2"
            >
              <p class="text-sm text-text-secondary">{{ step.step }}</p>
              <h4 class="text-lg font-semibold text-soft-ice">{{ step.title }}</h4>
              <p class="text-text-secondary text-sm">{{ step.copy }}</p>
            </div>
          </div>
        </section>

        <!-- Methods -->
        <section class="space-y-6 sm:space-y-8" id="methods" v-lazy-show>
          <div class="flex flex-col gap-2 sm:gap-3">
            <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">metody uczenia się</p>
            <h2 class="text-2xl sm:text-3xl lg:text-4xl font-semibold text-soft-ice">Historie praktyk, na których zbudowano FocusFlow</h2>
            <p class="text-text-secondary text-sm sm:text-base lg:text-lg max-w-3xl">
              Zebraliśmy sprawdzone w czasie podejścia do nauki i wbudowaliśmy je w interfejs. Każdy ekran to wizualne przypomnienie
              o tym, co pomaga mózgowi utrzymać wiedzę i utrzymać tempo.
            </p>
          </div>
          <div class="grid sm:grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-5 lg:gap-6">
            <article
              v-for="method in methods"
              :key="method.title"
              class="glass-card p-4 sm:p-5 lg:p-6 border border-white/5 space-y-2 sm:space-y-3"
            >
              <div class="flex items-center justify-between">
                <h3 class="text-xl font-semibold text-soft-ice">{{ method.title }}</h3>
                <span class="text-xs text-text-secondary uppercase tracking-[0.3em]">{{ method.year }}</span>
              </div>
              <p class="text-text-secondary text-sm leading-relaxed">{{ method.copy }}</p>
              <p class="text-xs text-soft-ice/70">{{ method.usage }}</p>
            </article>
          </div>
        </section>

        <!-- CTA -->
        <section
          class="glass-card p-4 sm:p-6 lg:p-8 rounded-2xl sm:rounded-3xl border border-soft-coral/30 flex flex-col lg:flex-row items-center justify-between gap-4 sm:gap-5 lg:gap-6"
          id="cta"
          v-lazy-show
        >
          <div class="text-center lg:text-left">
            <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">gotowy do startu</p>
            <h3 class="text-2xl sm:text-3xl lg:text-4xl font-semibold text-soft-ice">Złóż sesję fokusową w 45 sekund</h3>
          </div>
          <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 w-full sm:w-auto">
            <router-link to="/auth/register" class="btn-primary text-sm sm:text-base px-4 sm:px-6 py-2.5 sm:py-3 text-center">
              ✨ Utwórz konto
            </router-link>
            <router-link to="/auth/login" class="btn-ghost text-sm sm:text-base px-4 sm:px-6 py-2.5 sm:py-3 text-center">
              Mam już login
            </router-link>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '../stores/auth';
import { usePreferencesStore } from '../stores/preferences';

const authStore = useAuthStore();
const preferencesStore = usePreferencesStore();
const { user, isAuthenticated } = storeToRefs(authStore);
const { settings: preferences } = storeToRefs(preferencesStore);

const displayName = computed(() => {
  const trimmed = user.value?.name?.trim();
  if (trimmed) return trimmed;
  const handle = user.value?.email ? user.value.email.split('@')[0] : '';
  return handle || 'Twoje konto';
});

const profileAvatar = computed(() => preferences.value.avatarEmoji || '🧠');

const scrollTo = (id: string) => {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};
const features = [
  {
    label: '01 — Priorytet',
    title: 'AI mówi, co robić teraz',
    copy: 'Karta z paskiem Soft Coral podświetla temat, który przyniesie maksymalny postęp właśnie teraz.',
  },
  {
    label: '02 — Pomodoro',
    title: 'Timer, który się nie przerywa',
    copy: 'Wbudowany przycisk «🤯 Utknąłem» daje natychmiastową odpowiedź od AI, a ostatnie 60 sekund płynnie się podświetlają.',
  },
  {
    label: '03 — Statystyki',
    title: 'Postęp i seria',
    copy: 'Zobacz ukończone egzaminy, momenty utknięcia i serię fokusu, aby nie wypaść z dynamiki.',
  },
  {
    label: '04 — Ustawienia profilu',
    title: 'Nastrój dla Ciebie',
    copy: 'Awatar emoji, motywacja i cele sesji są dostępne na każdym ekranie.',
  },
  {
    label: '05 — Bento Layout',
    title: 'Wszystko widać od razu',
    copy: 'Sidebar, topbar i karty używają jednolitej szklanej siatki — zawsze wiesz, gdzie co się znajduje.',
  },
  {
    label: '06 — Eksport fokusu',
    title: 'Działa na każdym urządzeniu',
    copy: 'Lekka kompilacja Vite i responsywny layout sprawiają, że Study Flow jest taki sam na laptopie i tablecie.',
  },
];

const flow = [
  {
    step: 'Krok 1',
    title: 'Utwórz egzamin',
    copy: 'Podziel przedmiot na tematy, oceń pewność i ustaw deadline.',
  },
  {
    step: 'Krok 2',
    title: 'Uruchom Pomodoro',
    copy: 'Skup się przez 25 minut, zaznaczaj momenty utknięcia, otrzymuj podpowiedzi.',
  },
  {
    step: 'Krok 3',
    title: 'Utrzymaj przepływ',
    copy: 'Dashboard i statystyki podpowiedzą, jaki temat wziąć dalej.',
  },
];

const methods = [
  {
    title: 'Metoda Pomodoro',
    year: 'Lata 80.',
    copy: 'Francesco Cirillo wymyślił pracę w krótkich sprintach po 25 minut. Wzmocniliśmy ideę wizualnym timerem i przyciskiem AI «Utknąłem», aby nie wypaść z rytmu.',
    usage: 'W FocusFlow: ekran timera, karty «TERAZ», przypomnienia o przerwach.',
  },
  {
    title: 'Powtórki interwałowe',
    year: '1885',
    copy: 'Hermann Ebbinghaus udowodnił, że pamięć jest silniejsza, jeśli wracamy do tematu, gdy krzywa zapominania dopiero zaczyna spadać. Dashboard proponuje tematy z niską pewnością i najbliższym deadline.',
    usage: 'W FocusFlow: lista tematów z priorytetami, podpowiedzi «czego uczyć się następnie».',
  },
  {
    title: 'Task Prioritization',
    year: '1950-2020',
    copy: 'Od macierzy Eisenhowera po współczesne Decision Frameworks — sens jest jeden: wyróżniaj najważniejsze. Nasz Bento Grid podświetla «🔥 TERAZ», aby usunąć wątpliwości przy starcie.',
    usage: 'W FocusFlow: górna karta egzaminu i wizualny postęp.',
  },
  {
    title: 'Design behawioralny',
    year: '2009',
    copy: 'BJ Fogg opisał, że działanie następuje, gdy motywacja, możliwość i wyzwalacz się zbiegają. Sidebar, seria i małe CTA tworzą te trzy zbiegi okoliczności na każdym ekranie.',
    usage: 'W FocusFlow: szklane karty, odznaki serii, szybkie CTA w modalach.',
  },
];
</script>
