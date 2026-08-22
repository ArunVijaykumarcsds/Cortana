import PageHeader from "../components/PageHeader";
import FusionVisualization from "../components/FusionVisualization";
import {
  MODEL_1,
  MODEL_2,
  RULES,
  FUSION_FINAL_TEST,
  MODEL_COMPARISON,
  VALIDATION_STEPS,
  RELEASE,
  DECISION_THRESHOLD,
} from "../data/cortanaConfig";
import { pct } from "../utils/risk";

export default function ModelIntelligence() {
  return (
    <div>
      <PageHeader
        eyebrow="Model Intelligence"
        title="How CORTANA thinks"
        description={`${RELEASE.releaseName} · ${RELEASE.phase} · figures below are read directly from the release evaluation artifacts.`}
      />

      <div className="space-y-8 px-5 py-6 md:px-8">
        {/* Fusion diagram */}
        <div className="panel p-6">
          <p className="label-eyebrow mb-6">Fusion architecture</p>
          <FusionVisualization />
        </div>

        {/* Component cards */}
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="panel p-5">
            <p className="label-eyebrow">Model 1</p>
            <h3 className="mt-1 font-display text-lg text-ivory">{MODEL_1.algorithm}</h3>
            <p className="mt-1 text-xs text-mute">{MODEL_1.dataset} · {MODEL_1.learningType}</p>
            <dl className="mt-4 space-y-2 text-xs">
              <div className="flex justify-between"><dt className="text-mute">Purpose</dt><dd className="text-ivory-dim text-right">{MODEL_1.purpose}</dd></div>
              <div className="flex justify-between"><dt className="text-mute">Fusion weight</dt><dd className="data-num text-ivory">{pct(MODEL_1.weight, 0)}</dd></div>
              <div className="flex justify-between"><dt className="text-mute">Validation rows</dt><dd className="data-num text-ivory">{MODEL_1.validationRows.toLocaleString()}</dd></div>
              <div className="flex justify-between"><dt className="text-mute">Test rows</dt><dd className="data-num text-ivory">{MODEL_1.testRows.toLocaleString()}</dd></div>
            </dl>
          </div>

          <div className="panel p-5">
            <p className="label-eyebrow">Rule Engine</p>
            <h3 className="mt-1 font-display text-lg text-ivory">6 behavioral rules</h3>
            <p className="mt-1 text-xs text-mute">PaySim · deterministic</p>
            <ul className="mt-4 space-y-2">
              {RULES.map((r) => (
                <li key={r.rule_key} className="flex items-center justify-between text-xs">
                  <span className="text-ivory-dim">{r.rule_key.replaceAll("_", " ").toLowerCase()}</span>
                  <span className="data-num text-mute">{pct(r.weight, 0)}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="panel p-5">
            <p className="label-eyebrow">Model 2</p>
            <h3 className="mt-1 font-display text-lg text-ivory">{MODEL_2.algorithm}</h3>
            <p className="mt-1 text-xs text-mute">{MODEL_2.dataset} · {MODEL_2.learningType}</p>
            <dl className="mt-4 space-y-2 text-xs">
              <div className="flex justify-between"><dt className="text-mute">n_estimators</dt><dd className="data-num text-ivory">{MODEL_2.nEstimators}</dd></div>
              <div className="flex justify-between"><dt className="text-mute">Operating policy</dt><dd className="text-ivory-dim">rank-based, top {pct(MODEL_2.operatingPolicy.anomalyPercentage, 1)}</dd></div>
              <div className="flex justify-between"><dt className="text-mute">Fusion weight</dt><dd className="data-num text-ivory">{pct(MODEL_2.weight, 0)}</dd></div>
              <div className="flex justify-between"><dt className="text-mute">Training rows</dt><dd className="data-num text-ivory">{MODEL_2.trainingDataset.trainingRows.toLocaleString()}</dd></div>
            </dl>
          </div>
        </div>

        {/* Decision policy */}
        <div className="panel p-5">
          <p className="label-eyebrow">Decision policy</p>
          <p className="mt-2 text-sm text-ivory-dim">
            Fused risk ≥ <span className="data-num text-ivory">{DECISION_THRESHOLD}</span> → <span className="text-(--color-critical)">REVIEW</span>. Below threshold → <span className="text-(--color-low)">PASS</span>.
          </p>
          <p className="mt-2 text-xs text-mute">
            The threshold was selected using validation data and remained locked during final test evaluation — no test-set threshold optimization was performed.
          </p>
        </div>

        {/* Model comparison table */}
        <div className="panel overflow-hidden">
          <p className="label-eyebrow px-5 pt-5">Final untouched PaySim test — model comparison</p>
          <div className="overflow-x-auto">
            <table className="mt-3 w-full text-left text-sm">
              <thead>
                <tr className="border-y border-hairline bg-surface-2 text-mute">
                  <th className="label-eyebrow px-5 py-2 font-normal">System</th>
                  <th className="label-eyebrow px-5 py-2 font-normal">Precision</th>
                  <th className="label-eyebrow px-5 py-2 font-normal">Recall</th>
                  <th className="label-eyebrow px-5 py-2 font-normal">F1</th>
                  <th className="label-eyebrow px-5 py-2 font-normal">ROC-AUC</th>
                  <th className="label-eyebrow px-5 py-2 font-normal">PR-AUC</th>
                </tr>
              </thead>
              <tbody>
                {MODEL_COMPARISON.map((m) => (
                  <tr key={m.system} className="border-b border-hairline-soft last:border-0">
                    <td className="px-5 py-3 text-ivory">{m.system}</td>
                    <td className="px-5 py-3 data-num text-ivory-dim">{pct(m.precision)}</td>
                    <td className="px-5 py-3 data-num text-ivory-dim">{pct(m.recall)}</td>
                    <td className="px-5 py-3 data-num text-ivory-dim">{pct(m.f1)}</td>
                    <td className="px-5 py-3 data-num text-ivory-dim">{pct(m.rocAuc)}</td>
                    <td className="px-5 py-3 data-num text-ivory-dim">{pct(m.prAuc)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="px-5 pb-5 pt-3 text-xs text-mute">
            Confusion matrix — CORTANA Fusion: TP {FUSION_FINAL_TEST.truePositives}, FP {FUSION_FINAL_TEST.falsePositives}, TN {FUSION_FINAL_TEST.trueNegatives.toLocaleString()}, FN {FUSION_FINAL_TEST.falseNegatives}. Fraud detection rate {pct(FUSION_FINAL_TEST.fraudDetectionRate)} ({FUSION_FINAL_TEST.fraudDetected} of {FUSION_FINAL_TEST.knownFraud} known fraud cases).
          </p>
        </div>

        {/* Validation steps */}
        <div className="panel p-5">
          <p className="label-eyebrow mb-4">Release validation — Phase 6</p>
          <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {VALIDATION_STEPS.map((s) => (
              <li key={s.step} className="flex items-center justify-between rounded-md border border-hairline-soft px-3 py-2 text-xs">
                <span className="text-ivory-dim">{s.step}</span>
                <span className="text-(--color-low)">{s.status}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
