import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';
import { logApiError } from '../utils/errors';

export interface Session {
  id: string;
  topic_id: string;
  status: 'active' | 'paused' | 'completed';
  start_time: string;
  duration: number;
  stuck_moments: number;
}

export const useTimerStore = defineStore('timer', () => {
  const session = ref<Session | null>(null);
  const timeLeft = ref(25 * 60); // 25 minutes in seconds
  const isRunning = ref(false);
  const isPaused = ref(false);
  const showAIChat = ref(false);
  let intervalId: number | null = null;

  const progress = computed(() => {
    const total = 25 * 60;
    return ((total - timeLeft.value) / total) * 100;
  });

  const isLastMinute = computed(() => timeLeft.value <= 60);

  const formattedTime = computed(() => {
    const minutes = Math.floor(timeLeft.value / 60);
    const seconds = timeLeft.value % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  });

  async function startSession(topicId: string) {
    try {
      const { data } = await api.post('/sessions/start', { topic_id: topicId });
      session.value = data;
      timeLeft.value = 25 * 60;
      isRunning.value = true;
      isPaused.value = false;
      startTimer();
    } catch (error: unknown) {
      logApiError('timer/startSession', error, { topicId });
      throw error;
    }
  }

  function startTimer() {
    if (intervalId) clearInterval(intervalId);
    intervalId = window.setInterval(() => {
      if (timeLeft.value > 0) {
        timeLeft.value--;
      } else {
        completeSession();
      }
    }, 1000);
  }

  async function pause() {
    isRunning.value = false;
    isPaused.value = true;
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
    if (session.value) {
      try {
        await api.put(`/sessions/${session.value.id}/pause`);
      } catch (error: unknown) {
        logApiError('timer/pause', error, { sessionId: session.value.id });
      }
    }
  }

  async function resume() {
    isRunning.value = true;
    isPaused.value = false;
    startTimer();
    if (session.value) {
      try {
        await api.put(`/sessions/${session.value.id}/resume`);
      } catch (error: unknown) {
        logApiError('timer/resume', error, { sessionId: session.value.id });
      }
    }
  }

  async function completeSession() {
    isRunning.value = false;
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
    if (session.value) {
      try {
        await api.put(`/sessions/${session.value.id}/complete`);
      } catch (error: unknown) {
        logApiError('timer/complete', error, { sessionId: session.value.id });
      }
    }
    session.value = null;
  }

  async function toggleAIChat() {
    showAIChat.value = !showAIChat.value;
    if (showAIChat.value && session.value) {
      // Increment stuck_moments when opening chat
      // This will be tracked on backend when message is sent
      session.value.stuck_moments++;
    }
  }

  function reset() {
    if (intervalId) clearInterval(intervalId);
    session.value = null;
    timeLeft.value = 25 * 60;
    isRunning.value = false;
    isPaused.value = false;
    showAIChat.value = false;
  }

  return {
    session,
    timeLeft,
    isRunning,
    isPaused,
    showAIChat,
    progress,
    isLastMinute,
    formattedTime,
    startSession,
    pause,
    resume,
    completeSession,
    toggleAIChat,
    reset,
  };
});
