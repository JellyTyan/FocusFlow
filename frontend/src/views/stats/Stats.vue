<template>
  <div class="min-h-screen text-text-primary">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-5 lg:py-6">
      <div class="grid lg:grid-cols-[minmax(200px,260px)_1fr] gap-4 sm:gap-5 lg:gap-6">
        <Sidebar />
        <div class="min-w-0" v-lazy-show>
          <Topbar />

          <div
            class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-6 sm:mb-7 lg:mb-8"
            v-lazy-show
          >
            <div class="min-w-0">
              <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">Study pulse</p>
              <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold">Statystyki</h1>
            </div>
            <button
              @click="loadStats"
              class="px-4 sm:px-5 lg:px-6 py-2 sm:py-2.5 lg:py-3 rounded-lg sm:rounded-xl border border-white/10 text-xs sm:text-sm font-semibold hover:border-white/30 transition-all whitespace-nowrap flex-shrink-0"
            >
              Odśwież dane
            </button>
          </div>

          <div v-if="loading" class="glass-card text-center py-12 text-sea-mint text-xl">
            Ładowanie...
          </div>
          
          <div v-else-if="error" class="glass-card text-center py-12 text-soft-coral text-xl">
            {{ error }}
          </div>
          
          <div v-else class="space-y-4 sm:space-y-5 lg:space-y-6">
        <!-- Overview Stats -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-5 xl:gap-6">
          <BentoCard class="space-y-1">
            <p class="text-text-secondary text-sm">Wszystkich sesji</p>
            <div class="text-3xl font-bold text-soft-ice">{{ overview.total_sessions }}</div>
            <p class="text-xs text-text-secondary">+{{ overview.completed_sessions }} ukończono</p>
          </BentoCard>
          
          <BentoCard class="space-y-3">
            <p class="text-text-secondary text-sm">Czas fokusu</p>
            <div class="text-3xl font-bold text-soft-ice">{{ formatTime(overview.total_study_time) }}</div>
            <div class="w-full bg-soft-ice/10 rounded-full h-2">
              <div
                class="h-2 rounded-full bg-gradient-to-r from-sea-mint to-soft-coral"
                :style="{ width: `${Math.min((overview.total_study_time / 3600) * 5, 100)}%` }"
              ></div>
            </div>
            <p class="text-xs text-text-secondary">Cel: 5 h/dzień</p>
          </BentoCard>
          
          <BentoCard class="space-y-1">
            <p class="text-text-secondary text-sm">Tematów przestudiowanych</p>
            <div class="text-3xl font-bold text-soft-ice">{{ completedTopics }}</div>
            <p class="text-xs text-text-secondary">z {{ totalTopics }} tematów ({{ topicsCompletionRate }}%)</p>
          </BentoCard>
          
          <BentoCard class="space-y-2">
            <p class="text-text-secondary text-sm">Egzaminy</p>
            <div class="flex items-baseline gap-2">
              <div class="text-3xl font-bold text-soft-ice">{{ activeExams.length }}</div>
              <span class="text-text-secondary text-sm">aktywnych</span>
            </div>
            <p class="text-xs text-text-secondary">{{ completedExams.length }} ukończono</p>
          </BentoCard>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6">
          <!-- Active Exams -->
          <BentoCard class="lg:col-span-2">
            <div class="flex items-center justify-between gap-2 sm:gap-3 mb-3 sm:mb-4">
              <h2 class="text-xl sm:text-2xl font-bold">Aktywne egzaminy</h2>
              <span class="text-text-secondary text-xs sm:text-sm flex-shrink-0">{{ activeExams.length }} egzamin(ów)</span>
            </div>
            <div v-if="activeExams.length === 0" class="text-text-secondary text-center py-10">
              Wszystkie egzaminy ukończone 🎉
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="exam in activeExams"
                :key="exam.id"
                class="p-4 bg-deep-indigo/30 rounded-2xl space-y-3"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm text-text-secondary">{{ exam.subject }}</p>
                    <p class="text-lg font-semibold">{{ exam.name }}</p>
                  </div>
                  <button
                    class="text-soft-ice text-sm hover:text-sea-mint transition-colors"
                    @click="$router.push(`/projects/${exam.id}`)"
                  >
                    Otwórz →
                  </button>
                </div>
                <div class="flex items-center justify-between text-xs text-text-secondary">
                  <span>Postęp</span>
                  <span>{{ Math.round(exam.progress * 100) }}%</span>
                </div>
                <div class="w-full bg-soft-ice/5 rounded-full h-2 overflow-hidden">
                  <div
                    class="h-full bg-gradient-to-r from-sea-mint to-soft-coral transition-all"
                    :style="{ width: `${exam.progress * 100}%` }"
                  ></div>
                </div>
                <div class="flex items-center justify-between text-xs text-text-secondary">
                  <span>Tematów: {{ exam.topics.length }}</span>
                  <span>Deadline: {{ formatDate(exam.deadline) }}</span>
                </div>
              </div>
            </div>
          </BentoCard>

          <!-- Focus Insights -->
          <BentoCard class="space-y-6">
            <h2 class="text-2xl font-bold">Analityka fokusu</h2>
            <div class="space-y-4">
              <div>
                <div class="flex items-center justify-between text-sm text-text-secondary">
                  <span>Współczynnik ukończenia</span>
                  <span>{{ sessionCompletionRate }}%</span>
                </div>
                <div class="w-full bg-soft-ice/5 rounded-full h-2 overflow-hidden">
                  <div
                    class="h-full bg-sea-mint transition-all"
                    :style="{ width: `${sessionCompletionRate}%` }"
                  ></div>
                </div>
              </div>
              <div>
                <p class="text-text-secondary text-sm mb-1">Średnia sesja</p>
                <p class="text-xl font-semibold text-soft-ice">{{ averageSessionLength }}</p>
              </div>
              <div>
                <p class="text-text-secondary text-sm mb-1">Seria fokusu</p>
                <p class="text-xl font-semibold text-soft-ice">{{ focusStreak }} dni</p>
                <p class="text-xs text-text-secondary">pod rząd wykonywano sesje</p>
              </div>
            </div>
          </BentoCard>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Completed Exams -->
          <BentoCard>
            <h2 class="text-2xl font-bold mb-6">Ukończone egzaminy</h2>
            <div v-if="completedExams.length === 0" class="text-text-secondary text-center py-8">
              Nie ma jeszcze ukończonych egzaminów
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="project in completedExams"
                :key="project.id"
                class="p-4 bg-deep-indigo/30 rounded-xl space-y-2"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm text-text-secondary">{{ project.subject }}</p>
                    <p class="font-semibold">{{ project.name }}</p>
                  </div>
                  <span class="text-sea-mint text-sm">✓ ukończono</span>
                </div>
                <div class="flex items-center gap-4 text-xs text-text-secondary">
                  <span>Tematów: {{ project.topics.length }}</span>
                  <span>Deadline: {{ formatDate(project.deadline) }}</span>
                </div>
              </div>
            </div>
          </BentoCard>

          <!-- Stuck Topics -->
          <BentoCard>
            <h2 class="text-2xl font-bold mb-6">Tematy, w których najczęściej utykałeś</h2>
            <div v-if="stuckTopics.topics.length === 0" class="text-text-secondary text-center py-8">
              Nie ma jeszcze danych
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="topic in stuckTopics.topics"
                :key="topic.topic_id"
                class="p-4 bg-deep-indigo/30 rounded-xl space-y-2"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <p class="font-semibold">{{ topic.topic_name }}</p>
                    <p class="text-sm text-text-secondary">{{ topic.project_name }}</p>
                  </div>
                  <span class="text-soft-coral text-sm">{{ topic.stuck_count }}×</span>
                </div>
                <div class="text-xs text-text-secondary flex items-center gap-2">
                  <span>Pewność:</span>
                  <span>{{ '⭐'.repeat(topic.confidence_level) }}</span>
                </div>
              </div>
            </div>
          </BentoCard>
        </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useProjectsStore } from '../../stores/projects';
import Topbar from '../../components/layout/Topbar.vue';
import Sidebar from '../../components/layout/Sidebar.vue';
import BentoCard from '../../components/common/BentoCard.vue';
import api from '../../services/api';
import { processApiError } from '../../utils/errors';

const projectsStore = useProjectsStore();

const overview = ref({
  total_sessions: 0,
  completed_sessions: 0,
  total_study_time: 0,
  total_projects: 0,
  total_topics: 0,
});

const stuckTopics = ref({
  topics: [] as Array<{
    topic_id: string;
    topic_name: string;
    project_name: string;
    stuck_count: number;
    confidence_level: number;
  }>,
});

const loading = ref(true);
const error = ref<string | null>(null);

onMounted(async () => {
  await loadStats();
  await projectsStore.fetchProjects();
});

async function loadStats() {
  loading.value = true;
  error.value = null;
  try {
    const [overviewRes, stuckRes] = await Promise.all([
      api.get('/stats/overview'),
      api.get('/stats/stuck-topics'),
    ]);
    overview.value = overviewRes.data;
    stuckTopics.value = stuckRes.data;
  } catch (e: unknown) {
    error.value = processApiError('stats/load', e, 'Nie udało się załadować statystyk.');
  } finally {
    loading.value = false;
  }
}

function formatTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (hours > 0) {
    return `${hours}h ${minutes}min`;
  }
  return `${minutes}min`;
}

const activeExams = computed(() => {
  if (!Array.isArray(projectsStore.projects)) return [];
  return projectsStore.projects.filter(project => !project.completed);
});

const completedExams = computed(() => {
  if (!Array.isArray(projectsStore.projects)) return [];
  return projectsStore.projects.filter(project => project.completed);
});

const totalTopics = computed(() => {
  if (!Array.isArray(projectsStore.projects)) return 0;
  return projectsStore.projects.reduce((sum, project) => sum + project.topics.length, 0);
});

const completedTopics = computed(() => {
  if (!Array.isArray(projectsStore.projects)) return 0;
  return projectsStore.projects.reduce(
    (sum, project) => sum + project.topics.filter(topic => topic.completed).length,
    0
  );
});

const topicsCompletionRate = computed(() => {
  if (!totalTopics.value) return 0;
  return Math.round((completedTopics.value / totalTopics.value) * 100);
});

const sessionCompletionRate = computed(() => {
  if (!overview.value.total_sessions) return 0;
  return Math.round(
    (overview.value.completed_sessions / overview.value.total_sessions) * 100
  );
});

const averageSessionLength = computed(() => {
  if (!overview.value.completed_sessions) return '—';
  const avgSeconds = Math.round(
    overview.value.total_study_time / overview.value.completed_sessions
  );
  return formatTime(avgSeconds);
});

const focusStreak = computed(() => {
  // Placeholder: streak equals min completed sessions and 7
  return Math.min(overview.value.completed_sessions, 7);
});

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('pl-PL', {
    day: 'numeric',
    month: 'short',
  });
}
</script>
