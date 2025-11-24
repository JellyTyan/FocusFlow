/**
 * AI Service - Frontend service for AI generation endpoints
 * 
 * Provides methods for:
 * - Non-streaming chat completion
 * - Streaming chat completion (SSE)
 * - Health check
 */

import api from './api';
import { logApiError, getUserErrorMessage } from '../utils/errors';

export interface AIMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface GenerateAIRequest {
  messages: AIMessage[];
  model?: string;
  timeout?: number;
  stream?: boolean;
}

export interface GenerateAIResponse {
  content: string;
  model: string;
  finish_reason?: string;
}

export interface AIHealthResponse {
  enabled: boolean;
  available: boolean;
  default_model?: string;
}

/**
 * Generate AI chat completion (non-streaming)
 */
export async function generateAI(request: GenerateAIRequest): Promise<GenerateAIResponse> {
  try {
    const { data } = await api.post<GenerateAIResponse>('/ai/generate', {
      messages: request.messages,
      model: request.model,
      timeout: request.timeout,
      stream: false,
    });
    return data;
  } catch (error: unknown) {
    logApiError('ai/generate', error, { messages: request.messages.length });
    const errorMessage = getUserErrorMessage(
      error,
      'Nie udało się wygenerować odpowiedzi AI. Spróbuj ponownie.'
    );
    throw new Error(errorMessage);
  }
}

/**
 * Stream AI chat completion using Server-Sent Events (SSE)
 * 
 * @param request - Generation request
 * @param onChunk - Callback for each chunk
 * @param onError - Callback for errors
 * @param onComplete - Callback when stream completes
 */
export async function streamAI(
  request: GenerateAIRequest,
  onChunk: (chunk: string) => void,
  onError?: (error: Error) => void,
  onComplete?: () => void
): Promise<void> {
  try {
    const response = await fetch('/api/ai/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
      },
      body: JSON.stringify({
        messages: request.messages,
        model: request.model,
        timeout: request.timeout,
        stream: true,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          if (onComplete) onComplete();
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        
        // Process complete SSE events (separated by \n\n)
        let eventEndIndex;
        while ((eventEndIndex = buffer.indexOf('\n\n')) !== -1) {
          const event = buffer.substring(0, eventEndIndex);
          buffer = buffer.substring(eventEndIndex + 2);
          
          if (event.startsWith('data: ')) {
            try {
              const jsonStr = event.substring(6).trim();
              
              // Handle [DONE] marker
              if (jsonStr === '[DONE]') {
                if (onComplete) onComplete();
                return;
              }
              
              const data = JSON.parse(jsonStr);
              
              if (data.error) {
                throw new Error(data.error);
              }
              
              if (data.done) {
                if (onComplete) onComplete();
                return;
              }
              
              if (data.content) {
                // Call onChunk immediately for each chunk
                onChunk(data.content);
              }
            } catch (parseError) {
              if (event.length > 0 && !event.includes('keep-alive')) {
                console.warn('Nie udało się sparsować danych SSE:', event.substring(0, 100));
              }
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  } catch (error: unknown) {
    logApiError('ai/stream', error, { messages: request.messages.length });
    const errorMessage = getUserErrorMessage(
      error,
      'Nie udało się połączyć z AI. Spróbuj ponownie.'
    );
    const err = error instanceof Error ? error : new Error(errorMessage);
    if (onError) {
      onError(err);
    } else {
      throw err;
    }
  }
}

/**
 * Check AI service health
 */
export async function checkAIHealth(): Promise<AIHealthResponse> {
  try {
    const { data } = await api.get<AIHealthResponse>('/ai/health');
    return data;
  } catch (error: unknown) {
    logApiError('ai/health', error);
    // Return unavailable status on error
    return {
      enabled: false,
      available: false,
    };
  }
}

