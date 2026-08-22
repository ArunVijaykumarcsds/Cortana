import { RISK_COLOR_VAR, RISK_LABEL } from "../utils/risk";
import type { RiskLevel } from "../types";
import CortanaMark from "../components/CortanaMark";

export function ObserveVisual() {
  return (
    <div className="panel flex flex-col gap-3 p-6">
      <div className="flex items-center justify-between">
        <span className="label-eyebrow">Incoming transaction</span>
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-intel" aria-hidden="true" />
      </div>
      <div className="flex items-center justify-between rounded-md border border-hairline-soft bg-surface-2 px-4 py-3">
        <span className="data-num text-sm text-ivory">PSX-118422</span>
        <span className="data-num text-sm text-mute">$412,800.00</span>
      </div>
      <div className="flex items-center gap-2 text-[11px] text-mute">
        <span className="font-mono">CASH_OUT</span>
        <span>·</span>
        <span>PaySim context</span>
      </div>
    </div>
  );
}

export function DetectVisual() {
  return (
    <div className="panel p-6">
      <span className="label-eyebrow">Model 1 — Random Forest</span>
      <div className="mt-4 flex items-baseline gap-2">
        <span className="data-num text-4xl font-medium text-ivory">98.7</span>
        <span className="text-sm text-mute">% fraud probability</span>
      </div>
      <div className="mt-4 h-1.5 w-full rounded-full bg-surface-3">
        <div className="h-full rounded-full bg-intel" style={{ width: "98.7%" }} />
      </div>
      <p className="mt-4 text-xs leading-relaxed text-mute">
        Supervised on PaySim, calibrated to a probability CORTANA can weigh
        against the other signals.
      </p>
    </div>
  );
}

export function ChallengeVisual() {
  const rules = [
    { key: "HIGH_AMOUNT", hit: true },
    { key: "ORIGIN_BALANCE_INCONSISTENCY", hit: true },
    { key: "LARGE_BALANCE_CHANGE", hit: true },
    { key: "HIGH_RISK_TRANSACTION_TYPE", hit: true },
    { key: "DESTINATION_BALANCE_INCONSISTENCY", hit: false },
    { key: "ZERO_BALANCE_ANOMALY", hit: false },
  ];
  return (
    <div className="panel p-6">
      <span className="label-eyebrow">Rule engine — 6 behavioral rules</span>
      <ul className="mt-4 space-y-2">
        {rules.map((r) => (
          <li key={r.key} className="flex items-center justify-between rounded-md border border-hairline-soft px-3 py-2">
            <span className="font-mono text-[11px] text-ivory-dim">{r.key.replaceAll("_", " ").toLowerCase()}</span>
            <span
              className={`h-1.5 w-1.5 rounded-full ${r.hit ? "bg-amber" : "bg-mute-2"}`}
              aria-hidden="true"
            />
          </li>
        ))}
      </ul>
    </div>
  );
}

export function InvestigateVisual() {
  return (
    <div className="panel p-6">
      <span className="label-eyebrow">Model 2 — Isolation Forest · ULB</span>
      <div className="mt-4 flex items-baseline gap-2">
        <span className="data-num text-4xl font-medium text-ivory">91.2</span>
        <span className="text-sm text-mute">% anomaly score</span>
      </div>
      <div className="mt-4 rounded-md border border-dashed border-hairline px-4 py-3 text-[11px] leading-relaxed text-mute">
        Evaluated independently, on its own transaction stream. Never
        row-paired with a PaySim transaction like the one above.
      </div>
    </div>
  );
}

export function FuseVisual() {
  return (
    <div className="panel flex flex-col items-center gap-4 p-6">
      <CortanaMark variant="compact" className="h-28 w-28" animate />
      <div className="grid w-full grid-cols-3 gap-2 text-center">
        <div>
          <p className="data-num text-sm text-ivory">0.80</p>
          <p className="text-[10px] text-mute">Model 1</p>
        </div>
        <div>
          <p className="data-num text-sm text-ivory">0.10</p>
          <p className="text-[10px] text-mute">Rules</p>
        </div>
        <div>
          <p className="data-num text-sm text-ivory">0.10</p>
          <p className="text-[10px] text-mute">Model 2</p>
        </div>
      </div>
    </div>
  );
}

export function CalculateVisual() {
  const levels: RiskLevel[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
  return (
    <div className="panel p-6">
      <span className="label-eyebrow">Risk levels</span>
      <div className="mt-4 flex flex-col gap-2">
        {levels.map((l) => (
          <div key={l} className="flex items-center gap-3">
            <span className="w-20 shrink-0 font-mono text-[11px] uppercase tracking-wider text-mute">{RISK_LABEL[l]}</span>
            <div className="h-2 flex-1 rounded-full bg-surface-3">
              <div
                className="h-full rounded-full"
                style={{
                  width: l === "LOW" ? "25%" : l === "MEDIUM" ? "50%" : l === "HIGH" ? "75%" : "100%",
                  background: RISK_COLOR_VAR[l],
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ExplainVisual() {
  return (
    <div className="panel p-6">
      <span className="label-eyebrow">Why this was flagged</span>
      <ul className="mt-4 space-y-3 text-xs text-mute">
        <li className="border-l-2 border-amber pl-3">
          <span className="text-ivory-dim">HIGH_AMOUNT</span> — exceeds the configured behavioral threshold.
        </li>
        <li className="border-l-2 border-amber pl-3">
          <span className="text-ivory-dim">ORIGIN_BALANCE_INCONSISTENCY</span> — balance movement inconsistent with expected behavior.
        </li>
      </ul>
      <p className="mt-4 border-t border-hairline-soft pt-3 text-[11px] leading-relaxed text-mute">
        The deterministic signals are the explanation. A future language
        layer will narrate them — it will never decide the score.
      </p>
    </div>
  );
}

export function DecideVisual() {
  return (
    <div className="panel p-6">
      <span className="label-eyebrow">Case C-10291</span>
      <div className="mt-3 flex items-center gap-2">
        <span className="rounded-full border border-(--color-critical)/40 px-2.5 py-1 font-mono text-[10px] uppercase tracking-wider text-(--color-critical)">
          Critical
        </span>
        <span className="text-xs text-mute">Score 0.986</span>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2">
        <div className="rounded-md border border-hairline-soft px-3 py-2 text-center text-[11px] text-ivory-dim">
          Confirm fraud
        </div>
        <div className="rounded-md border border-hairline-soft px-3 py-2 text-center text-[11px] text-ivory-dim">
          Mark legitimate
        </div>
      </div>
      <p className="mt-4 text-[11px] leading-relaxed text-mute">
        CORTANA detects. The analyst decides — every action is written to an
        audit trail.
      </p>
    </div>
  );
}
