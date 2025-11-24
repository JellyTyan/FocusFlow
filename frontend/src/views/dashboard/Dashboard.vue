<template>
  <div class="min-h-screen text-text-primary">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-5 lg:py-6">
      <div class="grid lg:grid-cols-[minmax(200px,260px)_1fr] gap-4 sm:gap-5 lg:gap-6">
        <Sidebar />
        <div class="min-w-0">
          <Topbar />

          <div
            v-if="projectsStore.error"
            class="mb-4 sm:mb-5 lg:mb-6 px-3 sm:px-4 py-2 sm:py-3 rounded-xl sm:rounded-2xl border border-soft-coral/30 bg-soft-coral/10 text-soft-coral text-xs sm:text-sm"
          >
            {{ projectsStore.error }}
          </div>

          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4 mb-6 sm:mb-7 lg:mb-8" v-lazy-show>
            <h2 class="text-2xl sm:text-3xl lg:text-4xl font-bold">Moje egzaminy</h2>
            <button
              @click="showCreateModal = true"
              class="px-4 sm:px-5 lg:px-6 py-2 sm:py-2.5 lg:py-3 bg-sea-mint text-deep-indigo rounded-lg sm:rounded-xl font-semibold text-sm sm:text-base hover:scale-105 transition-transform whitespace-nowrap"
            >
              + Utwórz egzamin
            </button>
          </div>

          <!-- TERAZ Card -->
          <BentoCard v-if="projectsStore.topPriorityTopic" urgent class="mb-4 sm:mb-5 lg:mb-6">
            <div class="space-y-4 sm:space-y-5">
              <div class="flex items-center justify-between gap-3">
                <div class="flex items-center gap-2">
                  <span class="text-2xl sm:text-3xl">🔥</span>
                  <div>
                    <div class="text-soft-coral text-xs sm:text-sm font-bold uppercase tracking-wider">Zrób to TERAZ</div>
                    <div class="text-text-secondary text-[0.625rem] sm:text-xs">Najwyższy priorytet</div>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-xs sm:text-sm text-text-secondary">Priorytet</div>
                  <div class="text-lg sm:text-xl font-bold text-soft-coral">{{ projectsStore.topPriorityTopic.priority_score.toFixed(1) }}</div>
                </div>
              </div>
              
              <div class="space-y-2 sm:space-y-3">
                <div>
                  <h3 class="text-xl sm:text-2xl lg:text-3xl font-bold mb-1 sm:mb-2">{{ projectsStore.topPriorityTopic.name }}</h3>
                  <div class="flex flex-wrap items-center gap-2 sm:gap-3 text-xs sm:text-sm text-text-secondary">
                    <span class="font-semibold text-soft-ice">{{ projectsStore.topPriorityTopic.projectName }}</span>
                    <span>•</span>
                    <span>{{ projectsStore.topPriorityTopic.projectSubject }}</span>
                  </div>
                </div>
                
                <div class="flex flex-wrap items-center gap-3 sm:gap-4">
                  <div class="flex items-center gap-2">
                    <span class="text-xs sm:text-sm text-text-secondary">Pewność:</span>
                    <ConfidenceStars
                      :model-value="projectsStore.topPriorityTopic.confidence_level"
                      :readonly="true"
                    />
                  </div>
                  <div v-if="projectsStore.topPriorityTopic.projectDeadline" class="flex items-center gap-2">
                    <span class="text-xs sm:text-sm text-text-secondary">Deadline:</span>
                    <span class="text-xs sm:text-sm font-semibold text-soft-coral">{{ formatDeadline(projectsStore.topPriorityTopic.projectDeadline) }}</span>
                  </div>
                  <div v-if="projectsStore.topPriorityTopic.stuck_count > 0" class="flex items-center gap-2">
                    <span class="text-xs sm:text-sm text-text-secondary">Utknięć:</span>
                    <span class="text-xs sm:text-sm font-semibold text-soft-coral">{{ projectsStore.topPriorityTopic.stuck_count }}</span>
                  </div>
                </div>
              </div>
              
              <button
                @click="startSession(projectsStore.topPriorityTopic!.id)"
                class="w-full px-5 sm:px-6 lg:px-8 py-3 sm:py-3.5 lg:py-4 bg-gradient-to-r from-soft-coral to-sea-mint text-white rounded-lg sm:rounded-xl font-bold text-sm sm:text-base lg:text-lg hover:scale-105 transition-transform shadow-lg shadow-soft-coral/30"
              >
                ▶ Zacznij fokus teraz
              </button>
            </div>
          </BentoCard>

          <!-- Projects Grid -->
          <div v-if="projectsStore.loading" class="text-center py-12">
            <div class="text-sea-mint text-xl">Ładowanie projektów...</div>
          </div>

          <div v-else-if="!Array.isArray(projectsStore.projects) || projectsStore.projects.length === 0" class="text-center py-12">
            <p class="text-text-secondary text-lg mb-4">Nie masz jeszcze egzaminów</p>
            <button
              @click="showCreateModal = true"
              class="px-6 py-3 bg-sea-mint text-deep-indigo rounded-xl font-semibold hover:scale-105 transition-transform"
            >
              Utwórz pierwszy egzamin
            </button>
          </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6" v-lazy-show>
            <BentoCard
              v-for="project in (Array.isArray(projectsStore.projects) ? projectsStore.projects.filter(p => !p.completed) : [])"
              :key="project.id"
              hoverable
              @click="$router.push(`/projects/${project.id}`)"
              :class="project.completed ? 'opacity-60' : ''"
            >
              <h3 class="text-xl font-bold mb-2">{{ project.name }}</h3>
              <p class="text-text-secondary text-sm mb-4">{{ project.subject }}</p>
              <div class="text-sm text-text-secondary mb-2">
                Deadline: {{ formatDate(project.deadline) }}
              </div>
              <div class="text-sm text-text-secondary mb-4">
                Tematów: {{ project.topics.length }}
              </div>
              <div class="w-full bg-soft-ice/10 rounded-full h-2">
                <div
                  class="bg-sea-mint h-2 rounded-full transition-all"
                  :style="{ width: `${project.progress * 100}%` }"
                />
              </div>
            </BentoCard>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Project Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 lg:p-8 z-50 overflow-y-auto"
      @click.self="showCreateModal = false"
    >
      <div class="glass-card p-4 sm:p-6 lg:p-8 w-full max-w-3xl animate-scale-in my-auto">
        <div class="flex flex-col gap-2 mb-4 sm:mb-5 lg:mb-6">
          <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">Nowy egzamin</p>
          <div class="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-2 sm:gap-3">
            <h3 class="text-2xl sm:text-3xl font-bold">Złóż plan fokusowy</h3>
            <span class="text-xs sm:text-sm text-text-secondary">Scenariusz: przedmiot → deadline → tematy</span>
          </div>
        </div>

        <form @submit.prevent="handleCreateProject" class="space-y-4 sm:space-y-5 lg:space-y-6">
          <div
            v-if="projectsStore.error"
            class="px-3 sm:px-4 py-2 sm:py-3 rounded-xl sm:rounded-2xl border border-soft-coral/40 bg-soft-coral/10 text-soft-coral text-xs sm:text-sm"
          >
            {{ projectsStore.error }}
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <label class="block space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
              <span class="text-text-secondary">Nazwa egzaminu</span>
              <input
                v-model="newProject.name"
                required
                class="w-full px-3 sm:px-4 py-2.5 sm:py-3 text-sm sm:text-base bg-deep-indigo/50 rounded-xl sm:rounded-2xl border border-white/10 focus:border-sea-mint outline-none"
                placeholder="Na przykład, matura z biologii"
              />
            </label>

            <label class="block space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
              <span class="text-text-secondary">Deadline</span>
              <input
                v-model="newProject.deadline"
                type="date"
                required
                :min="today"
                class="w-full px-3 sm:px-4 py-2.5 sm:py-3 text-sm sm:text-base bg-deep-indigo/50 rounded-xl sm:rounded-2xl border border-white/10 focus:border-sea-mint outline-none"
              />
              <span v-if="deadlineError" class="text-[0.625rem] sm:text-xs text-soft-coral">
                Data musi być późniejsza niż dzisiejsza.
              </span>
            </label>
          </div>

          <label class="block space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
            <span class="text-text-secondary">Przedmiot</span>
            <select
              v-model="newProject.subject"
              required
              class="w-full px-3 sm:px-4 py-2.5 sm:py-3 text-sm sm:text-base bg-deep-indigo/50 rounded-xl sm:rounded-2xl border border-white/10 focus:border-sea-mint outline-none"
            >
              <option v-if="!newProject.subject" value="" disabled>Wybierz przedmiot</option>
              <option v-for="subjectName in subjectOptions" :key="subjectName" :value="subjectName">
                {{ subjectName }}
              </option>
              <option value="__NEW__">+ Dodaj nowy przedmiot</option>
            </select>
            <input
              v-if="newProject.subject === '__NEW__' || (newProject.subject && !subjectOptions.includes(newProject.subject))"
              v-model="newProject.newSubject"
              :placeholder="newProject.subject === '__NEW__' ? 'Wprowadź nową nazwę' : 'Lub wprowadź nowy przedmiot'"
              required
              class="w-full mt-2 px-3 sm:px-4 py-2.5 sm:py-3 text-sm sm:text-base bg-deep-indigo/50 rounded-xl sm:rounded-2xl border border-white/10 focus:border-sea-mint outline-none"
            />
          </label>

          <label class="block space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
            <span class="text-text-secondary">Tematy (jeden na linię)</span>
            <textarea
              v-model="newProject.topicsText"
              rows="5"
              placeholder="Fotosynteza&#10;Mitaza&#10;Mejoza"
              class="w-full px-3 sm:px-4 py-2.5 sm:py-3 text-sm sm:text-base bg-deep-indigo/50 rounded-xl sm:rounded-2xl border border-white/10 focus:border-sea-mint outline-none resize-y"
            />
            <span class="text-[0.625rem] sm:text-xs text-text-secondary">Rada: zacznij od najbardziej niepokojących tematów, aby przyspieszyć postęp</span>
          </label>

          <div class="flex flex-col sm:flex-row gap-3">
            <button
              type="submit"
              :disabled="projectsStore.loading"
              class="flex-1 btn-primary text-sm sm:text-base px-4 sm:px-6 py-2.5 sm:py-3 disabled:opacity-50 disabled:hover:scale-100"
            >
              {{ projectsStore.loading ? 'Tworzenie...' : 'Utwórz egzamin' }}
            </button>
            <button
              type="button"
              @click="showCreateModal = false"
              class="flex-1 px-4 sm:px-6 py-2.5 sm:py-3 rounded-xl sm:rounded-2xl border border-white/15 font-semibold text-xs sm:text-sm text-text-secondary hover:border-white/40 transition-colors"
            >
              Anuluj
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useProjectsStore } from '../../stores/projects';
import { useSubjectsStore } from '../../stores/subjects';
import Topbar from '../../components/layout/Topbar.vue';
import Sidebar from '../../components/layout/Sidebar.vue';
import BentoCard from '../../components/common/BentoCard.vue';
import ConfidenceStars from '../../components/common/ConfidenceStars.vue';
import { getSubjectOptions } from '../../utils/subjects';

const router = useRouter();
const projectsStore = useProjectsStore();
const subjectsStore = useSubjectsStore();
const showCreateModal = ref(false);
const newProject = ref({
  name: '',
  subject: '',
  deadline: '',
  topicsText: '',
  newSubject: '',
});
const today = new Date().toISOString().split('T')[0] ?? '';
const deadlineError = computed(() => {
  if (!newProject.value.deadline) return false;
  return newProject.value.deadline < today;
});

onMounted(async () => {
  await projectsStore.fetchProjects();
  await subjectsStore.fetchSubjects();
});

const subjectOptions = computed(() => {
  return getSubjectOptions(subjectsStore.subjects);
});

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('pl-PL', {
    day: 'numeric',
    month: 'long',
  });
};

const formatDeadline = (dateStr: string) => {
  const deadline = new Date(dateStr);
  const now = new Date();
  const diffTime = deadline.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays < 0) {
    return 'Przeterminowany';
  } else if (diffDays === 0) {
    return 'Dzisiaj';
  } else if (diffDays === 1) {
    return 'Jutro';
  } else if (diffDays <= 7) {
    return `Za ${diffDays} dni`;
  } else {
    return deadline.toLocaleDateString('pl-PL', {
      day: 'numeric',
      month: 'short',
    });
  }
};

const handleCreateProject = async () => {
  const topics = newProject.value.topicsText
    .split('\n')
    .map(t => t.trim())
    .filter(t => t.length > 0);

  if (deadlineError.value) {
    projectsStore.error = 'Wybierz datę późniejszą niż dzisiejsza.';
    return;
  }

  try {
    let subject = newProject.value.subject;

    if (newProject.value.subject === '__NEW__' || newProject.value.newSubject) {
      const subjectName = newProject.value.newSubject || newProject.value.subject;
      if (subjectName && !subjectOptions.value.includes(subjectName)) {
        const created = await subjectsStore.createSubject(subjectName);
        subject = created.name;
      } else {
        subject = subjectName;
      }
    }

    if (!subject) {
      return;
    }

    await projectsStore.createProject({
      name: newProject.value.name,
      subject: subject,
      deadline: newProject.value.deadline,
      topics,
    });
    showCreateModal.value = false;
    newProject.value = { name: '', subject: '', deadline: '', topicsText: '', newSubject: '' };
  } catch (e) {
  }
};

const startSession = async (topicId: string) => {
  await projectsStore.fetchProjects();
  router.push(`/timer/${topicId}`);
};

</script>
