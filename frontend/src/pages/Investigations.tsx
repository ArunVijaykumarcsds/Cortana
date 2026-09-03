import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PageHeader from "../components/PageHeader";
import RiskBadge from "../components/RiskBadge";
import { fetchInvestigations } from "../data/api";
import type { Investigation } from "../types";
import { formatTimestamp, pct } from "../utils/risk";

const STATUS_TONE: Record<string, string> = {
  OPEN: "text-ivory-dim",
  IN_REVIEW: "text-intel",
  ESCALATED: "text-(--color-high)",
  CLOSED: "text-mute",
};

export default function Investigations() {
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchInvestigations({ limit: 100 });
        if (mounted) setInvestigations(data);
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : "Failed to load investigations";
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
        eyebrow="Investigations"
        title="Case files"
        description="CORTANA detects. The analyst decides. Every case keeps a full audit trail of what happened and when."
      />

      <div className="px-5 py-6 md:px-8">
        {error ? (
          <div className="panel border-ruby/40 p-6 text-center">
            <p className="text-sm text-ruby">Failed to load investigations: {error}</p>
          </div>
        ) : loading ? (
          <div className="flex min-h-[200px] items-center justify-center">
            <span className="label-eyebrow animate-pulse">Loading Case Files…</span>
          </div>
        ) : investigations.length === 0 ? (
          <div className="panel p-10 text-center">
            <p className="text-sm text-mute">No open investigation cases found.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {investigations.map((c) => (
              <Link
                key={c.id}
                to={`/app/investigations/${c.id}`}
                className="panel flex flex-col gap-3 p-5 hover:border-intel/50"
              >
                <div className="flex items-start justify-between">
                  <span className="data-num text-sm text-ivory">{c.id}</span>
                  <RiskBadge level={c.risk_level} size="sm" />
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="data-num text-2xl font-medium text-ivory">{pct(c.risk_score)}</span>
                  <span className={`font-mono text-[10px] uppercase tracking-wider ${STATUS_TONE[c.status]}`}>
                    {c.status.replace("_", " ")}
                  </span>
                </div>
                <div className="flex items-center justify-between border-t border-hairline-soft pt-3 text-[11px] text-mute">
                  <span>{c.assigned_to || "Unassigned"}</span>
                  <span>{formatTimestamp(c.opened_at)}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
