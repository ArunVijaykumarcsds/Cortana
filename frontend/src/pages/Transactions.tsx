import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PageHeader from "../components/PageHeader";
import TransactionCard from "../components/TransactionCard";
import RiskBadge from "../components/RiskBadge";
import DecisionPill from "../components/DecisionPill";
import { fetchTransactions } from "../data/api";
import type { DatasetContext, RiskLevel, Transaction } from "../types";
import { formatCurrency, formatTimestamp, pct } from "../utils/risk";

const CONTEXTS: (DatasetContext | "ALL")[] = ["ALL", "PaySim", "ULB"];
const LEVELS: (RiskLevel | "ALL")[] = ["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"];

export default function Transactions() {
  const [context, setContext] = useState<DatasetContext | "ALL">("ALL");
  const [level, setLevel] = useState<RiskLevel | "ALL">("ALL");
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchTransactions({
          context: context === "ALL" ? undefined : context,
          risk_level: level === "ALL" ? undefined : level,
          limit: 100,
        });
        if (mounted) setTransactions(data);
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : "Failed to load transactions";
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
  }, [context, level]);

  return (
    <div>
      <PageHeader
        eyebrow="Transactions"
        title="All transactions"
        description="PaySim and ULB transactions are kept in separate dataset contexts, matching the fusion architecture."
      />

      <div className="flex flex-col gap-4 px-5 py-6 md:px-8">
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center gap-1.5 rounded-md border border-hairline p-1">
            {CONTEXTS.map((c) => (
              <button
                key={c}
                onClick={() => setContext(c)}
                aria-pressed={context === c}
                className={`rounded px-3 py-1.5 font-mono text-xs uppercase tracking-wider transition-colors ${
                  context === c ? "bg-surface-2 text-ivory" : "text-mute hover:text-ivory-dim"
                }`}
              >
                {c}
              </button>
            ))}
          </div>
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
          <span className="ml-auto self-center text-xs text-mute">{transactions.length} results</span>
        </div>

        {error ? (
          <div className="panel border-ruby/40 p-6 text-center">
            <p className="text-sm text-ruby">Failed to load transactions: {error}</p>
          </div>
        ) : loading ? (
          <div className="flex min-h-[250px] items-center justify-center">
            <span className="label-eyebrow animate-pulse">Loading Transactions…</span>
          </div>
        ) : transactions.length === 0 ? (
          <div className="panel p-10 text-center">
            <p className="text-sm text-mute">No transactions found matching the selected filters.</p>
          </div>
        ) : (
          <>
            {/* Desktop table */}
            <div className="hidden overflow-hidden rounded-md border border-hairline md:block">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-hairline bg-surface-2 text-mute">
                    <th className="label-eyebrow px-4 py-3 font-normal">ID</th>
                    <th className="label-eyebrow px-4 py-3 font-normal">Context</th>
                    <th className="label-eyebrow px-4 py-3 font-normal">Type</th>
                    <th className="label-eyebrow px-4 py-3 font-normal">Amount</th>
                    <th className="label-eyebrow px-4 py-3 font-normal">Risk score</th>
                    <th className="label-eyebrow px-4 py-3 font-normal">Level</th>
                    <th className="label-eyebrow px-4 py-3 font-normal">Decision</th>
                    <th className="label-eyebrow px-4 py-3 font-normal">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((t) => (
                    <tr key={t.id} className="border-b border-hairline-soft last:border-0 hover:bg-surface-2/50">
                      <td className="px-4 py-3">
                        <Link to={`/app/transactions/${t.id}`} className="data-num text-intel hover:underline">
                          {t.id}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-xs text-ivory-dim">{t.dataset_context}</td>
                      <td className="px-4 py-3 text-xs text-ivory-dim">{t.type}</td>
                      <td className="px-4 py-3 data-num text-ivory">{formatCurrency(t.amount, t.currency)}</td>
                      <td className="px-4 py-3 data-num text-ivory">{pct(t.fusion.fused_risk)}</td>
                      <td className="px-4 py-3">
                        <RiskBadge level={t.fusion.risk_level} size="sm" />
                      </td>
                      <td className="px-4 py-3">
                        <DecisionPill decision={t.fusion.decision} />
                      </td>
                      <td className="px-4 py-3 text-xs text-mute">{formatTimestamp(t.timestamp)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile cards */}
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:hidden">
              {transactions.map((t) => (
                <TransactionCard key={t.id} tx={t} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
