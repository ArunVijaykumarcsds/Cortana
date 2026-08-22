import { useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";
import TransactionCard from "../components/TransactionCard";
import RiskBadge from "../components/RiskBadge";
import DecisionPill from "../components/DecisionPill";
import { Link } from "react-router-dom";
import { MOCK_TRANSACTIONS } from "../data/mock/generator";
import type { DatasetContext, RiskLevel } from "../types";
import { formatCurrency, formatTimestamp, pct } from "../utils/risk";

const CONTEXTS: (DatasetContext | "ALL")[] = ["ALL", "PaySim", "ULB"];
const LEVELS: (RiskLevel | "ALL")[] = ["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"];

export default function Transactions() {
  const [context, setContext] = useState<DatasetContext | "ALL">("ALL");
  const [level, setLevel] = useState<RiskLevel | "ALL">("ALL");

  const filtered = useMemo(
    () =>
      MOCK_TRANSACTIONS.filter(
        (t) =>
          (context === "ALL" || t.dataset_context === context) &&
          (level === "ALL" || t.fusion.risk_level === level)
      ),
    [context, level]
  );

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
          <span className="ml-auto self-center text-xs text-mute">{filtered.length} results</span>
        </div>

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
              {filtered.map((t) => (
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
          {filtered.map((t) => (
            <TransactionCard key={t.id} tx={t} />
          ))}
        </div>
      </div>
    </div>
  );
}
