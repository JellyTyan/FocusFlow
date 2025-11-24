import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api';
import { processApiError } from '../utils/errors';

export interface Subject {
  id: string;
  name: string;
  created_at: string;
}

export const useSubjectsStore = defineStore('subjects', () => {
  const subjects = ref<Subject[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchSubjects() {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await api.get('/subjects');
      subjects.value = data;
    } catch (e: unknown) {
      error.value = processApiError('subjects/fetch', e, 'Nie udało się załadować przedmiotów.');
    } finally {
      loading.value = false;
    }
  }

  async function createSubject(name: string) {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await api.post('/subjects', { name });
      subjects.value.push(data);
      return data;
    } catch (e: unknown) {
      error.value = processApiError('subjects/create', e, 'Nie udało się utworzyć przedmiotu.');
      throw e;
    } finally {
      loading.value = false;
    }
  }

  return {
    subjects,
    loading,
    error,
    fetchSubjects,
    createSubject,
  };
});

