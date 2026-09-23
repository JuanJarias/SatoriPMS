const baseURL = (import.meta as ImportMeta & {
  env: { VITE_API_URL?: string };
}).env.VITE_API_URL ?? '';

type RequestConfig = RequestInit & { params?: Record<string, string> };

const request = async <T>(path: string, config: RequestConfig = {}) => {
  const { params, ...init } = config;
  const url = new URL(path, baseURL || window.location.origin);

  Object.entries(params ?? {}).forEach(([key, value]) => url.searchParams.set(key, value));

  const headers = new Headers(init.headers);
  const token = localStorage.getItem('token');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');

  const response = await fetch(url, { ...init, headers });
  const data = response.status === 204 ? undefined : await response.json();
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return { data, status: response.status, headers: response.headers } as { data: T; status: number; headers: Headers };
};

export const apiClient = {
  get: <T = unknown>(path: string, config?: RequestConfig) => request<T>(path, { ...config, method: 'GET' }),
  post: <T = unknown>(path: string, body?: unknown, config?: RequestConfig) =>
    request<T>(path, { ...config, method: 'POST', body: JSON.stringify(body) }),
  put: <T = unknown>(path: string, body?: unknown, config?: RequestConfig) =>
    request<T>(path, { ...config, method: 'PUT', body: JSON.stringify(body) }),
  delete: <T = unknown>(path: string, config?: RequestConfig) => request<T>(path, { ...config, method: 'DELETE' }),
};
