const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "";
const API_BASE_URL = rawApiBaseUrl.replace(/\/$/, "");

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Error ${response.status}`);
  }

  return (await response.json()) as T;
}

export { API_BASE_URL };