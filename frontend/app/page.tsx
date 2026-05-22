"use client";

import { useEffect, useMemo, useState } from 'react';

type HealthResponse = {
  status: string;
  service?: string;
  environment?: string;
  modules?: string[];
};

const defaultApiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://127.0.0.1:8000';

export default function Page() {
  const [apiBase, setApiBase] = useState(defaultApiBase);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const endpoints = useMemo(
    () => [
      '/health',
      '/api/v1/voters',
      '/api/v1/constituencies',
      '/api/v1/graph/network',
      '/api/v1/analytics/summary',
    ],
    []
  );

  useEffect(() => {
    setApiBase(defaultApiBase);
  }, []);

  async function checkHealth() {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiBase}/health`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = (await response.json()) as HealthResponse;
      setHealth(data);
    } catch (fetchError) {
      setHealth(null);
      setError(fetchError instanceof Error ? fetchError.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50">
      <section className="mx-auto flex min-h-screen max-w-6xl flex-col gap-8 px-6 py-10 lg:flex-row lg:items-center">
        <div className="flex-1 space-y-6">
          <span className="inline-flex rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-1 text-sm text-cyan-200">
            VoteGuard Nexus
          </span>
          <h1 className="max-w-2xl text-4xl font-semibold tracking-tight md:text-6xl">
            Modular voting operations, analytics, and verification in one place.
          </h1>
          <p className="max-w-2xl text-lg text-slate-300">
            This Next.js shell connects to the FastAPI backend, then grows into the admin, operator, and analytics surface.
          </p>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm text-slate-400">Backend base URL</p>
              <input
                value={apiBase}
                onChange={(event) => setApiBase(event.target.value)}
                className="mt-2 w-full rounded-xl border border-white/10 bg-slate-900 px-4 py-3 outline-none ring-0"
              />
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm text-slate-400">Current status</p>
              <p className="mt-2 text-xl font-medium text-cyan-300">{health?.status ?? 'idle'}</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={checkHealth}
              disabled={loading}
              className="rounded-full bg-cyan-400 px-5 py-3 font-medium text-slate-950 transition hover:bg-cyan-300 disabled:opacity-60"
            >
              {loading ? 'Checking…' : 'Check backend health'}
            </button>
            <a
              href={`${apiBase}/docs`}
              className="rounded-full border border-white/15 px-5 py-3 font-medium text-slate-100 transition hover:bg-white/5"
            >
              Open API docs
            </a>
            <a href="/login" className="rounded-full border border-white/15 px-5 py-3 font-medium text-slate-100 transition hover:bg-white/5">Login</a>
            <a href="/register" className="rounded-full border border-white/15 px-5 py-3 font-medium text-slate-100 transition hover:bg-white/5">Register</a>
          </div>

          {health && (
            <pre className="max-w-2xl overflow-auto rounded-2xl border border-white/10 bg-slate-900 p-4 text-sm text-slate-200">
              {JSON.stringify(health, null, 2)}
            </pre>
          )}
          {error && <p className="text-sm text-rose-300">{error}</p>}
        </div>

        <aside className="w-full max-w-xl rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-cyan-950/30">
          <h2 className="text-2xl font-semibold">Backend surface</h2>
          <ul className="mt-4 space-y-3 text-slate-300">
            {endpoints.map((endpoint) => (
              <li key={endpoint} className="rounded-xl border border-white/10 bg-slate-900/60 px-4 py-3">
                {endpoint}
              </li>
            ))}
          </ul>
        </aside>
      </section>
    </main>
  );
}
