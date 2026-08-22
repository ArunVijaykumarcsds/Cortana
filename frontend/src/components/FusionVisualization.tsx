import { pct } from "../utils/risk";

interface NodeProps {
  title: string;
  dataset: string;
  weight?: number;
  detail: string;
}

function Node({ title, dataset, weight, detail }: NodeProps) {
  return (
    <div className="panel flex flex-col gap-1 px-4 py-3">
      <div className="flex items-center justify-between gap-3">
        <span className="font-mono text-[11px] uppercase tracking-wider text-ivory-dim">{title}</span>
        {weight !== undefined && (
          <span className="data-num text-xs text-intel">{pct(weight, 0)}</span>
        )}
      </div>
      <span className="label-eyebrow">{dataset}</span>
      <p className="mt-1 text-[11px] leading-snug text-mute">{detail}</p>
    </div>
  );
}

export default function FusionVisualization() {
  return (
    <div className="w-full">
      <div className="grid grid-cols-1 gap-8 md:grid-cols-[1fr_auto_1fr]">
        {/* PaySim branch */}
        <div className="flex flex-col gap-3">
          <p className="label-eyebrow text-center md:text-left">PaySim context</p>
          <Node title="Model 1" dataset="Random Forest · supervised" weight={0.8} detail="Calibrated fraud probability" />
          <Node title="Rule Engine" dataset="6 behavioral rules" weight={0.1} detail="Calibrated behavioral risk" />
        </div>

        {/* connector */}
        <div className="flex flex-col items-center justify-center gap-2 py-2 md:py-0">
          <div className="h-8 w-px bg-hairline md:hidden" />
          <div className="hidden h-full w-px bg-gradient-to-b from-transparent via-hairline to-transparent md:block" />
        </div>

        {/* ULB branch */}
        <div className="flex flex-col gap-3">
          <p className="label-eyebrow text-center md:text-left">ULB context — independent</p>
          <Node title="Model 2" dataset="Isolation Forest · unsupervised" weight={0.1} detail="Calibrated anomaly score" />
          <div className="rounded-md border border-dashed border-hairline px-4 py-3 text-[11px] leading-snug text-mute">
            Never row-paired with PaySim transactions. Evaluated independently
            on its own transaction stream.
          </div>
        </div>
      </div>

      <div className="my-8 flex flex-col items-center gap-2">
        <div className="h-10 w-px bg-hairline" aria-hidden="true" />
        <div className="panel flex items-center gap-3 px-6 py-3">
          <span className="font-display text-xl tracking-wide text-ivory">CORTANA</span>
          <span className="label-eyebrow">fusion engine</span>
        </div>
        <div className="h-10 w-px bg-hairline" aria-hidden="true" />
        <div className="rounded-full border border-intel/40 bg-intel/10 px-5 py-2 font-mono text-xs uppercase tracking-wider text-intel">
          Fused Risk Score
        </div>
      </div>

      <p className="mx-auto max-w-lg text-center text-xs leading-relaxed text-mute">
        For a PaySim transaction, Model 1 and the Rule Engine combine at
        weights 0.80 and 0.10. Model 2's 0.10 weight applies only within the
        ULB context — CORTANA does not perform artificial row-wise fusion
        across the two datasets.
      </p>
    </div>
  );
}
