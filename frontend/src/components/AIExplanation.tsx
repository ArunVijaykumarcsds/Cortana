import { Sparkles } from "lucide-react";
import type { Transaction } from "../types";

const SUGGESTED = [
  "Why is this transaction suspicious?",
  "Which signals contributed most to the risk?",
  "What should an analyst investigate first?",
];

export default function AIExplanation({ transaction }: { transaction: Transaction }) {
  return (
    <div className="panel p-5">
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-amber" aria-hidden="true" />
        <h3 className="font-mono text-xs uppercase tracking-wider text-ivory-dim">
          Cortana Intelligence
        </h3>
        <span className="ml-auto rounded-[3px] border border-hairline px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-mute">
          Coming soon
        </span>
      </div>

      <p className="mt-3 text-xs leading-relaxed text-mute">
        This panel will host a natural-language explanation layer once the LLM
        service is connected. It will describe the deterministic risk factors
        already computed for {transaction.id} in plain language — it will not
        change the risk score or the decision. Fusion, fraud probability, and
        rule outcomes stay fully owned by the existing ML/rules system.
      </p>

      <div className="mt-4 space-y-2">
        {SUGGESTED.map((q) => (
          <button
            key={q}
            type="button"
            disabled
            className="w-full cursor-not-allowed rounded-md border border-hairline-soft bg-surface-2 px-3 py-2 text-left text-xs text-mute"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
