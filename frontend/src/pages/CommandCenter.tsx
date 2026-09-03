import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PageHeader from "../components/PageHeader";
import MetricCard from "../components/MetricCard";
import RiskBadge from "../components/RiskBadge";
import DecisionPill from "../components/DecisionPill";
import RiskDistributionChart from "../dashboard/RiskDistributionChart";
import DecisionTrendChart from "../dashboard/DecisionTrendChart";
import { fetchTransactions, fetchAlerts, isMockMode } from "../data/api";
import type { Alert, Transaction } from "../types";
import { FUSION_FINAL_TEST } from "../data/cortanaConfig";
import { formatCompactCurrency, formatTimestamp, pct } from "../utils/risk";

export default function CommandCenter() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [txList, alertList] = await Promise.all([
          fetchTransactions({ limit: 100 }),
          fetchAlerts({ limit: 100 }),
        ]);
        if (mounted) {
          setTransactions(txList);
          setAlerts(alertList);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : "Failed to load command center data";
          setError(msg);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }
    loadData();
    return () => {
      mounted = false;
    };
  }, []);

  const total = transactions.length;
  const critical = transactions.filter((t) => t.fusion.risk_level === "CRITICAL").length;
  const highRisk = transactions.filter(
    (t) => t.fusion.risk_level === "HIGH" || t.fusion.risk_level === "CRITICAL"
  ).length;
  const reviewQueue = alerts.filter((a) => a.status !== "RESOLVED").length;
  const volume = transactions.reduce((s, t) => s + t.amount, 0);

  const attention = [...transactions]
    .sort((a, b) => b.fusion.fused_risk - a.fusion.fused_risk)
    .slice(0, 6);

  return (
    <div>
      <PageHeader
        eyebrow="Command Center"
        title="What needs attention"
        description="A live view of transaction volume, risk distribution, and the review queue backed by the CORTANA Risk Engine."
      />

      <div className="px-5 py-6 md:px-8">
        {/* Sample-data or Backend status notice */}
        {isMockMode() ? (
          <div className="mb-6 rounded-md border border-hairline-soft bg-surface-2/40 px-4 py-2.5 text-xs text-mute">
            Running in offline demo mode with seeded mock transactions. Set{" "}
            <code className="font-mono text-ivory-dim">VITE_USE_MOCK_DATA=false</code> to connect to the live backend.
          </div>
        ) : (
          <div className="mb-6 rounded-md border border-emerald-500/20 bg-emerald-500/5 px-4 py-2.5 text-xs text-emerald-400">
            Connected to CORTANA FastAPI Backend · Real-time inference scoring active.
          </div>
        )}

        {error ? (
          <div className="panel mb-6 border-ruby/40 p-6 text-center">
            <p className="text-sm text-ruby">Backend Connection Error: {error}</p>
            <p className="mt-1 text-xs text-mute">Verify that the FastAPI server is running on the configured API base URL.</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 rounded-md border border-hairline bg-surface-2 px-3 py-1.5 font-mono text-xs uppercase tracking-wider text-ivory hover:bg-surface-3"
            >
              Retry Connection
            </button>
          </div>
        ) : loading ? (
          <div className="flex min-h-[300px] items-center justify-center">
            <span className="label-eyebrow animate-pulse">Loading Telemetry…</span>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
              <MetricCard label="Transactions processed" value={total.toLocaleString()} sublabel="Monitored window" />
              <MetricCard label="Total volume" value={formatCompactCurrency(volume)} sublabel="All monitored transactions" />
              <MetricCard label="High risk" value={highRisk.toLocaleString()} deltaTone="up" delta={total > 0 ? pct(highRisk / total) : "0%"} />
              <MetricCard label="Critical" value={critical.toLocaleString()} deltaTone="up" delta={total > 0 ? pct(critical / total) : "0%"} />
              <MetricCard label="Review queue" value={reviewQueue.toLocaleString()} sublabel="Open + under review" />
            </div>

            <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
              <RiskDistributionChart transactions={transactions} />
              <DecisionTrendChart transactions={transactions} />
            </div>

            <div className="mt-6 panel">
              <div className="flex items-center justify-between border-b border-hairline px-5 py-4">
                <h2 className="font-mono text-xs uppercase tracking-wider text-ivory-dim">
                  Needs attention now
                </h2>
                <Link to="/app/alerts" className="text-xs text-intel hover:underline">
                  View all alerts
                </Link>
              </div>
              {attention.length === 0 ? (
                <div className="p-8 text-center text-xs text-mute">No transactions in attention queue.</div>
              ) : (
                <ul>
                  {attention.map((t) => (
                    <li key={t.id} className="border-b border-hairline-soft last:border-0">
                      <Link
                        to={`/app/transactions/${t.id}`}
                        className="flex items-center justify-between gap-3 px-5 py-3 hover:bg-surface-2/50"
                      >
                        <div className="flex min-w-0 items-center gap-3">
                          <RiskBadge level={t.fusion.risk_level} size="sm" />
                          <span className="data-num truncate text-sm text-ivory">{t.id}</span>
                          <span className="hidden text-xs text-mute sm:inline">{t.dataset_context}</span>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="data-num hidden text-xs text-mute sm:inline">
                            {formatTimestamp(t.timestamp)}
                          </span>
                          <DecisionPill decision={t.fusion.decision} />
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="mt-6 panel p-5">
              <p className="label-eyebrow">Fraud detection performance — final test evaluation</p>
              <div className="mt-3 grid grid-cols-2 gap-4 sm:grid-cols-4">
                <div>
                  <p className="data-num text-xl text-ivory">{pct(FUSION_FINAL_TEST.recall)}</p>
                  <p className="text-[11px] text-mute">Recall</p>
                </div>
                <div>
                  <p className="data-num text-xl text-ivory">{pct(FUSION_FINAL_TEST.precision)}</p>
                  <p className="text-[11px] text-mute">Precision</p>
                </div>
                <div>
                  <p className="data-num text-xl text-ivory">{pct(FUSION_FINAL_TEST.rocAuc)}</p>
                  <p className="text-[11px] text-mute">ROC-AUC</p>
                </div>
                <div>
                  <p className="data-num text-xl text-ivory">
                    {FUSION_FINAL_TEST.fraudDetected}/{FUSION_FINAL_TEST.knownFraud}
                  </p>
                  <p className="text-[11px] text-mute">Fraud caught</p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
