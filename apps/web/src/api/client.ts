const baseURL = (import.meta as ImportMeta & {
  env: { VITE_API_URL?: string };
}).env.VITE_API_URL ?? 'http://localhost:8080';

export function getApiBaseUrl(): string {
  return baseURL || window.location.origin;
}

type RequestConfig = RequestInit & { params?: Record<string, string> };

async function extractErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (body && typeof body.detail === 'string') {
      return body.detail;
    }
  } catch {
    // Respuesta sin JSON
  }
  return `Error HTTP ${response.status}`;
}

const request = async <T>(path: string, config: RequestConfig = {}) => {
  const { params, ...init } = config;
  const url = new URL(path, getApiBaseUrl());

  Object.entries(params ?? {}).forEach(([key, value]) => url.searchParams.set(key, value));

  const headers = new Headers(init.headers);
  const token = localStorage.getItem('token');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');

  const response = await fetch(url, { ...init, headers });
  if (response.status === 401) {
    window.dispatchEvent(new Event('satori:unauthorized'));
  }
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  const data = response.status === 204 ? undefined : await response.json();
  return { data, status: response.status, headers: response.headers } as { data: T; status: number; headers: Headers };
};

export async function downloadAuthorizedFile(path: string, fallbackFilename: string): Promise<void> {
  const url = new URL(path, getApiBaseUrl());
  const headers = new Headers();
  const token = localStorage.getItem('token');
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const response = await fetch(url, { method: 'GET', headers });
  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = objectUrl;
  anchor.download = fallbackFilename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(objectUrl);
}

export const apiClient = {
  get: <T = unknown>(path: string, config?: RequestConfig) => request<T>(path, { ...config, method: 'GET' }),
  post: <T = unknown>(path: string, body?: unknown, config?: RequestConfig) =>
    request<T>(path, { ...config, method: 'POST', body: body !== undefined ? JSON.stringify(body) : undefined }),
  put: <T = unknown>(path: string, body?: unknown, config?: RequestConfig) =>
    request<T>(path, { ...config, method: 'PUT', body: body !== undefined ? JSON.stringify(body) : undefined }),
  patch: <T = unknown>(path: string, body?: unknown, config?: RequestConfig) =>
    request<T>(path, { ...config, method: 'PATCH', body: body !== undefined ? JSON.stringify(body) : undefined }),
  delete: <T = unknown>(path: string, config?: RequestConfig) => request<T>(path, { ...config, method: 'DELETE' }),
};
