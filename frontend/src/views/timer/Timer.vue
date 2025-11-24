<template>
  <div class="min-h-screen theme-bg-primary text-text-primary relative overflow-hidden">
    <div class="absolute inset-0 theme-bg-gradient-overlay" style="opacity: 0.95;"></div>
    <div class="absolute inset-0">
      <div class="w-[15rem] sm:w-[25rem] lg:w-96 h-[15rem] sm:h-[25rem] lg:h-96 bg-soft-coral/10 rounded-full blur-3xl absolute -top-8 sm:-top-12 lg:-top-16 -right-5 sm:-right-8 lg:-right-10"></div>
      <div class="w-[12rem] sm:w-[20rem] lg:w-80 h-[12rem] sm:h-[20rem] lg:h-80 bg-sea-mint/10 rounded-full blur-3xl absolute bottom-0 left-5 sm:left-8 lg:left-10"></div>
    </div>

    <div class="relative z-10 max-w-8xl mx-auto py-6 sm:py-8 lg:py-10 px-4 sm:px-6 lg:px-8">
      <div class="space-y-4 sm:space-y-5 lg:space-y-6" v-lazy-show>
        <div class="flex items-center justify-between gap-3 sm:gap-4">
          <div class="space-y-0.5 sm:space-y-1 min-w-0 flex-1">
            <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">Pomodoro</p>
            <h1 class="text-2xl sm:text-3xl font-bold text-soft-ice truncate">Sesja fokusu</h1>
          </div>
          <button
            @click="router.push('/dashboard')"
            class="px-3 sm:px-4 lg:px-5 py-1.5 sm:py-2 rounded-xl sm:rounded-2xl border border-white/15 text-xs sm:text-sm text-text-secondary hover:border-white/40 transition-colors whitespace-nowrap flex-shrink-0"
          >
            <span class="hidden sm:inline">← Do egzaminów</span>
            <span class="sm:hidden">←</span>
          </button>
        </div>

        <div v-if="error" class="glass-card text-center py-12 rounded-3xl border border-soft-coral/40">
          <div class="text-soft-coral text-xl mb-4">{{ error }}</div>
          <button @click="router.push('/dashboard')" class="px-6 py-3 bg-soft-coral text-white rounded-xl">
            Wróć do Dashboard
          </button>
        </div>

        <div v-else-if="loading" class="glass-card text-center py-12 rounded-3xl border border-soft-ice/10">
          <div class="text-sea-mint text-xl">Ładowanie...</div>
        </div>

        <div v-else class="grid grid-cols-1 xl:grid-cols-[1.7fr_0.9fr] gap-4 sm:gap-5 lg:gap-6 xl:gap-8 items-start">
          <!-- Timer card -->
          <div class="glass-card rounded-2xl sm:rounded-3xl border border-soft-ice/10 p-4 sm:p-6 lg:p-8 xl:p-10 space-y-6 sm:space-y-8 lg:space-y-10">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3 sm:gap-4">
            <div class="min-w-0 flex-1">
              <p class="text-xs sm:text-sm uppercase tracking-[0.4em] text-text-secondary">SESJA FOKUSU</p>
              <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-soft-ice mt-1 sm:mt-2 truncate">{{ topicName }}</h1>
              <p class="text-text-secondary text-xs sm:text-sm mt-1">25 minut pomodoro • {{ timerStore.isRunning ? 'w trakcie' : timerStore.isPaused ? 'pauza' : 'gotowy do startu' }}</p>
            </div>
            <div class="flex items-center gap-2 bg-soft-ice/5 rounded-full px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm flex-shrink-0">
              <span class="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full" :class="timerStore.isRunning ? 'bg-sea-mint animate-pulse' : 'bg-soft-ice/40'"></span>
              <span class="hidden sm:inline">{{ timerStore.isRunning ? 'Timer aktywny' : timerStore.isPaused ? 'Na pauzie' : 'Oczekuje na uruchomienie' }}</span>
              <span class="sm:hidden">{{ timerStore.isRunning ? 'Aktywny' : timerStore.isPaused ? 'Pauza' : 'Gotowy' }}</span>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8 lg:gap-10">
            <div class="flex flex-col items-center justify-center gap-4 sm:gap-5 lg:gap-6">
              <div class="relative flex items-center justify-center">
                <div
                  class="w-48 h-48 sm:w-56 sm:h-56 lg:w-64 lg:h-64 rounded-full border border-soft-ice/5 p-1"
                  :style="progressRingStyle"
                >
                  <div class="w-full h-full rounded-full bg-[#0b1220] flex items-center justify-center flex-col gap-1 sm:gap-2">
                    <span class="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-mono font-bold" :class="timerStore.isLastMinute ? 'text-soft-coral' : 'text-sea-mint'">
                      {{ timerStore.formattedTime }}
                    </span>
                    <span class="text-text-secondary text-[0.625rem] sm:text-xs uppercase tracking-[0.4em]">Pomodoro</span>
                  </div>
                </div>
                <div class="absolute -bottom-4 sm:-bottom-6 bg-soft-ice/10 rounded-full px-3 sm:px-4 py-0.5 sm:py-1 text-[0.625rem] sm:text-xs text-text-secondary">
                  Postęp {{ Math.round(timerStore.progress) }}%
                </div>
              </div>

              <div class="flex flex-wrap items-center justify-center gap-2 sm:gap-3 w-full">
                <button
                  v-if="!timerStore.isRunning && !timerStore.isPaused"
                  @click="handleStart"
                  class="px-6 sm:px-8 lg:px-10 py-2.5 sm:py-3 rounded-full bg-gradient-to-r from-sea-mint to-soft-coral text-deep-indigo font-semibold text-sm sm:text-base shadow-lg shadow-soft-coral/30 hover:scale-105 transition-transform w-full sm:w-auto"
                >
                  ▶ Zacznij fokus
                </button>
                <template v-else>
                  <button
                    v-if="timerStore.isRunning"
                    @click="timerStore.pause()"
                    class="px-5 sm:px-6 lg:px-8 py-2 sm:py-2.5 lg:py-3 rounded-full bg-soft-ice/10 hover:bg-soft-ice/20 transition-colors text-xs sm:text-sm w-full sm:w-auto"
                  >
                    ⏸ Pauza
                  </button>
                  <button
                    v-if="timerStore.isPaused"
                    @click="timerStore.resume()"
                    class="px-5 sm:px-6 lg:px-8 py-2 sm:py-2.5 lg:py-3 rounded-full bg-sea-mint/90 text-deep-indigo font-semibold text-xs sm:text-sm hover:scale-105 transition-transform w-full sm:w-auto"
                  >
                    ▶ Kontynuuj
                  </button>
                  <button
                    @click="handleStop"
                    class="px-5 sm:px-6 lg:px-8 py-2 sm:py-2.5 lg:py-3 rounded-full bg-soft-coral/20 text-soft-coral hover:bg-soft-coral/30 transition-colors text-xs sm:text-sm w-full sm:w-auto"
                  >
                    ⏹ Zakończ
                  </button>
                </template>
                <button
                  v-if="timerStore.isRunning || timerStore.isPaused"
                  @click="timerStore.toggleAIChat()"
                  class="px-5 sm:px-6 lg:px-8 py-2 sm:py-2.5 lg:py-3 rounded-full border border-soft-coral/50 text-soft-coral hover:bg-soft-coral/10 transition-colors text-xs sm:text-sm w-full sm:w-auto"
                >
                  🤯 Utknąłem
                </button>
              </div>
            </div>

            <div class="space-y-4 sm:space-y-5 lg:space-y-6">
              <div class="bg-soft-ice/5 rounded-xl sm:rounded-2xl p-3 sm:p-4 space-y-3 sm:space-y-4">
                <div class="flex items-center justify-between text-xs sm:text-sm text-text-secondary uppercase tracking-[0.3em]">
                  <span>Stan</span>
                  <span>{{ timerStore.isRunning ? 'W trakcie' : timerStore.isPaused ? 'Pauza' : 'Oczekiwanie' }}</span>
                </div>
                <div class="grid grid-cols-2 gap-2 sm:gap-3 text-left">
                  <div class="p-2.5 sm:p-3 rounded-lg sm:rounded-xl bg-soft-ice/5">
                    <p class="text-[0.625rem] sm:text-xs text-text-secondary">Pozostało</p>
                    <p class="text-lg sm:text-xl font-semibold text-soft-ice">{{ timerStore.formattedTime }}</p>
                  </div>
                  <div class="p-2.5 sm:p-3 rounded-lg sm:rounded-xl bg-soft-ice/5">
                    <p class="text-[0.625rem] sm:text-xs text-text-secondary">Fokus</p>
                    <p class="text-lg sm:text-xl font-semibold text-soft-ice">
                      {{ timerStore.session?.stuck_moments || 0 }} utknięć
                    </p>
                  </div>
                  <div class="p-2.5 sm:p-3 rounded-lg sm:rounded-xl bg-soft-ice/5">
                    <p class="text-[0.625rem] sm:text-xs text-text-secondary">Sesja</p>
                    <p class="text-lg sm:text-xl font-semibold text-soft-ice">25 min</p>
                  </div>
                  <div class="p-2.5 sm:p-3 rounded-lg sm:rounded-xl bg-soft-ice/5">
                    <p class="text-[0.625rem] sm:text-xs text-text-secondary">Tryb</p>
                    <p class="text-lg sm:text-xl font-semibold text-soft-ice">Pomodoro</p>
                  </div>
                </div>
              </div>

              <div class="bg-soft-ice/5 rounded-xl sm:rounded-2xl p-3 sm:p-4 space-y-3 sm:space-y-4">
                <div class="flex items-center justify-between">
                  <p class="text-text-secondary text-xs sm:text-sm uppercase tracking-[0.3em]">Rada</p>
                  <span class="text-[0.625rem] sm:text-xs text-soft-ice/60">Zachowaj fokus</span>
                </div>
                <p class="text-sm sm:text-base text-soft-ice font-semibold">{{ focusTip?.title }}</p>
                <p class="text-text-secondary text-xs sm:text-sm">{{ focusTip?.body }}</p>
                <div class="w-full bg-soft-ice/10 rounded-full h-1 overflow-hidden">
                  <div class="h-full bg-soft-coral/60 animate-pulse"></div>
                </div>
              </div>
            </div>
          </div>
          </div>

          <!-- Side column -->
          <div class="space-y-4 sm:space-y-5 lg:space-y-6">
            <div class="glass-card rounded-2xl sm:rounded-3xl border border-soft-ice/10 bg-soft-ice/5 p-4 sm:p-5 lg:p-6 space-y-3 sm:space-y-4">
              <h3 class="text-lg sm:text-xl font-bold">Postęp fokusu</h3>
              <div class="space-y-2 sm:space-y-3">
                <div class="flex items-center justify-between text-xs sm:text-sm text-text-secondary">
                  <span>Bieżąca sesja</span>
                  <span>{{ Math.round(timerStore.progress) }}%</span>
                </div>
                <div class="w-full bg-soft-ice/10 rounded-full h-1.5 sm:h-2 overflow-hidden">
                  <div
                    class="h-full bg-gradient-to-r from-sea-mint to-soft-coral transition-all"
                    :style="{ width: `${timerStore.progress}%` }"
                  ></div>
                </div>
                <div class="text-[0.625rem] sm:text-xs text-text-secondary">
                  Pamiętaj: ostatnie 60 sekund zabarwią się na koralowy kolor – meta już blisko ✨
                </div>
              </div>
            </div>

            <div class="glass-card rounded-2xl sm:rounded-3xl border border-soft-ice/10 bg-soft-ice/5 p-4 sm:p-5 lg:p-6 space-y-3 sm:space-y-4">
              <h3 class="text-lg sm:text-xl font-bold">Sesja</h3>
              <ul class="space-y-2 sm:space-y-3 text-xs sm:text-sm text-text-secondary">
                <li class="flex items-center justify-between gap-2">
                  <span>Temat</span>
                  <span class="text-soft-ice font-semibold truncate text-right min-w-0 flex-1 ml-2">{{ topicName }}</span>
                </li>
                <li class="flex items-center justify-between">
                  <span>Utknięć</span>
                  <span class="text-soft-ice font-semibold">{{ timerStore.session?.stuck_moments || 0 }}</span>
                </li>
                <li class="flex items-center justify-between">
                  <span>Status</span>
                  <span class="text-soft-ice font-semibold">{{ timerStore.isRunning ? 'W trakcie' : timerStore.isPaused ? 'Pauza' : 'Oczekiwanie' }}</span>
                </li>
              </ul>
            </div>

            <div class="glass-card rounded-2xl sm:rounded-3xl border border-soft-ice/10 bg-soft-ice/5 p-4 sm:p-5 lg:p-6 space-y-3 sm:space-y-4">
              <div class="flex items-center justify-between">
                <h3 class="text-lg sm:text-xl font-bold">🎧 Lo-fi atmosfera</h3>
                <span class="text-[0.625rem] sm:text-xs text-text-secondary px-2 py-1 rounded-full bg-white/5">
                  {{ isAudioPlaying ? '● Odtwarzanie' : '⏸ Pauza' }}
                </span>
              </div>
              <audio
                ref="audioPlayer"
                autoplay
                crossorigin="anonymous"
                class="hidden"
              >
                <source src="https://live.proradiosonline.com/listen/lofi_radio/aac" type="audio/aac">
              </audio>
              <div class="space-y-2 sm:space-y-3">
                <div class="flex items-center gap-2 sm:gap-3">
                  <button
                    @click="toggleAudio"
                    :class="[
                      'w-10 h-10 sm:w-12 sm:h-12 rounded-full font-semibold flex items-center justify-center hover:scale-105 transition-all shadow-lg flex-shrink-0',
                      isAudioPlaying
                        ? 'bg-gradient-to-r from-soft-coral to-sea-mint text-white shadow-soft-coral/30'
                        : 'bg-gradient-to-r from-sea-mint to-soft-coral text-deep-indigo shadow-soft-coral/30'
                    ]"
                    aria-label="Play/Pause"
                  >
                    <span v-if="!isAudioPlaying" class="text-base sm:text-lg">▶</span>
                    <span v-else class="text-base sm:text-lg">⏸</span>
                  </button>
                  <div class="flex-1 space-y-0.5 sm:space-y-1 min-w-0">
                    <p class="text-xs sm:text-sm font-semibold text-soft-ice truncate">Lo-fi Radio</p>
                    <p class="text-[0.625rem] sm:text-xs text-text-secondary">Streaming</p>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-[0.625rem] sm:text-xs text-text-secondary w-12 sm:w-16 flex-shrink-0">Głośność</span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    :value="audioVolume"
                    @input="(e) => setAudioVolume((e.target as HTMLInputElement).valueAsNumber)"
                    class="flex-1 accent-sea-mint"
                  />
                  <span class="text-[0.625rem] sm:text-xs text-text-secondary w-8 text-right flex-shrink-0">{{ Math.round(audioVolume) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <AIChatPanel
      v-if="!loading && !error"
      :show="timerStore.showAIChat"
      :topic-name="topicName"
      :session-id="timerStore.session?.id"
      @close="timerStore.toggleAIChat()"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useTimerStore } from '../../stores/timer';
import { useProjectsStore } from '../../stores/projects';
import AIChatPanel from '../../components/chat/AIChatPanel.vue';
import api from '../../services/api';
import { processApiError } from '../../utils/errors';

const route = useRoute();
const router = useRouter();
const timerStore = useTimerStore();
const projectsStore = useProjectsStore();
const topicName = ref('Ładowanie...');
const topicId = ref<string>('');
const loading = ref(true);
const error = ref<string | null>(null);
const audioPlayer = ref<HTMLAudioElement | null>(null);
const isAudioPlaying = ref(false);
const audioVolume = ref(50);
const focusTips = [
  {
    title: '3 głębokie oddechy',
    body: 'Skoncentruj się na oddechu, aby ustabilizować uwagę i zmniejszyć niepokój przed trudnym pytaniem.',
  },
  {
    title: 'Sformułuj pytanie',
    body: 'Określ, co dokładnie przeszkadza w zrozumieniu tematu. Jedno jasne pytanie przyspieszy odpowiedź od AI i wróci Cię do przepływu.',
  },
  {
    title: 'Mikro-cel',
    body: 'Wybierz malutkie zadanie na najbliższe 5 minut. Małe zwycięstwo przywraca motywację.',
  },
];

const focusTip = computed(() => {
  if (timerStore.isLastMinute) return focusTips[1];
  if (timerStore.isRunning) return focusTips[0];
  return focusTips[2];
});

const progressRingStyle = computed(() => {
  const progress = Math.min(Math.max(timerStore.progress, 0), 100);
  const color = timerStore.isLastMinute ? '#FF8866' : '#66CCB6';
  return {
    background: `conic-gradient(${color} ${progress}%, rgba(255,255,255,0.08) ${progress}%)`,
  };
});

let audioStateCheckInterval: ReturnType<typeof setInterval> | null = null;

watch(
  () => audioPlayer.value,
  (player) => {
    if (player) {
      const checkState = () => {
        if (player) {
          const wasPlaying = isAudioPlaying.value;
          const isNowPlaying = !player.paused && !player.ended;
          if (wasPlaying !== isNowPlaying) {
            isAudioPlaying.value = isNowPlaying;
          }
        }
      };
      
      audioStateCheckInterval = setInterval(checkState, 100);
      checkState();
    } else {
      if (audioStateCheckInterval) {
        clearInterval(audioStateCheckInterval);
        audioStateCheckInterval = null;
      }
    }
  },
  { immediate: true }
);

onUnmounted(() => {
  if (audioStateCheckInterval) {
    clearInterval(audioStateCheckInterval);
  }
});

onMounted(async () => {
  topicId.value = route.params.sessionId as string;
  await projectsStore.fetchProjects();
  
  try {
    const { data } = await api.get(`/topics/${topicId.value}`);
    topicName.value = data.name;
    loading.value = false;
  } catch (e: any) {
    error.value = processApiError('timer/topic', e, 'Nie udało się załadować tematu.');
    loading.value = false;
  }

  if (audioPlayer.value) {
    audioPlayer.value.volume = audioVolume.value / 100;
    
    const updatePlayingState = () => {
      nextTick(() => {
        if (audioPlayer.value) {
          isAudioPlaying.value = !audioPlayer.value.paused;
        }
      });
    };
    
    audioPlayer.value.addEventListener('play', updatePlayingState);
    audioPlayer.value.addEventListener('pause', updatePlayingState);
    audioPlayer.value.addEventListener('playing', updatePlayingState);
    audioPlayer.value.addEventListener('ended', updatePlayingState);
    audioPlayer.value.addEventListener('loadstart', updatePlayingState);
    audioPlayer.value.addEventListener('canplay', updatePlayingState);
    
    nextTick(() => {
      updatePlayingState();
    });
  }
});

onUnmounted(() => {
  if (audioStateCheckInterval) {
    clearInterval(audioStateCheckInterval);
    audioStateCheckInterval = null;
  }
  if (timerStore.isRunning) {
    timerStore.pause();
  }
  if (audioPlayer.value) {
    audioPlayer.value.pause();
  }
});

const handleStart = async () => {
  try {
    await timerStore.startSession(topicId.value);
  } catch (e: unknown) {
    error.value = processApiError('timer/start', e, 'Nie udało się uruchomić sesji.');
  }
};

const handleStop = async () => {
  if (confirm('Zakończyć sesję?')) {
    try {
      await timerStore.completeSession();
      router.push('/dashboard');
    } catch (e: unknown) {
      error.value = processApiError('timer/complete', e, 'Nie udało się zakończyć sesji.');
    }
  }
};

const toggleAudio = async () => {
  if (!audioPlayer.value) return;
  
  if (audioPlayer.value.paused) {
    try {
      await audioPlayer.value.play();
      isAudioPlaying.value = true;
    } catch (e) {
      console.warn('Nie udało się odtworzyć audio:', e);
    }
  } else {
    audioPlayer.value.pause();
    isAudioPlaying.value = false;
  }
};

const setAudioVolume = (volume: number) => {
  audioVolume.value = volume;
  if (audioPlayer.value) {
    audioPlayer.value.volume = volume / 100;
  }
};
</script>
