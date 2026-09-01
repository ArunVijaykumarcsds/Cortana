import { useEffect, useState } from "react";
import { Sparkles, RefreshCw, ShieldCheck, Cpu } from "lucide-react";
import { fetchTransactionExplanation } from "../data/api";
import type { ExplanationResponse, Transaction } from "../types";

export default function AIExplanation({ transaction }: { transaction: Transaction }) {
  const [explanation, setExplanation] = useState<ExplanationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadExplanation() {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchTransactionExplanation(transaction.id);
      setExplanation(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load risk explanation";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadExplanation();
  }, [transaction.id]);

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-amber" aria-hidden="true" />
          <h3 className="font-mono text-xs uppercase tracking-wider text-ivory-dim">
            Cortana AI Explanation
          </h3>
        </div>
        <div className="flex items-center gap-2">
          {explanation && (
            <span className="flex items-center gap-1 rounded-[3px] border border-hairline px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-mute">
              {explanation.is_fallback ? (
                <>
                  <ShieldCheck className="h-3 w-3 text-emerald-400" />
                  Deterministic Engine
                </>
              ) : (
                <>
                  <Cpu className="h-3 w-3 text-intel" />
                  {explanation.provider.toUpperCase()}
                </>
              )}
            </span>
          )}
          <button
            type="button"
            onClick={loadExplanation}
            disabled={loading}
            title="Refresh explanation"
            className="rounded p-1 text-mute transition-colors hover:text-ivory disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {error ? (
        <div className="mt-3 rounded border border-ruby/30 bg-ruby/5 p-3 text-xs text-ruby">
          <p>Failed to generate explanation: {error}</p>
          <button
            type="button"
            onClick={loadExplanation}
            className="mt-2 text-intel underline hover:text-ivory"
          >
            Retry
          </button>
        </div>
      ) : loading ? (
        <div className="mt-4 flex min-h-[80px] items-center justify-center">
          <span className="label-eyebrow animate-pulse">Analyzing Risk Signals…</span>
        </div>
      ) : explanation ? (
        <div className="mt-3 space-y-3">
          <p className="text-xs leading-relaxed text-ivory-dim">
            {explanation.explanation_text}
          </p>

          {explanation.referenced_signals && explanation.referenced_signals.length > 0 && (
            <div className="border-t border-hairline-soft pt-3">
              <p className="label-eyebrow mb-1.5 text-[10px]">Referenced Signals</p>
              <div className="flex flex-wrap gap-1.5">
                {explanation.referenced_signals.map((sig) => (
                  <span
                    key={sig}
                    className="rounded bg-surface-2 px-2 py-0.5 font-mono text-[10px] text-mute"
                  >
                    {sig}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
