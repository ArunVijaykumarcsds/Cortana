import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import SystemStatusIndicator from "../components/SystemStatusIndicator";
import { fetchSystemStatus, isMockMode } from "../data/api";
import type { SystemStatus } from "../types";
import { RELEASE, DECISION_THRESHOLD, FUSION_WEIGHTS } from "../data/cortanaConfig";

export default function SystemPage() {
  const [services, setServices] = useState<SystemStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchSystemStatus();
        if (mounted) setServices(data.services);
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : "Failed to load system status";
          setError(msg);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div>
      <PageHeader
        eyebrow="System"
        title="System status"
        description="Live operational state of every CORTANA pipeline component, verified through backend telemetry."
      />

      <div className="space-y-6 px-5 py-6 md:px-8">
        {/* Notice */}
        {isMockMode() && (
          <div className="rounded-md border border-hairline-soft bg-surface-2/40 px-4 py-2.5 text-xs text-mute">
            Displaying static baseline configuration (Mock mode active).
          </div>
        )}

        {error ? (
          <div className="panel border-ruby/40 p-6 text-center">
            <p className="text-sm text-ruby">Backend Status Unavailable: {error}</p>
          </div>
        ) : loading ? (
          <div className="flex min-h-[200px] items-center justify-center">
            <span className="label-eyebrow animate-pulse">Checking System Health…</span>
          </div>
        ) : (
          <div className="panel overflow-hidden">
            {services.map((s, i) => (
              <div
                key={s.service}
                className={`flex items-center justify-between px-5 py-4 ${
                  i !== services.length - 1 ? "border-b border-hairline-soft" : ""
                }`}
              >
                <div>
                  <p className="text-sm text-ivory">{s.service}</p>
                  <p className="mt-0.5 text-[11px] text-mute">{s.detail}</p>
                </div>
                <SystemStatusIndicator state={s.state} />
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="panel p-5">
            <p className="label-eyebrow">Model version</p>
            <p className="mt-1 text-sm text-ivory">{RELEASE.releaseName}</p>
          </div>
          <div className="panel p-5">
            <p className="label-eyebrow">Deployment phase</p>
            <p className="mt-1 text-sm text-ivory">{RELEASE.phase} — Final</p>
          </div>
          <div className="panel p-5">
            <p className="label-eyebrow">Package status</p>
            <p className="mt-1 text-sm text-ivory">Smoke-tested, artifact-reproducible</p>
          </div>
        </div>

        <div className="panel p-5">
          <p className="label-eyebrow">Locked production policy</p>
          <p className="mt-2 text-xs leading-relaxed text-mute">
            Fusion weights — Model 1 {FUSION_WEIGHTS.model_1}, Model 2 {FUSION_WEIGHTS.model_2}, Rules{" "}
            {FUSION_WEIGHTS.rules}. Decision threshold {DECISION_THRESHOLD}. This policy is set by the ML core in{" "}
            <span className="font-mono text-ivory-dim">{RELEASE.releaseName}</span> and is not modified by the frontend.
          </p>
        </div>
      </div>
    </div>
  );
}
