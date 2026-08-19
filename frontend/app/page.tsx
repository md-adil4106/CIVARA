"use client";

import { useEffect, useState } from "react";

interface HealthResponse {
  status: string;
  db: boolean;
}

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/health`, { cache: "no-store" });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data: HealthResponse = await res.json();
      setHealth(data);
    } catch (err: any) {
      setError(err?.message || "Failed to reach backend");
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-950 text-slate-100">
      <div className="max-w-xl w-full bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-2xl space-y-6">
        <div className="border-b border-slate-800 pb-4">
          <h1 className="text-3xl font-bold tracking-tight text-emerald-400">
            CIVARA
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            SIH25031 &bull; MOOLKARAN Engine Scaffolding (Phase 0)
          </p>
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-200">
            System Connectivity Status
          </h2>

          {loading ? (
            <div className="flex items-center space-x-3 text-slate-400 bg-slate-800/50 p-4 rounded-lg">
              <div className="w-4 h-4 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
              <span>Checking backend connection...</span>
            </div>
          ) : error ? (
            <div className="bg-red-950/40 border border-red-800 p-4 rounded-lg text-red-300 space-y-2">
              <div className="flex items-center space-x-2 font-medium">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span>
                <span>Backend disconnected</span>
              </div>
              <p className="text-xs text-red-400 font-mono">Error: {error}</p>
            </div>
          ) : health && health.db ? (
            <div className="bg-emerald-950/40 border border-emerald-800 p-4 rounded-lg text-emerald-300 space-y-2">
              <div className="flex items-center space-x-2 font-medium text-lg">
                <span className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Backend connected</span>
              </div>
              <p className="text-xs text-emerald-400">
                FastAPI service is running and PostgreSQL (PostGIS) connection verified.
              </p>
            </div>
          ) : (
            <div className="bg-amber-950/40 border border-amber-800 p-4 rounded-lg text-amber-300 space-y-2">
              <div className="flex items-center space-x-2 font-medium">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                <span>Backend reachable, but Database is disconnected</span>
              </div>
              <p className="text-xs text-amber-400">
                FastAPI responded, but <code>SELECT 1</code> against PostgreSQL failed.
              </p>
            </div>
          )}
        </div>

        <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
          <span>Target API: <code className="text-slate-300">{apiUrl}</code></span>
          <button
            onClick={fetchHealth}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded transition text-xs font-medium"
          >
            Recheck
          </button>
        </div>
      </div>
    </main>
  );
}
