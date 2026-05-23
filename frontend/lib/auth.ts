export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://127.0.0.1:8000';

export async function register(email: string, password: string) {
  const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

export function setToken(token: string) {
  if (typeof window !== 'undefined') localStorage.setItem('vg_token', token);
}

export function getToken() {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('vg_token');
}

export async function apiFetch(path: string, opts: RequestInit = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) } as Record<string, string>;
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers });
  return res;
}
