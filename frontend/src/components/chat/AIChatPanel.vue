<template>
  <div
    class="fixed right-0 top-0 h-full w-full sm:w-96 max-w-full sm:max-w-md glass-card rounded-none sm:rounded-l-3xl border-l-2 border-sea-mint transform transition-transform duration-300 flex flex-col z-50"
    :class="show ? 'translate-x-0' : 'translate-x-full'"
  >
    <div class="p-4 sm:p-6 border-b border-soft-ice/10 flex items-center justify-between">
      <h3 class="text-lg sm:text-xl font-bold">💬 Asystent AI</h3>
      <button @click="$emit('close')" class="text-text-secondary hover:text-text-primary text-xl sm:text-2xl w-8 h-8 flex items-center justify-center" aria-label="Zamknij">
        ✕
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-3 sm:space-y-4">
      <div v-if="loadingHistory" class="text-text-secondary text-center py-8">
        Ładowanie historii...
      </div>
      <div v-else-if="messages.length === 0" class="text-text-secondary text-center py-8">
        Zadaj pytanie dotyczące tematu "{{ topicName }}"
      </div>
      
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="msg.role === 'user' ? 'ml-8' : 'mr-8'"
      >
        <div
          :class="[
            'p-3 rounded-xl',
            msg.role === 'user' ? 'bg-sea-mint/20 text-right' : 'bg-soft-ice/10'
          ]"
        >
          <div class="text-xs text-text-secondary mb-1">
            {{ msg.role === 'user' ? '👤 Ty' : '🤖 AI' }}
          </div>
          <div class="whitespace-pre-wrap break-words">{{ msg.content }}</div>
        </div>
      </div>

      <div v-if="loading || streaming" class="flex gap-2 items-center text-sea-mint">
        <div class="w-2 h-2 bg-sea-mint rounded-full animate-bounce" style="animation-delay: 0ms"></div>
        <div class="w-2 h-2 bg-sea-mint rounded-full animate-bounce" style="animation-delay: 150ms"></div>
        <div class="w-2 h-2 bg-soft-coral rounded-full animate-bounce" style="animation-delay: 300ms"></div>
        <span v-if="streaming" class="text-xs text-text-secondary ml-2">Pisanie...</span>
      </div>
    </div>

    <div class="p-4 sm:p-6 border-t border-soft-ice/10">
      <form @submit.prevent="sendMessage" class="flex gap-2">
        <input
          v-model="input"
          type="text"
          placeholder="Zadaj pytanie..."
          :disabled="loading"
          class="flex-1 px-3 sm:px-4 py-2 text-sm sm:text-base bg-deep-indigo/50 rounded-xl border border-soft-ice/10 focus:border-sea-mint outline-none disabled:opacity-50"
        />
        <button
          type="submit"
          :disabled="!input.trim() || loading"
          class="px-4 sm:px-6 py-2 bg-sea-mint text-deep-indigo rounded-xl font-semibold hover:scale-105 transition-transform disabled:opacity-50 disabled:hover:scale-100 text-lg sm:text-xl flex-shrink-0"
          aria-label="Wyślij"
        >
          →
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import api from '../../services/api';
import { generateAI, streamAI, type AIMessage } from '../../services/ai.service';
import { logApiError, getUserErrorMessage } from '../../utils/errors';

const props = defineProps<{
  show: boolean;
  topicName: string;
  sessionId?: string;
  useStreaming?: boolean;
}>();

const useStreaming = computed(() => props.useStreaming !== false);

defineEmits<{
  close: [];
}>();

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

const messages = ref<Message[]>([]);
const input = ref('');
const loading = ref(false);
const loadingHistory = ref(false);
const streaming = ref(false);

watch(() => props.show, async (newVal) => {
  if (newVal && props.sessionId) {
    await loadChatHistory();
  }
});

async function loadChatHistory() {
  if (!props.sessionId) return;
  
  loadingHistory.value = true;
  try {
    const { data } = await api.get(`/chat/${props.sessionId}/history`);
    messages.value = data.messages.map((msg: unknown) => {
      if (typeof msg === 'object' && msg !== null && 'role' in msg && 'content' in msg) {
        return {
          role: msg.role as 'user' | 'assistant',
          content: String(msg.content),
          timestamp: 'timestamp' in msg ? String(msg.timestamp) : undefined,
        };
      }
      return { role: 'assistant' as const, content: String(msg), timestamp: undefined };
    });
  } catch (e: unknown) {
    logApiError('chat/loadHistory', e, { sessionId: props.sessionId });
    messages.value = [];
  } finally {
    loadingHistory.value = false;
  }
}

const sendMessage = async () => {
  if (!input.value.trim() || !props.sessionId) return;

  const userMessage = input.value.trim();
  messages.value.push({ role: 'user', content: userMessage });
  input.value = '';
  loading.value = true;

  try {
    const aiMessages: AIMessage[] = [
      {
        role: 'system',
        content: `Jesteś pomocnym asystentem AI w aplikacji FocusFlow. Użytkownik studiuje temat: "${props.topicName}". Twoim zadaniem jest pomagać w zrozumieniu materiału, odpowiadać na pytania i motywować do kontynuacji nauki. Odpowiadaj po polsku, zwięźle i pomocnie.`,
      },
    ];

    const recentHistory = messages.value.slice(-10);
    for (const msg of recentHistory) {
      if (msg.role === 'user' || msg.role === 'assistant') {
        aiMessages.push({
          role: msg.role,
          content: msg.content,
        });
      }
    }

    if (useStreaming.value) {
      streaming.value = true;
      const assistantMessageIndex = messages.value.length;
      const assistantMessage: Message = {
        role: 'assistant',
        content: '',
      };
      messages.value.push(assistantMessage);

      await streamAI(
        { messages: aiMessages },
        (chunk: string) => {
          if (messages.value[assistantMessageIndex] && chunk) {
            const currentContent = messages.value[assistantMessageIndex].content;
            messages.value[assistantMessageIndex].content = currentContent + chunk;
          }
        },
        (error: Error) => {
          logApiError('ai/stream', error, { sessionId: props.sessionId });
          if (messages.value[assistantMessageIndex]) {
            messages.value[assistantMessageIndex].content = getUserErrorMessage(
              error,
              'Przepraszam, wystąpił błąd podczas generowania odpowiedzi. Spróbuj ponownie.'
            );
          }
          streaming.value = false;
          loading.value = false;
        },
        async () => {
          streaming.value = false;
          loading.value = false;
          
          if (props.sessionId) {
            setTimeout(async () => {
              try {
                await api.post('/chat/message', {
                  session_id: props.sessionId,
                  content: userMessage,
                });
                
                const finalContent = messages.value[assistantMessageIndex]?.content || assistantMessage.content;
                if (finalContent) {
                  await api.post('/chat/message', {
                    session_id: props.sessionId,
                    content: finalContent,
                  });
                }
              } catch (e: unknown) {
                logApiError('chat/saveMessages', e, { sessionId: props.sessionId });
              }
            }, 0);
          }
        }
      );
    } else {
      const response = await generateAI({ messages: aiMessages });
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.content,
      };
      messages.value.push(assistantMessage);
      
      loading.value = false;

      if (props.sessionId) {
        setTimeout(async () => {
          try {
            await api.post('/chat/message', {
              session_id: props.sessionId,
              content: userMessage,
            });
            
            await api.post('/chat/message', {
              session_id: props.sessionId,
              content: response.content,
            });
          } catch (e: unknown) {
            logApiError('chat/saveMessages', e, { sessionId: props.sessionId });
          }
        }, 0);
      }
    }
  } catch (e: unknown) {
    logApiError('ai/generate', e, { sessionId: props.sessionId });
    const errorMessage = getUserErrorMessage(
      e,
      'Przepraszam, wystąpił błąd. Spróbuj ponownie.'
    );
    messages.value.push({
      role: 'assistant',
      content: errorMessage,
    });
  } finally {
    loading.value = false;
    streaming.value = false;
  }
};
</script>
