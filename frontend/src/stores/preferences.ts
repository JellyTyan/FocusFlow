import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { logger } from '../services/logger';

export type FocusTheme = 'deep-space' | 'dawn' | 'minimal';
export type FocusSoundscape = 'lofi' | 'rain' | 'silence';
export type FocusLighting = 'glow' | 'aurora' | 'minimal';
export type MotivationMode = 'calm' | 'coach' | 'hype';
export type MotivationMantra = 'flow' | 'clarity' | 'legacy';

export interface PreferencesState {
  avatarEmoji: string;
  focusTheme: FocusTheme;
  focusSoundscape: FocusSoundscape;
  focusLighting: FocusLighting;
  ambienceLevel: number;
  motivationMode: MotivationMode;
  motivationMantra: MotivationMantra;
  motivationPulse: number;
  celebrationReminders: boolean;
  dailyFocusGoal: number; // hours per day
  notifications: boolean;
}

const STORAGE_KEY = 'focusflow-preferences';

const defaultPreferences: PreferencesState = {
  avatarEmoji: '🧠',
  focusTheme: 'deep-space',
  focusSoundscape: 'lofi',
  focusLighting: 'glow',
  ambienceLevel: 3,
  motivationMode: 'coach',
  motivationMantra: 'flow',
  motivationPulse: 3,
  celebrationReminders: true,
  dailyFocusGoal: 3,
  notifications: true,
};

export const usePreferencesStore = defineStore('preferences', () => {
  const settings = ref<PreferencesState>({ ...defaultPreferences });
  const hydrated = ref(false);

  const loadPreferences = () => {
    if (hydrated.value) return;
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        settings.value = { ...defaultPreferences, ...parsed };
      }
    } catch (error) {
      logger.warn('Failed to parse preferences', { error });
    } finally {
      hydrated.value = true;
    }
  };

  const persistPreferences = () => {
    if (!hydrated.value) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings.value));
  };

  const setPreference = <K extends keyof PreferencesState>(key: K, value: PreferencesState[K]) => {
    settings.value = { ...settings.value, [key]: value } as PreferencesState;
  };

  const resetPreferences = () => {
    settings.value = { ...defaultPreferences };
  };

  loadPreferences();

  watch(
    () => settings.value,
    () => persistPreferences(),
    { deep: true }
  );

  return {
    settings,
    hydrated,
    setPreference,
    resetPreferences,
    loadPreferences,
  };
});
