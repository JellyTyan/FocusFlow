import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';
import { computePriority } from '../utils/priority';
import { processApiError } from '../utils/errors';

export interface Topic {
  id: string;
  project_id: string;
  name: string;
  confidence_level: number;
  priority_score: number;
  stuck_count: number;
  created_at: string;
  completed: boolean;
}

export interface Project {
  id: string;
  name: string;
  subject: string;
  deadline: string;
  created_at: string;
  topics: Topic[];
  progress: number;
  completed: boolean;
}

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref<Project[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  function isExpired(deadline: string): boolean {
    const deadlineDate = new Date(deadline);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    deadlineDate.setHours(0, 0, 0, 0);
    return deadlineDate < today;
  }

  const topPriorityTopic = computed(() => {
    if (!Array.isArray(projects.value)) {
      return undefined;
    }
    
    const allTopics: (Topic & { projectName: string; projectSubject: string; projectDeadline: string })[] = [];
    
    projects.value
      .filter(project => !project.completed && !isExpired(project.deadline))
      .forEach(project => {
        if (Array.isArray(project.topics)) {
          project.topics
            .filter(topic => !topic.completed)
            .forEach(topic => {
              const priority = computePriority(project.deadline, topic.confidence_level);
              allTopics.push({
                ...topic,
                priority_score: priority,
                projectName: project.name,
                projectSubject: project.subject,
                projectDeadline: project.deadline,
              });
            });
        }
      });

    return allTopics.sort((a, b) => b.priority_score - a.priority_score)[0];
  });

  async function fetchProjects() {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await api.get('/projects');
      projects.value = Array.isArray(data) ? data : [];
    } catch (e: unknown) {
      error.value = processApiError('projects/fetch', e, 'Nie udało się załadować egzaminów.');
      projects.value = [];
    } finally {
      loading.value = false;
    }
  }

  async function createProject(projectData: { name: string; subject: string; deadline: string; topics: string[] }) {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await api.post('/projects', projectData);
      if (!Array.isArray(projects.value)) {
        projects.value = [];
      }
      projects.value.push(data);
      return data;
    } catch (e: unknown) {
      error.value = processApiError('projects/create', e, 'Nie udało się utworzyć egzaminu.');
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function deleteProject(projectId: string) {
    try {
      await api.delete(`/projects/${projectId}`);
      if (Array.isArray(projects.value)) {
        projects.value = projects.value.filter(p => p.id !== projectId);
      } else {
        projects.value = [];
      }
    } catch (e: unknown) {
      error.value = processApiError('projects/delete', e, 'Nie udało się usunąć egzaminu.');
      throw e;
    }
  }

  async function updateTopicConfidence(topicId: string, confidence: number) {
    try {
      await api.put(`/topics/${topicId}`, { confidence_level: confidence });
      await fetchProjects();
    } catch (e: unknown) {
      error.value = processApiError('topics/updateConfidence', e, 'Nie udało się zaktualizować pewności co do tematu.');
      throw e;
    }
  }

  return {
    projects,
    loading,
    error,
    topPriorityTopic,
    isExpired,
    fetchProjects,
    createProject,
    deleteProject,
    updateTopicConfidence,
  };
});
