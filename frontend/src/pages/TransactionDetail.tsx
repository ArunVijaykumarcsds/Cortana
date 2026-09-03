import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ShieldAlert, ListChecks, Radar } from "lucide-react";
import { fetchTransactionById } from "../data/api";
import type { Transaction } from "../types";
import RiskBadge from "../components/RiskBadge";
import DecisionPill from "../components/DecisionPill";
import RiskScore from "../components/RiskScore";
import SignalCard from "../components/SignalCard";
import AIExplanation from "../components/AIExplanation";
import { formatCurrency, formatTimestamp, pct } from "../utils/risk";

const RULE_LABEL: Record<string, string> = {
  HIGH_AMOUNT: "High amount",
  ORIGIN_BALANCE_INCONSISTENCY: "Origin balance inconsistency",
  DESTINATION_BALANCE_INCONSISTENCY: "Destination balance inconsistency",
  LARGE_BALANCE_CHANGE: "Large balance change",
  HIGH_RISK_TRANSACTION_TYPE: "High-risk transaction type",
  ZERO_BALANCE_ANOMALY: "Zero-balance anomaly",
};

export default function TransactionDetail() {
  const { id } = useParams();
  const [tx, setTx] = useState<Transaction | null | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      if (!id) {
        setTx(null);
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        setError(null);
        const data = await fetchTransactionById(id);
        if (mounted) setTx(data || null);
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : "Failed to load transaction";
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
  }, [id]);

  if (loading) {
    return (
      <div className="flex min-h-[300px] items-center justify-center">
        <span className="label-eyebrow animate-pulse">Loading Transaction Details…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-5 py-10 md:px-8">
        <div className="panel border-ruby/40 p-6 text-center">
          <p className="text-sm text-ruby">Error: {error}</p>
          <Link to="/app/transactions" className="mt-4 inline-block text-sm text-intel hover:underline">
            Back to transactions
          </Link>
        </div>
      </div>
    );
  }

  if (!tx) {
    return (
      <div className="px-5 py-10 md:px-8">
        <p className="text-sm text-mute">Transaction '{id}' not found.</p>
        <Link to="/app/transactions" className="mt-3 inline-block text-sm text-intel hover:underline">
          Back to transactions
        </Link>
      </div>
    );
  }

  const rules = tx.rules?.triggered ?? [];

  return (
    <div>
      <div className="flex items-center gap-3 border-b border-hairline px-5 py-6 md:px-8">
        <Link to="/app/transactions" className="text-mute hover:text-ivory">
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
        </Link>
        <div>
          <p className="label-eyebrow">Transaction</p>
          <h1 className="font-display text-2xl text-ivory md:text-3xl">{tx.id}</h1>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <RiskBadge level={tx.fusion.risk_level} />
          <DecisionPill decision={tx.fusion.decision} />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 px-5 py-6 md:px-8 lg:grid-cols-3">
        {/* Left: details */}
        <div className="space-y-6 lg:col-span-2">
          <div className="panel p-5">
            <p className="label-eyebrow">Transaction details</p>
            <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-4 sm:grid-cols-3">
              <div>
                <dt className="text-[11px] text-mute">Dataset context</dt>
                <dd className="mt-0.5 text-sm text-ivory">{tx.dataset_context}</dd>
              </div>
              <div>
                <dt className="text-[11px] text-mute">Type</dt>
                <dd className="mt-0.5 text-sm text-ivory">{tx.type}</dd>
              </div>
              <div>
                <dt className="text-[11px] text-mute">Amount</dt>
                <dd className="data-num mt-0.5 text-sm text-ivory">{formatCurrency(tx.amount, tx.currency)}</dd>
              </div>
              <div>
                <dt className="text-[11px] text-mute">Origin account</dt>
                <dd className="data-num mt-0.5 text-sm text-ivory">{tx.origin_account || "—"}</dd>
              </div>
              <div>
                <dt className="text-[11px] text-mute">Destination account</dt>
                <dd className="data-num mt-0.5 text-sm text-ivory">{tx.destination_account || "—"}</dd>
              </div>
              <div>
                <dt className="text-[11px] text-mute">Timestamp</dt>
                <dd className="mt-0.5 text-sm text-ivory">{formatTimestamp(tx.timestamp)}</dd>
              </div>
              <div>
                <dt className="text-[11px] text-mute">Origin balance before → after</dt>
                <dd className="data-num mt-0.5 text-sm text-ivory">
                  {formatCurrency(tx.origin_balance_before)} → {formatCurrency(tx.origin_balance_after)}
                </dd>
              </div>
              <div>
                <dt className="text-[11px] text-mute">Destination balance before → after</dt>
                <dd className="data-num mt-0.5 text-sm text-ivory">
                  {formatCurrency(tx.destination_balance_before)} → {formatCurrency(tx.destination_balance_after)}
                </dd>
              </div>
            </dl>
          </div>

          {/* Risk signals */}
          <div>
            <p className="label-eyebrow mb-3 flex items-center gap-2">
              <Radar className="h-3.5 w-3.5" aria-hidden="true" /> Risk signals
            </p>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <SignalCard
                title="Model 1"
                context="PaySim"
                score={tx.model_1?.fraud_probability ?? 0}
                weight={0.8}
                description="Random Forest — calibrated supervised fraud probability."
                inactive={!tx.model_1}
              />
              <SignalCard
                title="Rule Engine"
                context="PaySim"
                score={tx.rules?.behavioral_risk ?? 0}
                weight={0.1}
                description="Six behavioral rules — calibrated rule-based risk."
                inactive={!tx.rules}
              />
              <SignalCard
                title="Model 2"
                context="ULB"
                score={tx.model_2?.anomaly_score ?? 0}
                weight={0.1}
                description="Isolation Forest — calibrated anomaly score. Active only in the ULB context."
                inactive={!tx.model_2}
              />
            </div>
          </div>

          {/* Why flagged */}
          <div className="panel p-5">
            <p className="label-eyebrow mb-3 flex items-center gap-2">
              <ShieldAlert className="h-3.5 w-3.5" aria-hidden="true" /> Why CORTANA flagged this transaction
            </p>
            {rules.length === 0 ? (
              <p className="text-sm text-mute">
                {tx.dataset_context === "ULB"
                  ? "The behavioral rule engine does not evaluate ULB transactions — this context is scored by Model 2 alone."
                  : "No behavioral rules triggered for this transaction."}
              </p>
            ) : (
              <ul className="space-y-3">
                {rules.map((r) => (
                  <li key={r.rule_key} className="flex items-start gap-3 rounded-md border border-hairline-soft px-4 py-3">
                    <ListChecks className="mt-0.5 h-4 w-4 shrink-0 text-amber" aria-hidden="true" />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs uppercase tracking-wider text-ivory">
                          {RULE_LABEL[r.rule_key] ?? r.rule_key}
                        </span>
                        <RiskBadge level={r.severity} size="sm" />
                      </div>
                      <p className="mt-1 text-xs text-mute">{r.description}</p>
                      {r.field && (
                        <p className="mt-1 font-mono text-[11px] text-mute">
                          {r.field}: <span className="text-ivory-dim">{r.value}</span>
                        </p>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <AIExplanation transaction={tx} />
        </div>

        {/* Right: fusion */}
        <div className="space-y-6">
          <div className="panel flex flex-col items-center gap-4 p-6">
            <p className="label-eyebrow">Cortana fusion</p>
            <RiskScore score={tx.fusion.fused_risk} level={tx.fusion.risk_level} size={148} />
            <div className="flex items-center gap-2">
              <RiskBadge level={tx.fusion.risk_level} />
              <DecisionPill decision={tx.fusion.decision} />
            </div>
            <p className="text-center text-[11px] leading-relaxed text-mute">
              Decision threshold {pct(tx.fusion.threshold, 0)} — fused risk{" "}
              {tx.fusion.fused_risk >= tx.fusion.threshold ? "meets or exceeds" : "is below"} the threshold.
            </p>
          </div>

          <Link
            to={`/app/investigations`}
            className="block panel p-5 text-center text-sm text-ivory hover:border-intel/50"
          >
            Open an investigation case for this transaction →
          </Link>
        </div>
      </div>
    </div>
  );
}
