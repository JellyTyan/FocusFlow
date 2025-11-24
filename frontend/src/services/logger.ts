const LOG_ENDPOINT = '/api/logs';

interface LogEntry {
  level: 'info' | 'warn' | 'error';
  message: string;
  meta?: Record<string, unknown>;
  timestamp: string;
}

const STORAGE_KEY = 'focusflow:logs';
const MAX_LOGS = 200;

function readLogs(): LogEntry[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw);
  } catch (error) {
    console.warn('[logger] Failed to parse logs', error);
    return [];
  }
}

function persist(entry: LogEntry) {
  const logs = readLogs();
  logs.push(entry);
  while (logs.length > MAX_LOGS) {
    logs.shift();
  }
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(logs));
  } catch (error) {
    console.warn('[logger] Failed to persist logs', error);
  }
}

function sendToServer(entry: LogEntry) {
  try {
    const payload = {
      level: entry.level,
      message: entry.message,
      meta: entry.meta,
      timestamp: entry.timestamp,
      path: typeof window !== 'undefined' ? window.location.pathname : undefined,
    };
    const body = JSON.stringify(payload);

    if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
      const blob = new Blob([body], { type: 'application/json' });
      navigator.sendBeacon(LOG_ENDPOINT, blob);
    } else {
      fetch(LOG_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
        keepalive: true,
      }).catch(() => {});
    }
  } catch (error) {
    console.warn('[logger] Failed to send log', error);
  }
}

function emit(level: LogEntry['level'], message: string, meta?: Record<string, unknown>) {
  const entry: LogEntry = {
    level,
    message,
    meta,
    timestamp: new Date().toISOString(),
  };

  if (level === 'error') {
    console.error('[FocusFlow]', message, meta);
  } else if (level === 'warn') {
    console.warn('[FocusFlow]', message, meta);
  } else {
    console.log('[FocusFlow]', message, meta);
  }

  persist(entry);

  if (level === 'error') {
    sendToServer(entry);
  }
}

export const logger = {
  info(message: string, meta?: Record<string, unknown>) {
    emit('info', message, meta);
  },
  warn(message: string, meta?: Record<string, unknown>) {
    emit('warn', message, meta);
  },
  error(message: string, meta?: Record<string, unknown>) {
    emit('error', message, meta);
  },
  getLogs(): LogEntry[] {
    return readLogs();
  },
  clear() {
    localStorage.removeItem(STORAGE_KEY);
  },
};

if (typeof window !== 'undefined') {
  (window as typeof window & { focusFlowLogs?: typeof logger }).focusFlowLogs = logger;
}
