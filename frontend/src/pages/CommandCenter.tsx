import { Link } from "react-router-dom";
import PageHeader from "../components/PageHeader";
import MetricCard from "../components/MetricCard";
import RiskBadge from "../components/RiskBadge";
import DecisionPill from "../components/DecisionPill";
import RiskDistributionChart from "../dashboard/RiskDistributionChart";
import DecisionTrendChart from "../dashboard/DecisionTrendChart";
import { MOCK_TRANSACTIONS } from "../data/mock/generator";
import { MOCK_ALERTS } from "../data/mock/alerts";
import { FUSION_FINAL_TEST } from "../data/cortanaConfig";
import { formatCompactCurrency, formatTimestamp, pct } from "../utils/risk";

export default function CommandCenter() {
  const total = MOCK_TRANSACTIONS.length;
  const critical = MOCK_TRANSACTIONS.filter((t) => t.fusion.risk_level === "CRITICAL").length;
  const highRisk = MOCK_TRANSACTIONS.filter(
    (t) => t.fusion.risk_level === "HIGH" || t.fusion.risk_level === "CRITICAL"
  ).length;
  const reviewQueue = MOCK_ALERTS.filter((a) => a.status !== "RESOLVED").length;
  const volume = MOCK_TRANSACTIONS.reduce((s, t) => s + t.amount, 0);

  const attention = [...MOCK_TRANSACTIONS]
    .sort((a, b) => b.fusion.fused_risk - a.fusion.fused_risk)
    .slice(0, 6);

  return (
    <div>
      <PageHeader
        eyebrow="Command Center"
        title="What needs attention"
        description="A live view of transaction volume, risk distribution, and the review queue — mock data until the API layer is connected."
      />

      <div className="px-5 py-6 md:px-8">
        {/* Sample-data notice */}
        <div className="mb-6 rounded-md border border-hairline-soft bg-surface-2/40 px-4 py-2.5 text-xs text-mute">
          Figures below are generated from the frontend's mock-data layer for
          demonstration. Model performance figures on the{" "}
          <Link to="/app/model-intelligence" className="text-intel hover:underline">
            Model Intelligence
          </Link>{" "}
          page are the real evaluation results from the release package.
        </div>

        <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
          <MetricCard label="Transactions processed" value={total.toLocaleString()} sublabel="Rolling 72h window" />
          <MetricCard label="Total volume" value={formatCompactCurrency(volume)} sublabel="All monitored transactions" />
          <MetricCard label="High risk" value={highRisk.toLocaleString()} deltaTone="up" delta={pct(highRisk / total)} />
          <MetricCard label="Critical" value={critical.toLocaleString()} deltaTone="up" delta={pct(critical / total)} />
          <MetricCard label="Review queue" value={reviewQueue.toLocaleString()} sublabel="Open + under review" />
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <RiskDistributionChart transactions={MOCK_TRANSACTIONS} />
          <DecisionTrendChart transactions={MOCK_TRANSACTIONS} />
        </div>

        <div className="mt-6 panel">
          <div className="flex items-center justify-between border-b border-hairline px-5 py-4">
            <h2 className="font-mono text-xs uppercase tracking-wider text-ivory-dim">
              Needs attention now
            </h2>
            <Link to="/app/alerts" className="text-xs text-intel hover:underline">
              View all alerts
            </Link>
          </div>
          <ul>
            {attention.map((t) => (
              <li key={t.id} className="border-b border-hairline-soft last:border-0">
                <Link
                  to={`/app/transactions/${t.id}`}
                  className="flex items-center justify-between gap-3 px-5 py-3 hover:bg-surface-2/50"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <RiskBadge level={t.fusion.risk_level} size="sm" />
                    <span className="data-num truncate text-sm text-ivory">{t.id}</span>
                    <span className="hidden text-xs text-mute sm:inline">{t.dataset_context}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="data-num hidden text-xs text-mute sm:inline">
                      {formatTimestamp(t.timestamp)}
                    </span>
                    <DecisionPill decision={t.fusion.decision} />
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-6 panel p-5">
          <p className="label-eyebrow">Fraud detection performance — final test evaluation</p>
          <div className="mt-3 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div>
              <p className="data-num text-xl text-ivory">{pct(FUSION_FINAL_TEST.recall)}</p>
              <p className="text-[11px] text-mute">Recall</p>
            </div>
            <div>
              <p className="data-num text-xl text-ivory">{pct(FUSION_FINAL_TEST.precision)}</p>
              <p className="text-[11px] text-mute">Precision</p>
            </div>
            <div>
              <p className="data-num text-xl text-ivory">{pct(FUSION_FINAL_TEST.rocAuc)}</p>
              <p className="text-[11px] text-mute">ROC-AUC</p>
            </div>
            <div>
              <p className="data-num text-xl text-ivory">
                {FUSION_FINAL_TEST.fraudDetected}/{FUSION_FINAL_TEST.knownFraud}
              </p>
              <p className="text-[11px] text-mute">Fraud caught</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
