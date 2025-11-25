<template>
  <div class="min-h-screen text-text-primary">
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-5 lg:py-6">
      <div class="grid lg:grid-cols-[minmax(200px,260px)_1fr] gap-4 sm:gap-5 lg:gap-6">
        <Sidebar />
        <div class="min-w-0">
          <Topbar />

          <div v-if="loading" class="glass-card text-center py-12 text-sea-mint text-xl">
            Ładowanie egzaminu...
          </div>

          <div v-else-if="error" class="glass-card text-center py-12 space-y-4">
            <div class="text-soft-coral text-xl">{{ error }}</div>
            <button
              @click="$router.push('/dashboard')"
              class="px-6 py-3 rounded-xl bg-soft-coral/20 text-soft-coral font-semibold hover:bg-soft-coral/30 transition-colors"
            >
              Wróć do tablicy
            </button>
          </div>

          <div v-else-if="project" class="space-y-6">
            <button
              @click="$router.push('/dashboard')"
              class="text-text-secondary hover:text-white transition-colors flex items-center gap-2 text-sm"
            >
              ← Wróć do egzaminów
            </button>

            <div 
              class="glass-card p-4 sm:p-5 lg:p-6 rounded-2xl sm:rounded-3xl border border-white/10 flex flex-col gap-4 sm:gap-5 lg:gap-6 lg:flex-row lg:items-center lg:justify-between"
              :class="projectsStore.isExpired(project.deadline) ? 'opacity-50 grayscale' : ''"
            >
              <div class="space-y-1.5 sm:space-y-2 min-w-0">
                <div class="flex items-center gap-2">
                  <p class="text-[0.625rem] sm:text-xs uppercase tracking-[0.4em] text-text-secondary">Exam focus</p>
                  <span v-if="projectsStore.isExpired(project.deadline)" class="text-xs px-2 py-1 bg-text-secondary/20 text-text-secondary rounded-lg">
                    Zakończony
                  </span>
                </div>
                <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold truncate">{{ project.name }}</h1>
                <p class="text-text-secondary text-base sm:text-lg truncate">{{ project.subject }}</p>
                <div class="text-xs sm:text-sm text-text-secondary">
                  Deadline: {{ formatDate(project.deadline) }}
                  <span v-if="projectsStore.isExpired(project.deadline)" class="text-soft-coral ml-2">(Przeterminowany)</span>
                </div>
              </div>
              <div class="flex gap-2 sm:gap-3 flex-wrap flex-shrink-0">
                <button
                  @click="showEditModal = true"
                  class="px-5 py-3 rounded-2xl border border-white/15 text-sm font-semibold hover:border-white/40 transition-colors"
                >
                  ✏️ Edytuj
                </button>
                <button
                  @click="handleCompleteProject"
                  :class="[
                    'px-5 py-3 rounded-2xl text-sm font-semibold transition-transform hover:scale-105',
                    project.completed
                      ? 'bg-soft-ice/10 text-text-secondary'
                      : 'bg-gradient-to-r from-sea-mint to-soft-coral text-deep-indigo'
                  ]"
                >
                  {{ project.completed ? '✓ Zakończony' : 'Zakończ egzamin' }}
                </button>
              </div>
            </div>

            <div class="grid gap-4 sm:gap-5 lg:gap-6 lg:grid-cols-[1.4fr_0.6fr]">
              <BentoCard class="space-y-3 sm:space-y-4">
                <div class="flex items-center justify-between gap-2 sm:gap-3">
                  <div class="min-w-0">
                    <p class="text-text-secondary text-xs sm:text-sm">Postęp</p>
                    <p class="text-2xl sm:text-3xl font-bold text-soft-ice">{{ Math.round(project.progress * 100) }}%</p>
                  </div>
                  <div class="text-right text-xs sm:text-sm text-text-secondary flex-shrink-0">
                    <p>Tematów ukończonych</p>
                    <p class="text-base sm:text-lg font-semibold text-soft-ice">{{ completedTopicsCount }} / {{ project.topics.length }}</p>
                  </div>
                </div>
                <div class="w-full bg-soft-ice/10 rounded-full h-2 sm:h-3 overflow-hidden">
                  <div
                    class="h-full bg-gradient-to-r from-sea-mint to-soft-coral transition-all"
                    :style="{ width: `${project.progress * 100}%` }"
                  ></div>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 text-xs sm:text-sm text-text-secondary">
                  <div class="p-3 rounded-2xl bg-white/5 border border-white/5">
                    <p>Pewność (śr.)</p>
                    <p class="text-xl font-semibold text-soft-ice">
                      {{ (project.topics.reduce((sum, t) => sum + t.confidence_level, 0) / (project.topics.length || 1)).toFixed(1) }} ⭐
                    </p>
                  </div>
                  <div class="p-3 rounded-2xl bg-white/5 border border-white/5">
                    <p>Utknięć</p>
                    <p class="text-xl font-semibold text-soft-ice">
                      {{ project.topics.reduce((sum, t) => sum + t.stuck_count, 0) }}×
                    </p>
                  </div>
                  <div class="p-3 rounded-2xl bg-white/5 border border-white/5">
                    <p>Tematów bez sesji</p>
                    <p class="text-xl font-semibold text-soft-ice">
                      {{ project.topics.filter(t => !t.completed && t.stuck_count === 0).length }}
                    </p>
                  </div>
                </div>
              </BentoCard>

              <BentoCard class="space-y-4">
                <p class="text-text-secondary text-sm">Egzamin</p>
                <div class="space-y-3 text-sm text-text-secondary">
                  <div class="flex items-center justify-between">
                    <span>Status</span>
                    <span class="text-soft-ice">{{ project.completed ? 'Zakończony' : 'W trakcie' }}</span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span>Temat priorytetowy</span>
                    <span class="text-soft-ice">
                      {{ project.topics.find(t => !t.completed)?.name || '—' }}
                    </span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span>Tematów łącznie</span>
                    <span class="text-soft-ice">{{ project.topics.length }}</span>
                  </div>
                </div>
              </BentoCard>
            </div>

            <div class="flex items-center justify-between flex-wrap gap-4">
              <div>
                <p class="text-xs uppercase tracking-[0.4em] text-text-secondary">Study sprint</p>
                <h2 class="text-3xl font-bold">Tematy</h2>
              </div>
              <button
                @click="showAddTopicModal = true"
                class="px-5 py-3 rounded-2xl border border-white/15 text-sm font-semibold hover:border-white/40 transition-colors"
              >
                + Dodaj temat
              </button>
            </div>

            <div v-if="project.topics.length === 0" class="glass-card rounded-3xl p-10 text-center space-y-4">
              <p class="text-text-secondary">Nie ma jeszcze tematów — zacznij od najbardziej niepokojącego 🤍</p>
              <div class="flex justify-center gap-4 flex-wrap">
                <button
                  @click="showAddTopicModal = true"
                  class="px-6 py-3 bg-sea-mint text-deep-indigo rounded-2xl font-semibold hover:scale-105 transition-transform"
                >
                  Dodaj pierwszy temat
                </button>
                <button
                  v-if="!project.completed"
                  @click="handleCompleteProject"
                  class="px-6 py-3 bg-soft-coral text-white rounded-2xl font-semibold hover:scale-105 transition-transform"
                >
                  Zakończ egzamin
                </button>
              </div>
            </div>

            <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <BentoCard
                v-for="topic in project.topics"
                :key="topic.id"
                :class="[topic.completed ? 'opacity-60' : '', 'transition-all']"
                hoverable
              >
                <div class="flex items-start justify-between gap-4">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <h3 class="text-xl font-bold">{{ topic.name }}</h3>
                      <span v-if="topic.completed" class="text-sea-mint text-sm">✓</span>
                    </div>
                    <ConfidenceStars
                      :model-value="topic.confidence_level"
                      :readonly="true"
                      class="mb-3"
                    />
                    <div class="text-sm text-text-secondary mb-2">
                      Priorytet: {{ topic.priority_score.toFixed(2) }}
                    </div>
                    <div class="text-sm text-text-secondary">
                      Utknięć: {{ topic.stuck_count }}
                    </div>
                  </div>
                  <div class="flex flex-col gap-2">
                    <button
                      @click="startSession(topic.id)"
                      :disabled="topic.completed"
                      class="px-4 py-2 bg-sea-mint text-deep-indigo rounded-xl font-semibold hover:scale-105 transition-transform disabled:opacity-50"
                    >
                      ▶ Fokus
                    </button>
                    <button
                      @click="editTopic(topic)"
                      class="px-4 py-2 bg-soft-ice/10 rounded-xl font-semibold hover:scale-105 transition-transform"
                    >
                      ✏️
                    </button>
                    <button
                      @click="handleCompleteTopic(topic.id, !topic.completed)"
                      :class="[
                        'px-4 py-2 rounded-xl font-semibold transition-transform hover:scale-105',
                        topic.completed
                          ? 'bg-soft-ice/10 text-text-secondary'
                          : 'bg-soft-coral/20 text-soft-coral'
                      ]"
                    >
                      {{ topic.completed ? 'Anuluj' : '✓ Gotowe' }}
                    </button>
                  </div>
                </div>
              </BentoCard>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Project Modal -->
    <Transition name="modal">
      <div
        v-if="showEditModal && project"
        class="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center p-4 sm:p-8 z-50"
        @click.self="showEditModal = false"
      >
        <div class="glass-card p-6 sm:p-8 w-full max-w-3xl animate-scale-in">
        <div class="flex flex-col gap-2 mb-6">
          <p class="text-xs uppercase tracking-[0.4em] text-text-secondary">Edycja</p>
          <div class="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-3">
            <h3 class="text-3xl font-bold">Zaktualizuj parametry egzaminu</h3>
            <span class="text-sm text-text-secondary">Wpływ: deadline'y, kolor karty, priorytety</span>
          </div>
        </div>
        <form @submit.prevent="handleUpdateProject" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label class="block space-y-2 text-sm">
              <span class="text-text-secondary">Nazwa</span>
              <input
                v-model="editForm.name"
                required
                class="w-full px-4 py-3 bg-deep-indigo/50 rounded-2xl border border-white/10 focus:border-sea-mint outline-none"
              />
            </label>
            <label class="block space-y-2 text-sm">
              <span class="text-text-secondary">Deadline</span>
              <input
                v-model="editForm.deadline"
                type="date"
                required
                class="w-full px-4 py-3 bg-deep-indigo/50 rounded-2xl border border-white/10 focus:border-sea-mint outline-none"
              />
            </label>
          </div>

          <label class="block space-y-2 text-sm">
            <span class="text-text-secondary">Przedmiot</span>
            <select
              v-model="editForm.subject"
              required
              class="w-full px-4 py-3 bg-deep-indigo/50 rounded-2xl border border-white/10 focus:border-sea-mint outline-none"
            >
              <option v-if="!editForm.subject" value="" disabled>Wybierz przedmiot</option>
              <option v-for="subjectName in subjectOptions" :key="subjectName" :value="subjectName">
                {{ subjectName }}
              </option>
              <option value="__NEW__">+ Dodaj nowy przedmiot</option>
            </select>
            <input
              v-if="editForm.subject === '__NEW__' || (editForm.subject && !subjectOptions.includes(editForm.subject))"
              v-model="editForm.newSubject"
              :placeholder="editForm.subject === '__NEW__' ? 'Wprowadź nową nazwę' : 'Lub wprowadź nowy przedmiot'"
              required
              class="w-full mt-2 px-4 py-3 bg-deep-indigo/50 rounded-2xl border border-white/10 focus:border-sea-mint outline-none"
            />
          </label>

          <div class="flex flex-col sm:flex-row gap-3">
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 btn-primary disabled:opacity-50 disabled:hover:scale-100"
            >
              {{ loading ? 'Zapisywanie...' : 'Zapisz' }}
            </button>
            <button
              type="button"
              @click="showEditModal = false"
              class="flex-1 px-6 py-3 rounded-2xl border border-white/15 font-semibold text-text-secondary hover:border-white/40 transition-colors"
            >
              Anuluj
            </button>
          </div>
        </form>
      </div>
    </div>
    </Transition>

    <!-- Add/Edit Topic Modal -->
    <Transition name="modal">
      <div
        v-if="showAddTopicModal || editingTopic"
        class="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center p-4 sm:p-8 z-50"
        @click.self="closeTopicModal"
      >
        <div class="glass-card p-6 sm:p-8 w-full max-w-2xl animate-scale-in">
        <div class="flex items-center justify-between mb-6">
          <div>
            <p class="text-xs uppercase tracking-[0.4em] text-text-secondary">Temat</p>
            <h3 class="text-2xl font-bold">{{ editingTopic ? 'Zaktualizuj fragment planu' : 'Dodaj nowy temat' }}</h3>
          </div>
          <span class="text-text-secondary text-sm">{{ project?.subject }}</span>
        </div>
        <form @submit.prevent="handleSaveTopic" class="space-y-5">
          <label class="block space-y-2 text-sm">
            <span class="text-text-secondary">Nazwa tematu</span>
            <input
              v-model="topicForm.name"
              required
              class="w-full px-4 py-3 bg-deep-indigo/50 rounded-2xl border border-white/10 focus:border-sea-mint outline-none"
              placeholder="Np., Fotosynteza"
            />
          </label>

          <div class="space-y-2 text-sm">
            <span class="text-text-secondary">Pewność</span>
            <div class="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-between">
              <ConfidenceStars
                :model-value="topicForm.confidence_level"
                @update="(val) => (topicForm.confidence_level = val)"
              />
              <span class="text-xs text-text-secondary">Oceń intuicyjnie — zawsze można zmienić</span>
            </div>
          </div>

          <div v-if="error" class="text-soft-coral text-sm bg-soft-coral/10 border border-soft-coral/30 rounded-2xl px-4 py-3">
            {{ error }}
          </div>

          <div class="flex flex-col sm:flex-row gap-3">
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 btn-primary disabled:opacity-50 disabled:hover:scale-100"
            >
              {{ loading ? 'Zapisywanie...' : editingTopic ? 'Zapisz' : 'Dodaj temat' }}
            </button>
            <button
              type="button"
              @click="closeTopicModal"
              class="flex-1 px-6 py-3 rounded-2xl border border-white/15 font-semibold text-text-secondary hover:border-white/40 transition-colors"
            >
              Anuluj
            </button>
          </div>
        </form>
      </div>
    </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useProjectsStore } from '../../stores/projects';
import Topbar from '../../components/layout/Topbar.vue';
import Sidebar from '../../components/layout/Sidebar.vue';
import BentoCard from '../../components/common/BentoCard.vue';
import ConfidenceStars from '../../components/common/ConfidenceStars.vue';
import api from '../../services/api';
import type { Project, Topic } from '../../stores/projects';
import { getSubjectOptions } from '../../utils/subjects';
import { processApiError } from '../../utils/errors';

const route = useRoute();
const router = useRouter();
const projectsStore = useProjectsStore();

const project = ref<Project | null>(null);
const subjects = ref<Array<{ id: string; name: string }>>([]);
const loading = ref(true);
const error = ref<string | null>(null);
const showEditModal = ref(false);
const showAddTopicModal = ref(false);
const editingTopic = ref<Topic | null>(null);

const editForm = ref({
  name: '',
  subject: '',
  deadline: '',
  newSubject: '',
});

const topicForm = ref({
  name: '',
  confidence_level: 1,
});

const completedTopicsCount = computed(() => project.value?.topics.filter(t => t.completed).length || 0);
const subjectOptions = computed(() => getSubjectOptions(subjects.value));

onMounted(async () => {
  await projectsStore.fetchProjects();
  await loadProject();
  await loadSubjects();
});

async function loadProject() {
  loading.value = true;
  error.value = null;
  try {
    const { data } = await api.get(`/projects/${route.params.id}`);
    project.value = data;
    if (project.value) {
      editForm.value = {
        name: project.value.name,
        subject: project.value.subject,
        deadline: project.value.deadline?.split('T')[0] ?? '',
        newSubject: '',
      };
    }
  } catch (e: unknown) {
    error.value = processApiError('projects/load-single', e, 'Nie udało się załadować egzaminu.');
  } finally {
    loading.value = false;
  }
}

async function loadSubjects() {
  try {
    const { data } = await api.get('/subjects');
    subjects.value = data;
  } catch (e: unknown) {
    error.value = processApiError('subjects/load', e, 'Nie udało się załadować listy przedmiotów.');
  }
}

async function handleUpdateProject() {
  try {
    let subject = editForm.value.subject;

    if (editForm.value.subject === '__NEW__' || editForm.value.newSubject) {
      const subjectName = editForm.value.newSubject || editForm.value.subject;
      if (subjectName && !subjectOptions.value.includes(subjectName)) {
        const { data } = await api.post('/subjects', { name: subjectName });
        subject = data.name;
        await loadSubjects();
      } else {
        subject = subjectName;
      }
    }

    if (!subject) {
      error.value = 'Wybierz lub wprowadź przedmiot';
      return;
    }

    await api.put(`/projects/${route.params.id}`, {
      name: editForm.value.name,
      subject,
      deadline: editForm.value.deadline,
    });

    await loadProject();
    showEditModal.value = false;
  } catch (e: unknown) {
    error.value = processApiError('projects/update', e, 'Nie udało się zaktualizować egzaminu.');
  }
}

async function handleSaveTopic() {
  if (!topicForm.value.name.trim()) {
    error.value = 'Wprowadź nazwę tematu';
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    if (editingTopic.value) {
      await api.put(`/topics/${editingTopic.value.id}`, {
        name: topicForm.value.name,
        confidence_level: topicForm.value.confidence_level,
      });
    } else {
      await api.post(`/projects/${route.params.id}/topics`, {
        name: topicForm.value.name,
        confidence_level: topicForm.value.confidence_level,
      });
    }
    await loadProject();
    closeTopicModal();
  } catch (e: unknown) {
    error.value = processApiError('topics/save', e, 'Nie udało się zapisać tematu.');
  } finally {
    loading.value = false;
  }
}

async function handleCompleteTopic(topicId: string, completed: boolean) {
  try {
    await api.put(`/topics/${topicId}`, { completed });
    await loadProject();
  } catch (e: unknown) {
    error.value = processApiError('topics/complete', e, 'Nie udało się zaktualizować statusu tematu.');
  }
}

async function handleCompleteProject() {
  try {
    await api.put(`/projects/${route.params.id}`, {
      completed: !project.value?.completed,
    });
    await loadProject();
  } catch (e: unknown) {
    error.value = processApiError('projects/complete', e, 'Nie udało się zmienić statusu egzaminu.');
  }
}

function editTopic(topic: Topic) {
  editingTopic.value = topic;
  topicForm.value = {
    name: topic.name,
    confidence_level: topic.confidence_level,
  };
  showAddTopicModal.value = true;
}

function closeTopicModal() {
  showAddTopicModal.value = false;
  editingTopic.value = null;
  topicForm.value = { name: '', confidence_level: 1 };
}

function startSession(topicId: string) {
  router.push(`/timer/${topicId}`);
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('pl-PL', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}
</script>
