import { Link } from "react-router-dom";
import type { Transaction } from "../types";
import RiskBadge from "./RiskBadge";
import DecisionPill from "./DecisionPill";
import { formatCurrency, formatTimestamp, pct } from "../utils/risk";

export default function TransactionCard({ tx }: { tx: Transaction }) {
  return (
    <Link
      to={`/app/transactions/${tx.id}`}
      className="panel flex flex-col gap-3 p-4 transition-colors hover:border-intel/50"
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="data-num text-sm text-ivory">{tx.id}</p>
          <p className="mt-0.5 text-[11px] text-mute">
            {tx.dataset_context} · {tx.type}
          </p>
        </div>
        <RiskBadge level={tx.fusion.risk_level} size="sm" />
      </div>

      <div className="flex items-end justify-between">
        <span className="data-num text-lg font-medium text-ivory">
          {formatCurrency(tx.amount, tx.currency)}
        </span>
        <span className="data-num text-xs text-mute">{pct(tx.fusion.fused_risk)}</span>
      </div>

      <div className="flex items-center justify-between border-t border-hairline-soft pt-3">
        <span className="text-[11px] text-mute">{formatTimestamp(tx.timestamp)}</span>
        <DecisionPill decision={tx.fusion.decision} />
      </div>
    </Link>
  );
}
