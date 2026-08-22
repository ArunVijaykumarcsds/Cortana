import { Link } from "react-router-dom";
import PageHeader from "../components/PageHeader";
import RiskBadge from "../components/RiskBadge";
import { MOCK_INVESTIGATIONS } from "../data/mock/investigations";
import { formatTimestamp, pct } from "../utils/risk";

const STATUS_TONE: Record<string, string> = {
  OPEN: "text-ivory-dim",
  IN_REVIEW: "text-intel",
  ESCALATED: "text-(--color-high)",
  CLOSED: "text-mute",
};

export default function Investigations() {
  return (
    <div>
      <PageHeader
        eyebrow="Investigations"
        title="Case files"
        description="CORTANA detects. The analyst decides. Every case keeps a full audit trail of what happened and when."
      />

      <div className="grid grid-cols-1 gap-3 px-5 py-6 sm:grid-cols-2 md:px-8 lg:grid-cols-3">
        {MOCK_INVESTIGATIONS.map((c) => (
          <Link key={c.id} to={`/app/investigations/${c.id}`} className="panel flex flex-col gap-3 p-5 hover:border-intel/50">
            <div className="flex items-start justify-between">
              <span className="data-num text-sm text-ivory">{c.id}</span>
              <RiskBadge level={c.risk_level} size="sm" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="data-num text-2xl font-medium text-ivory">{pct(c.risk_score)}</span>
              <span className={`font-mono text-[10px] uppercase tracking-wider ${STATUS_TONE[c.status]}`}>
                {c.status.replace("_", " ")}
              </span>
            </div>
            <div className="flex items-center justify-between border-t border-hairline-soft pt-3 text-[11px] text-mute">
              <span>{c.assigned_to}</span>
              <span>{formatTimestamp(c.opened_at)}</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
