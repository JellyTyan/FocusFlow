<template>
  <div class="min-h-screen text-text-primary">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-5 lg:py-6">
      <div class="grid lg:grid-cols-[minmax(200px,260px)_1fr] gap-4 sm:gap-5 lg:gap-6">
        <Sidebar />
        <div class="min-w-0" v-lazy-show>
          <Topbar />

          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-6 sm:mb-7 lg:mb-8" v-lazy-show>
            <div class="min-w-0">
              <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">Profile</p>
              <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold">Twój Study Flow</h1>
            </div>
            <div class="flex flex-wrap gap-2 sm:gap-3">
              <button
                type="button"
                class="px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg sm:rounded-xl border border-white/10 text-xs sm:text-sm font-semibold hover:border-white/30 transition-colors whitespace-nowrap"
                @click="preferencesStore.resetPreferences()"
              >
                Resetuj presety
              </button>
              <button
                type="button"
                class="px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg sm:rounded-xl bg-sea-mint/20 text-sea-mint font-semibold text-xs sm:text-sm hover:bg-sea-mint/30 transition-colors whitespace-nowrap"
                @click="handleSaveProfile"
                :disabled="isSavingProfile"
              >
                {{ isSavingProfile ? 'Zapisywanie...' : 'Zapisz' }}
              </button>
            </div>
          </div>

          <div class="grid gap-4 sm:gap-5 lg:gap-6 lg:grid-cols-[1.2fr_0.8fr]" v-lazy-show>
            <BentoCard class="p-4 sm:p-5 lg:p-6 space-y-4 sm:space-y-5 lg:space-y-6">
              <div class="flex items-start gap-3 sm:gap-4">
                <div class="text-3xl sm:text-4xl lg:text-5xl bg-white/5 rounded-2xl sm:rounded-3xl px-3 sm:px-4 py-2 sm:py-3 flex-shrink-0">
                  {{ preferences.avatarEmoji }}
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-text-secondary text-xs sm:text-sm mb-0.5 sm:mb-1">Konto</p>
                  <p class="text-xl sm:text-2xl font-semibold truncate">{{ profileForm.name || 'Bez imienia' }}</p>
                  <p class="text-text-secondary text-xs sm:text-sm truncate">{{ profileForm.email || '—' }}</p>
                </div>
              </div>

              <form @submit.prevent="handleSaveProfile" class="space-y-3 sm:space-y-4">
                <div>
                  <label class="block text-xs sm:text-sm mb-1.5 sm:mb-2 text-text-secondary">Imię</label>
                  <input
                    v-model="profileForm.name"
                    class="w-full px-3 sm:px-4 py-2.5 sm:py-3 text-sm sm:text-base rounded-xl sm:rounded-2xl bg-deep-indigo/50 border border-white/10 focus:border-sea-mint outline-none"
                    placeholder="Jak do Ciebie się zwracać?"
                  />
                </div>
                <div>
                  <label class="block text-xs sm:text-sm mb-1.5 sm:mb-2 text-text-secondary">Email</label>
                  <input
                    v-model="profileForm.email"
                    disabled
                    class="w-full px-3 sm:px-4 py-2.5 sm:py-3 text-sm sm:text-base rounded-xl sm:rounded-2xl bg-deep-indigo/30 border border-white/10 text-text-secondary cursor-not-allowed"
                  />
                </div>
                <div class="flex flex-wrap items-center gap-2 sm:gap-3 text-xs sm:text-sm">
                  <span class="text-text-secondary">Awatar</span>
                  <button
                    v-for="emoji in emojiOptions"
                    :key="emoji"
                    type="button"
                    class="px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-lg sm:rounded-xl border transition-all text-lg sm:text-xl"
                    :class="preferences.avatarEmoji === emoji ? 'border-sea-mint bg-sea-mint/10' : 'border-white/10 hover:border-white/30'"
                    @click="preferencesStore.setPreference('avatarEmoji', emoji)"
                  >
                    {{ emoji }}
                  </button>
                </div>
                <p v-if="profileError" class="text-soft-coral text-xs sm:text-sm">{{ profileError }}</p>
                <p v-else-if="profileSuccess" class="text-sea-mint text-xs sm:text-sm">Profil zaktualizowany ✨</p>
              </form>
            </BentoCard>

            <BentoCard class="p-4 sm:p-5 lg:p-6 space-y-3 sm:space-y-4">
              <p class="text-text-secondary text-xs sm:text-sm">Podsumowanie postępu</p>
              <div class="grid grid-cols-2 gap-2 sm:gap-3 lg:gap-4">
                <div class="p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-white/5 border border-white/10">
                  <p class="text-[0.625rem] sm:text-xs text-text-secondary mb-0.5 sm:mb-1">Aktywne egzaminy</p>
                  <p class="text-2xl sm:text-3xl font-bold">{{ activeExams }}</p>
                </div>
                <div class="p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-white/5 border border-white/10">
                  <p class="text-[0.625rem] sm:text-xs text-text-secondary mb-0.5 sm:mb-1">Ukończono</p>
                  <p class="text-2xl sm:text-3xl font-bold text-sea-mint">{{ completedExams }}</p>
                </div>
                <div class="p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-white/5 border border-white/10">
                  <p class="text-[0.625rem] sm:text-xs text-text-secondary mb-0.5 sm:mb-1">Tematów przestudiowanych</p>
                  <p class="text-2xl sm:text-3xl font-bold">{{ completedTopics }}</p>
                </div>
                <div class="p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-white/5 border border-white/10">
                  <p class="text-[0.625rem] sm:text-xs text-text-secondary mb-0.5 sm:mb-1">Cel w godzinach</p>
                  <p class="text-2xl sm:text-3xl font-bold">{{ preferences.dailyFocusGoal }}h</p>
                </div>
              </div>
              <div class="flex items-center justify-between rounded-xl sm:rounded-2xl bg-soft-coral/10 border border-soft-coral/30 px-3 sm:px-4 py-2 sm:py-3">
                <div>
                  <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-soft-coral/90">Streak</p>
                  <p class="text-xl sm:text-2xl font-bold">{{ focusStreak }} dni</p>
                </div>
                <span class="text-2xl sm:text-3xl">🔥</span>
              </div>
            </BentoCard>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-5 lg:gap-6 mt-4 sm:mt-5 lg:mt-6" v-lazy-show>
            <BentoCard class="p-4 sm:p-5 lg:p-6 space-y-4 sm:space-y-5 lg:space-y-6">
              <div class="flex items-center justify-between gap-2 sm:gap-3">
                <div class="min-w-0">
                  <p class="text-text-secondary text-xs sm:text-sm">Atmosfera fokusu</p>
                  <p class="text-lg sm:text-xl font-semibold">Wybierz nastrój</p>
                </div>
                <span class="text-sm text-text-secondary">{{ focusThemeLabel }}</span>
              </div>

              <div class="relative rounded-2xl sm:rounded-3xl border border-white/10 overflow-hidden min-h-[140px] sm:min-h-[160px] lg:min-h-[180px]" style="background-color: var(--theme-bg-secondary);">
                <div class="absolute inset-0 opacity-60 blur-3xl theme-bg-gradient"></div>
                <div class="relative z-10 p-4 sm:p-5 lg:p-6 space-y-2 sm:space-y-3">
                  <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">aktualny klimat</p>
                  <p class="text-xl sm:text-2xl font-semibold">{{ activeFocusTheme.title }}</p>
                  <p class="text-text-secondary text-xs sm:text-sm">{{ activeSoundscape.description }}</p>
                  <div class="flex flex-wrap gap-1.5 sm:gap-2 text-[0.625rem] sm:text-xs">
                    <span class="inline-flex items-center gap-1 px-2 sm:px-3 py-0.5 sm:py-1 rounded-full bg-white/10 border border-white/20">
                      <span>{{ activeSoundscape.icon }}</span>
                      <span>{{ activeSoundscape.label }}</span>
                    </span>
                    <span class="inline-flex items-center gap-1 px-2 sm:px-3 py-0.5 sm:py-1 rounded-full bg-white/10 border border-white/20">
                      <span>intensywność</span>
                      <span>{{ preferencesProxy.ambienceLevel }}/5</span>
                    </span>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3">
                <button
                  v-for="theme in focusThemes"
                  :key="theme.id"
                  type="button"
                  class="rounded-xl sm:rounded-2xl p-3 sm:p-4 border text-left transition-all"
                  :class="preferences.focusTheme === theme.id ? 'border-sea-mint bg-sea-mint/10 ' + theme.aura : 'border-white/10 hover:border-white/30'"
                  @click="preferencesStore.setPreference('focusTheme', theme.id)"
                >
                  <p class="text-sm sm:text-base font-semibold mb-0.5 sm:mb-1">{{ theme.title }}</p>
                  <p class="text-[0.625rem] sm:text-xs text-text-secondary">{{ theme.subtitle }}</p>
                </button>
              </div>

              <div class="space-y-2 sm:space-y-3">
                <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">dźwięk tła</p>
                <div class="flex flex-wrap gap-2 sm:gap-3">
                  <button
                    v-for="sound in focusSoundscapes"
                    :key="sound.id"
                    type="button"
                    class="px-3 sm:px-4 py-1.5 sm:py-2 rounded-xl sm:rounded-2xl border text-xs sm:text-sm transition-all inline-flex items-center gap-1.5 sm:gap-2"
                    :class="preferences.focusSoundscape === sound.id ? 'border-sea-mint bg-sea-mint/10 text-sea-mint' : 'border-white/10 hover:border-white/30'"
                    @click="preferencesStore.setPreference('focusSoundscape', sound.id)"
                  >
                    <span>{{ sound.icon }}</span>
                    <span>{{ sound.label }}</span>
                  </button>
                </div>
              </div>

              <div>
                <div class="flex items-center justify-between text-xs sm:text-sm text-text-secondary mb-1.5 sm:mb-2">
                  <span>Intensywność animacji</span>
                  <span>{{ preferencesProxy.ambienceLevel }}/5</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="5"
                  step="1"
                  v-model.number="preferencesProxy.ambienceLevel"
                  class="w-full accent-sea-mint"
                  @change="handleAmbienceChange"
                />
                <p class="text-[0.625rem] sm:text-xs text-text-secondary mt-1">{{ ambienceInsight }}</p>
              </div>
            </BentoCard>

            <BentoCard class="p-4 sm:p-5 lg:p-6 space-y-4 sm:space-y-5 lg:space-y-6">
              <div class="flex items-center justify-between gap-2 sm:gap-3">
                <div class="min-w-0">
                  <p class="text-text-secondary text-xs sm:text-sm">Motywacja</p>
                  <p class="text-lg sm:text-xl font-semibold">Zdefiniuj ton i rytm</p>
                </div>
                <span class="text-xs sm:text-sm text-text-secondary flex-shrink-0">{{ motivationModeDetail.label }}</span>
              </div>

              <div class="rounded-xl sm:rounded-2xl border border-white/10 bg-white/5 p-4 sm:p-5 space-y-2 sm:space-y-3">
                <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">{{ activeMantra.label }}</p>
                <p class="text-base sm:text-lg font-semibold text-soft-ice leading-snug">"{{ activeMantra.quote }}"</p>
                <div class="flex flex-wrap gap-2 sm:gap-3 text-[0.625rem] sm:text-xs text-text-secondary">
                  <span>{{ motivationModeDetail.copy }}</span>
                  <span>Energia {{ preferencesProxy.motivationPulse }}/10</span>
                </div>
              </div>

              <div class="space-y-2 sm:space-y-3">
                <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">ton wsparcia</p>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="mode in motivationModes"
                    :key="mode.id"
                    type="button"
                    class="px-3 sm:px-4 py-1.5 sm:py-2 rounded-xl sm:rounded-2xl border text-xs sm:text-sm transition-all"
                    :class="preferences.motivationMode === mode.id ? 'border-soft-coral bg-soft-coral/10 text-soft-coral' : 'border-white/10 hover:border-white/30'"
                    @click="preferencesStore.setPreference('motivationMode', mode.id)"
                  >
                    {{ mode.label }}
                  </button>
                </div>
                <p class="text-[0.625rem] sm:text-xs text-text-secondary">{{ motivationModeDetail.copy }}</p>
              </div>

              <div class="space-y-2 sm:space-y-3">
                <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">mantra dnia</p>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3">
                  <button
                    v-for="mantra in mantraOptions"
                    :key="mantra.id"
                    type="button"
                    class="rounded-xl sm:rounded-2xl p-3 sm:p-4 border text-left transition-all"
                    :class="preferences.motivationMantra === mantra.id ? 'border-soft-coral bg-soft-coral/10' : 'border-white/10 hover:border-white/30'"
                    @click="preferencesStore.setPreference('motivationMantra', mantra.id)"
                  >
                    <p class="text-sm sm:text-base font-semibold mb-0.5 sm:mb-1">{{ mantra.label }}</p>
                    <p class="text-[0.625rem] sm:text-xs text-text-secondary leading-snug">"{{ mantra.quote }}"</p>
                  </button>
                </div>
              </div>

              <div>
                <div class="flex items-center justify-between text-xs sm:text-sm text-text-secondary mb-1.5 sm:mb-2">
                  <span>Poziom energii komunikatów</span>
                  <span>{{ preferencesProxy.motivationPulse }}/10</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  v-model.number="preferencesProxy.motivationPulse"
                  class="w-full accent-soft-coral"
                  @change="handleMotivationPulseChange"
                />
                <p class="text-[0.625rem] sm:text-xs text-text-secondary mt-1">{{ motivationPulseInsight }}</p>
              </div>

              <div>
                <div class="flex items-center justify-between text-xs sm:text-sm text-text-secondary mb-1.5 sm:mb-2">
                  <span>Dzienny cel fokusu</span>
                  <span>{{ preferencesProxy.dailyFocusGoal }} h</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="6"
                  step="1"
                  v-model.number="preferencesProxy.dailyFocusGoal"
                  class="w-full accent-sea-mint"
                  @change="preferencesStore.setPreference('dailyFocusGoal', preferencesProxy.dailyFocusGoal)"
                />
              </div>
            </BentoCard>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
import Topbar from '../../components/layout/Topbar.vue';
import Sidebar from '../../components/layout/Sidebar.vue';
import BentoCard from '../../components/common/BentoCard.vue';
import { useAuthStore } from '../../stores/auth';
import { useProjectsStore } from '../../stores/projects';
import { usePreferencesStore } from '../../stores/preferences';

const authStore = useAuthStore();
const projectsStore = useProjectsStore();
const preferencesStore = usePreferencesStore();
const { settings: preferences } = storeToRefs(preferencesStore);

const profileForm = ref({
  name: '',
  email: '',
});

const profileError = ref<string | null>(null);
const profileSuccess = ref(false);
const isSavingProfile = ref(false);

const emojiOptions = ['🧠', '🚀', '📚', '💡', '🛰', '🌙'];

const focusThemes = [
  {
    id: 'deep-space',
    title: 'Deep Space',
    subtitle: 'Granat + szkło',
    gradient: 'linear-gradient(135deg, rgba(13,18,45,0.95), rgba(4,7,15,0.9))',
    aura: 'shadow-[0_0_80px_rgba(88,113,255,0.25)]',
  },
  {
    id: 'dawn',
    title: 'Aurora Dawn',
    subtitle: 'Ciepły świt',
    gradient: 'linear-gradient(135deg, rgba(255,136,102,0.7), rgba(102,204,182,0.45))',
    aura: 'shadow-[0_0_80px_rgba(255,136,102,0.25)]',
  },
  {
    id: 'minimal',
    title: 'Minimal Mono',
    subtitle: 'Czyste szkło',
    gradient: 'linear-gradient(135deg, rgba(17,22,40,0.85), rgba(6,9,20,0.85))',
    aura: 'shadow-[0_0_80px_rgba(255,255,255,0.12)]',
  },
] as const;

const focusSoundscapes = [
  { id: 'lofi', label: 'Lo-fi nocą', description: 'miękkie beaty i cichy szum miasta', icon: '🎧' },
  { id: 'rain', label: 'Deszcz & błysk', description: 'kojące krople z delikatnymi syntezami', icon: '🌧' },
  { id: 'silence', label: 'Cisza studyjna', description: 'tylko puls światła i timer', icon: '🌙' },
] as const;

const motivationModes = [
  { id: 'calm', label: 'Calm mentor', copy: 'Spokojne, ciche przypomnienia' },
  { id: 'coach', label: 'Coach', copy: 'Konkretny plan działania' },
  { id: 'hype', label: 'Hype squad', copy: 'Energia i emoji' },
] as const;

const mantraOptions = [
  { id: 'flow', label: 'Tryb Flow', quote: 'Liczy się tylko następne 25 minut.' },
  { id: 'clarity', label: 'Jasność', quote: 'Porządkuj temat, nie emocje.' },
  { id: 'legacy', label: 'Legacy', quote: 'Każda sesja dokłada cegłę do wyniku.' },
] as const;

const preferencesProxy = ref({
  dailyFocusGoal: preferences.value.dailyFocusGoal,
  ambienceLevel: preferences.value.ambienceLevel,
  motivationPulse: preferences.value.motivationPulse,
});

watch(
  () => preferences.value.dailyFocusGoal,
  newGoal => {
    preferencesProxy.value.dailyFocusGoal = newGoal;
  }
);

watch(
  () => preferences.value.ambienceLevel,
  newLevel => {
    preferencesProxy.value.ambienceLevel = newLevel;
  }
);

watch(
  () => preferences.value.motivationPulse,
  newPulse => {
    preferencesProxy.value.motivationPulse = newPulse;
  }
);

watch(
  () => authStore.user,
  user => {
    profileForm.value.name = user?.name ?? '';
    profileForm.value.email = user?.email ?? '';
  },
  { immediate: true }
);

onMounted(async () => {
  if (!authStore.user && !authStore.loading) {
    await authStore.fetchCurrentUser();
  }
  if (!Array.isArray(projectsStore.projects) || !projectsStore.projects.length) {
    await projectsStore.fetchProjects();
  }
});

const activeExams = computed(() => {
  if (!Array.isArray(projectsStore.projects)) return 0;
  return projectsStore.projects.filter(project => !project.completed).length;
});
const completedExams = computed(() => {
  if (!Array.isArray(projectsStore.projects)) return 0;
  return projectsStore.projects.filter(project => project.completed).length;
});
const completedTopics = computed(() => {
  if (!Array.isArray(projectsStore.projects)) return 0;
  return projectsStore.projects.reduce(
    (sum, project) => sum + project.topics.filter(topic => topic.completed).length,
    0
  );
});

const focusStreak = computed(() => Math.max(completedExams.value, 1));

const focusThemeLabel = computed(() => {
  const theme = focusThemes.find(item => item.id === preferences.value.focusTheme);
  return theme ? theme.title : '—';
});

const activeFocusTheme = computed(() => focusThemes.find(theme => theme.id === preferences.value.focusTheme) ?? focusThemes[0]);
const activeSoundscape =
  computed(() => focusSoundscapes.find(sound => sound.id === preferences.value.focusSoundscape) ?? focusSoundscapes[0]);

const ambienceInsight = computed(() => {
  const level = preferencesProxy.value.ambienceLevel;
  if (level <= 2) return 'Delikatna mgła — zero rozpraszaczy.';
  if (level === 3) return 'Balans: animacje reagują na timer, ale nie atakują.';
  return 'Świetlne fale pulsują z muzyką, dobry wybór na wieczór.';
});

const motivationModeDetail = computed(
  () => motivationModes.find(mode => mode.id === preferences.value.motivationMode) ?? motivationModes[0]
);

const activeMantra =
  computed(() => mantraOptions.find(mantra => mantra.id === preferences.value.motivationMantra) ?? mantraOptions[0]);

const motivationPulseInsight = computed(() => {
  const pulse = preferencesProxy.value.motivationPulse;
  if (pulse <= 3) return 'Ton spokojny, żadnych emoji — jak mentor, który siedzi obok.';
  if (pulse <= 6) return 'Krótkie, konkretne zdania przypominają o celu sesji.';
  return 'Pełna energia, skróty i emoji dopingują każdą przerwę.';
});

const handleSaveProfile = async () => {
  if (!profileForm.value.name.trim()) {
    profileError.value = 'Imię nie może być puste';
    return;
  }
  profileError.value = null;
  profileSuccess.value = false;
  isSavingProfile.value = true;
  try {
    await authStore.updateProfile({ name: profileForm.value.name.trim() });
    profileSuccess.value = true;
    setTimeout(() => {
      profileSuccess.value = false;
    }, 3000);
  } catch (e) {
    profileError.value = authStore.error || 'Nie udało się zapisać profilu';
  } finally {
    isSavingProfile.value = false;
  }
};


const handleAmbienceChange = () => {
  preferencesStore.setPreference('ambienceLevel', preferencesProxy.value.ambienceLevel);
};

const handleMotivationPulseChange = () => {
  preferencesStore.setPreference('motivationPulse', preferencesProxy.value.motivationPulse);
};
</script>
