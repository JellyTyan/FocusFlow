import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { AxiosError } from 'axios';
import { authService } from '../services/auth.service';
import type { RegisterData } from '../services/auth.service';
import { processApiError } from '../utils/errors';

function isAxiosError(error: unknown): error is AxiosError {
  return typeof error === 'object' && error !== null && 'response' in error;
}

export interface User {
  id: string;
  email: string;
  name: string;
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const isAuthenticated = ref(false);
  const loading = ref(false);
  const profileUpdating = ref(false);
  const error = ref<string | null>(null);

  async function login(credentials: { email: string; password: string }) {
    loading.value = true;
    error.value = null;
    try {
      const userData = await authService.login(credentials);
      user.value = userData;
      isAuthenticated.value = true;
    } catch (e: unknown) {
      error.value = processApiError('auth/login', e, 'Nie udało się zalogować. Sprawdź email i hasło.');
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function register(data: RegisterData) {
    loading.value = true;
    error.value = null;
    try {
      const userData = await authService.register(data);
      user.value = userData;
      isAuthenticated.value = true;
      await login({ email: data.email, password: data.password });
    } catch (e: unknown) {
      error.value = processApiError('auth/register', e, 'Nie udało się zakończyć rejestracji.');
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchCurrentUser() {
    const token = authService.getToken();
    if (!token) {
      loading.value = false;
      return;
    }

    loading.value = true;
    try {
      const userData = await authService.getCurrentUser();
      user.value = userData;
      isAuthenticated.value = true;
    } catch (e: unknown) {
      if (isAxiosError(e) && e.response?.status === 401) {
        user.value = null;
        isAuthenticated.value = false;
        authService.logout();
      } else {
        processApiError('auth/fetchCurrentUser', e, 'Nie udało się zaktualizować danych użytkownika.');
      }
    } finally {
      loading.value = false;
    }
  }

  async function updateProfile(payload: { name: string }) {
    profileUpdating.value = true;
    error.value = null;
    try {
      const updatedUser = await authService.updateProfile(payload);
      user.value = updatedUser;
      return updatedUser;
    } catch (e: unknown) {
      error.value = processApiError('auth/updateProfile', e, 'Nie udało się zapisać profilu.');
      throw e;
    } finally {
      profileUpdating.value = false;
    }
  }

  function logout() {
    authService.logout();
    user.value = null;
    isAuthenticated.value = false;
  }

  return {
    user,
    isAuthenticated,
    loading,
    error,
    profileUpdating,
    login,
    register,
    fetchCurrentUser,
    updateProfile,
    logout,
  };
});
