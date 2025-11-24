import type { AxiosError } from 'axios';
import { logger } from '../services/logger';

const statusMessages: Record<number, string> = {
  400: 'Żądanie odrzucone. Sprawdź wypełnione pola i spróbuj ponownie.',
  401: 'Sesja wygasła. Zaloguj się ponownie.',
  403: 'Nie masz uprawnień do tej akcji.',
  404: 'Żądane dane nie zostały znalezione.',
  409: 'Takie dane już istnieją. Spróbuj innej wartości.',
  422: 'Niektóre pola są wypełnione nieprawidłowo. Popraw błędy i spróbuj ponownie.',
  429: 'Zbyt wiele żądań. Poczekaj chwilę i spróbuj ponownie.',
  500: 'Serwer tymczasowo niedostępny. Spróbuj później.',
  503: 'Usługa AI jest tymczasowo niedostępna. Spróbuj później.',
  504: 'Żądanie AI przekroczyło limit czasu. Spróbuj ponownie.',
};

function parsePayload(payload?: unknown) {
  if (!payload) return undefined;
  if (typeof payload === 'string') {
    try {
      return JSON.parse(payload);
    } catch {
      return payload;
    }
  }
  return payload;
}

function isAxiosError(error: unknown): error is AxiosError {
  return typeof error === 'object' && error !== null && 'response' in error;
}

function extractAxiosMeta(error: unknown): {
  status?: number;
  statusText?: string;
  url?: string;
  method?: string;
  detail?: string | unknown;
  payload?: unknown;
} {
  if (!isAxiosError(error)) {
    return {
      status: undefined,
      statusText: undefined,
      url: undefined,
      method: undefined,
      detail: error instanceof Error ? error.message : String(error),
      payload: undefined,
    };
  }

  const response = error.response;
  const config = error.config || response?.config;
  const data = response?.data as { detail?: unknown } | undefined;
  return {
    status: response?.status,
    statusText: response?.statusText,
    url: config?.url,
    method: config?.method,
    detail: data?.detail || error.message,
    payload: parsePayload(config?.data),
  };
}

export function getUserErrorMessage(error: unknown, fallback: string): string {
  if (isAxiosError(error)) {
    const responseData = error.response?.data;
    if (responseData && typeof responseData === 'object' && 'detail' in responseData) {
      const detail = responseData.detail;
      if (typeof detail === 'string') {
        return detail;
      }
      if (Array.isArray(detail)) {
        return detail.map((err: unknown) => {
          if (typeof err === 'object' && err !== null && 'msg' in err) {
            return String(err.msg);
          }
          return String(err);
        }).join('; ');
      }
    }

    const status = error.response?.status;
    if (status && statusMessages[status]) {
      return statusMessages[status];
    }

    if (error.message?.toLowerCase().includes('network')) {
      return 'Brak połączenia z serwerem. Sprawdź internet lub spróbuj później.';
    }

    if (error.code === 'ECONNABORTED') {
      return 'Czas oczekiwania na odpowiedź wygasł. Spróbuj ponownie.';
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return fallback;
}

export function logApiError(scope: string, error: unknown, extra?: Record<string, unknown>) {
  const meta = {
    scope,
    ...extractAxiosMeta(error),
    ...extra,
  };
  logger.error('API error', meta);
}

export function processApiError(scope: string, error: unknown, fallback: string, extra?: Record<string, unknown>): string {
  logApiError(scope, error, extra);
  return getUserErrorMessage(error, fallback);
}
