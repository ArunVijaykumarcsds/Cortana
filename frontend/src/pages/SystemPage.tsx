import PageHeader from "../components/PageHeader";
import SystemStatusIndicator from "../components/SystemStatusIndicator";
import { MOCK_SYSTEM_STATUS, DEPLOYMENT } from "../data/mock/systemStatus";
import { RELEASE, DECISION_THRESHOLD, FUSION_WEIGHTS } from "../data/cortanaConfig";

export default function SystemPage() {
  return (
    <div>
      <PageHeader
        eyebrow="System"
        title="System status"
        description="Operational state of every CORTANA component, including services planned for the integration phase."
      />

      <div className="space-y-6 px-5 py-6 md:px-8">
        <div className="panel overflow-hidden">
          {MOCK_SYSTEM_STATUS.map((s, i) => (
            <div
              key={s.service}
              className={`flex items-center justify-between px-5 py-4 ${
                i !== MOCK_SYSTEM_STATUS.length - 1 ? "border-b border-hairline-soft" : ""
              }`}
            >
              <div>
                <p className="text-sm text-ivory">{s.service}</p>
                <p className="mt-0.5 text-[11px] text-mute">{s.detail}</p>
              </div>
              <SystemStatusIndicator state={s.state} />
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="panel p-5">
            <p className="label-eyebrow">Model version</p>
            <p className="mt-1 text-sm text-ivory">{DEPLOYMENT.modelVersion}</p>
          </div>
          <div className="panel p-5">
            <p className="label-eyebrow">Deployment phase</p>
            <p className="mt-1 text-sm text-ivory">{DEPLOYMENT.releasePhase}</p>
          </div>
          <div className="panel p-5">
            <p className="label-eyebrow">Package status</p>
            <p className="mt-1 text-sm text-ivory">{DEPLOYMENT.packageStatus}</p>
          </div>
        </div>

        <div className="panel p-5">
          <p className="label-eyebrow">Locked production policy</p>
          <p className="mt-2 text-xs leading-relaxed text-mute">
            Fusion weights — Model 1 {FUSION_WEIGHTS.model_1}, Model 2 {FUSION_WEIGHTS.model_2}, Rules{" "}
            {FUSION_WEIGHTS.rules}. Decision threshold {DECISION_THRESHOLD}. This policy is set by the ML core in{" "}
            <span className="font-mono text-ivory-dim">{RELEASE.releaseName}</span> and is not modified by the frontend.
          </p>
        </div>
      </div>
    </div>
  );
}
