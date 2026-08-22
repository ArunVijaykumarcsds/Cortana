import type { ReactNode } from "react";
import { pct } from "../utils/risk";

interface SignalCardProps {
  title: string;
  context: string;
  score: number;
  weight: number;
  description: string;
  icon?: ReactNode;
  inactive?: boolean;
}

export default function SignalCard({ title, context, score, weight, description, icon, inactive }: SignalCardProps) {
  return (
    <div className={`panel p-5 ${inactive ? "opacity-40" : ""}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {icon && <span className="text-intel" aria-hidden="true">{icon}</span>}
          <h3 className="font-mono text-xs uppercase tracking-wider text-ivory-dim">{title}</h3>
        </div>
        <span className="label-eyebrow">{context}</span>
      </div>

      {inactive ? (
        <p className="mt-4 text-sm text-mute">Not active for this transaction's dataset context.</p>
      ) : (
        <>
          <div className="mt-4 flex items-end justify-between">
            <span className="data-num text-3xl font-medium text-ivory">{pct(score)}</span>
            <span className="label-eyebrow">weight {pct(weight, 0)}</span>
          </div>
          <div className="mt-3 h-1 w-full overflow-hidden rounded-full bg-surface-3">
            <div
              className="h-full rounded-full bg-intel"
              style={{ width: `${Math.min(100, score * 100)}%` }}
            />
          </div>
        </>
      )}
      <p className="mt-3 text-xs leading-relaxed text-mute">{description}</p>
    </div>
  );
}
