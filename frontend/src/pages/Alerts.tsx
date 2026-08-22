import { useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";
import AlertTable from "../alerts/AlertTable";
import { MOCK_ALERTS } from "../data/mock/alerts";
import type { RiskLevel, Decision } from "../types";

const LEVELS: (RiskLevel | "ALL")[] = ["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"];
const DECISIONS: (Decision | "ALL")[] = ["ALL", "PASS", "REVIEW"];

export default function Alerts() {
  const [level, setLevel] = useState<RiskLevel | "ALL">("ALL");
  const [decision, setDecision] = useState<Decision | "ALL">("ALL");

  const filtered = useMemo(
    () =>
      MOCK_ALERTS.filter(
        (a) => (level === "ALL" || a.risk_level === level) && (decision === "ALL" || a.decision === decision)
      ),
    [level, decision]
  );

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
          <span className="ml-auto self-center text-xs text-mute">{filtered.length} alerts</span>
        </div>

        <AlertTable alerts={filtered} />
      </div>
    </div>
  );
}
