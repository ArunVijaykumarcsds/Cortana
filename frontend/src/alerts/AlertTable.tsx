import { Link } from "react-router-dom";
import type { Alert } from "../types";
import RiskBadge from "../components/RiskBadge";
import DecisionPill from "../components/DecisionPill";
import { formatTimestamp, pct } from "../utils/risk";

const STATUS_LABEL: Record<Alert["status"], string> = {
  OPEN: "Open",
  UNDER_REVIEW: "Under review",
  RESOLVED: "Resolved",
};

export default function AlertTable({ alerts }: { alerts: Alert[] }) {
  if (alerts.length === 0) {
    return (
      <div className="panel p-10 text-center">
        <p className="text-sm text-mute">No alerts match these filters.</p>
      </div>
    );
  }

  return (
    <>
      {/* Desktop table */}
      <div className="hidden overflow-hidden rounded-md border border-hairline md:block">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-hairline bg-surface-2 text-mute">
              <th className="label-eyebrow px-4 py-3 font-normal">Transaction</th>
              <th className="label-eyebrow px-4 py-3 font-normal">Type</th>
              <th className="label-eyebrow px-4 py-3 font-normal">Risk score</th>
              <th className="label-eyebrow px-4 py-3 font-normal">Level</th>
              <th className="label-eyebrow px-4 py-3 font-normal">Decision</th>
              <th className="label-eyebrow px-4 py-3 font-normal">Status</th>
              <th className="label-eyebrow px-4 py-3 font-normal">Flagged</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a) => (
              <tr key={a.id} className="border-b border-hairline-soft last:border-0 hover:bg-surface-2/50">
                <td className="px-4 py-3">
                  <Link to={`/app/transactions/${a.transaction_id}`} className="data-num text-intel hover:underline">
                    {a.transaction_id}
                  </Link>
                  <p className="text-[11px] text-mute">{a.dataset_context}</p>
                </td>
                <td className="px-4 py-3 text-xs text-ivory-dim">{a.type}</td>
                <td className="px-4 py-3 data-num text-ivory">{pct(a.risk_score)}</td>
                <td className="px-4 py-3">
                  <RiskBadge level={a.risk_level} size="sm" />
                </td>
                <td className="px-4 py-3">
                  <DecisionPill decision={a.decision} />
                </td>
                <td className="px-4 py-3 text-xs text-mute">{STATUS_LABEL[a.status]}</td>
                <td className="px-4 py-3 text-xs text-mute">{formatTimestamp(a.timestamp)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <div className="flex flex-col gap-3 md:hidden">
        {alerts.map((a) => (
          <Link
            key={a.id}
            to={`/app/transactions/${a.transaction_id}`}
            className="panel flex flex-col gap-3 p-4"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="data-num text-sm text-ivory">{a.transaction_id}</p>
                <p className="text-[11px] text-mute">
                  {a.dataset_context} · {a.type}
                </p>
              </div>
              <RiskBadge level={a.risk_level} size="sm" />
            </div>
            <div className="flex items-center justify-between border-t border-hairline-soft pt-3">
              <span className="data-num text-sm text-ivory">{pct(a.risk_score)}</span>
              <DecisionPill decision={a.decision} />
            </div>
            <div className="flex items-center justify-between text-[11px] text-mute">
              <span>{STATUS_LABEL[a.status]}</span>
              <span>{formatTimestamp(a.timestamp)}</span>
            </div>
          </Link>
        ))}
      </div>
    </>
  );
}
