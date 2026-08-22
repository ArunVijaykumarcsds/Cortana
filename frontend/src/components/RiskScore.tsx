import { RISK_COLOR_VAR } from "../utils/risk";
import type { RiskLevel } from "../types";

interface RiskScoreProps {
  score: number; // 0..1
  level: RiskLevel;
  size?: number;
  label?: string;
}

export default function RiskScore({ score, level, size = 128, label }: RiskScoreProps) {
  const r = (size - 12) / 2;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - score);
  const color = RISK_COLOR_VAR[level];

  return (
    <div className="inline-flex flex-col items-center gap-2">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label={`Fused risk score ${(score * 100).toFixed(1)} percent`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--color-surface-3)"
          strokeWidth="6"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dashoffset 1s cubic-bezier(0.16,1,0.3,1)" }}
        />
        <text
          x="50%"
          y="46%"
          textAnchor="middle"
          className="data-num"
          fill="var(--color-ivory)"
          fontSize={size * 0.19}
          fontWeight={500}
        >
          {(score * 100).toFixed(1)}
        </text>
        <text
          x="50%"
          y="62%"
          textAnchor="middle"
          fill="var(--color-mute)"
          fontSize={size * 0.075}
          fontFamily="var(--font-mono)"
          letterSpacing="0.08em"
        >
          FUSED RISK
        </text>
      </svg>
      {label && <span className="label-eyebrow">{label}</span>}
    </div>
  );
}
