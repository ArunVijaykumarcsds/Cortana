import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import AlertTable from "../alerts/AlertTable";
import { fetchAlerts } from "../data/api";
import type { Alert, Decision, RiskLevel } from "../types";

const LEVELS: (RiskLevel | "ALL")[] = ["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"];
const DECISIONS: (Decision | "ALL")[] = ["ALL", "PASS", "REVIEW"];

export default function Alerts() {
  const [level, setLevel] = useState<RiskLevel | "ALL">("ALL");
  const [decision, setDecision] = useState<Decision | "ALL">("ALL");
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchAlerts({
          risk_level: level === "ALL" ? undefined : level,
          limit: 100,
        });
        if (mounted) {
          const filtered = data.filter((a) => decision === "ALL" || a.decision === decision);
          setAlerts(filtered);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : "Failed to load alerts";
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
  }, [level, decision]);

  return (
    <div>
      <PageHeader
        eyebrow="Alerts"
        title="Alert queue"
        description="Every alert traces back to a fused CORTANA risk score. Filter by level or decision, then open the transaction."
      />

      <div className="flex flex-col gap-4 px-5 py-6 md:px-8">
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center gap-1.5 rounded-md border border-hairline p-1">
            {LEVELS.map((l) => (
              <button
                key={l}
                onClick={() => setLevel(l)}
                aria-pressed={level === l}
                className={`rounded px-3 py-1.5 font-mono text-xs uppercase tracking-wider transition-colors ${
                  level === l ? "bg-surface-2 text-ivory" : "text-mute hover:text-ivory-dim"
                }`}
              >
                {l}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-1.5 rounded-md border border-hairline p-1">
            {DECISIONS.map((d) => (
              <button
                key={d}
                onClick={() => setDecision(d)}
                aria-pressed={decision === d}
                className={`rounded px-3 py-1.5 font-mono text-xs uppercase tracking-wider transition-colors ${
                  decision === d ? "bg-surface-2 text-ivory" : "text-mute hover:text-ivory-dim"
                }`}
              >
                {d}
              </button>
            ))}
          </div>
          <span className="ml-auto self-center text-xs text-mute">{alerts.length} alerts</span>
        </div>

        {error ? (
          <div className="panel border-ruby/40 p-6 text-center">
            <p className="text-sm text-ruby">Failed to load alerts: {error}</p>
          </div>
        ) : loading ? (
          <div className="flex min-h-[200px] items-center justify-center">
            <span className="label-eyebrow animate-pulse">Loading Alerts…</span>
          </div>
        ) : (
          <AlertTable alerts={alerts} />
        )}
      </div>
    </div>
  );
}
