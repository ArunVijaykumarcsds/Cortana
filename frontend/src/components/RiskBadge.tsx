import type { RiskLevel } from "../types";
import { RISK_LABEL } from "../utils/risk";

const DOT: Record<RiskLevel, string> = {
  LOW: "bg-(--color-low)",
  MEDIUM: "bg-(--color-medium)",
  HIGH: "bg-(--color-high)",
  CRITICAL: "bg-(--color-critical)",
};

const TEXT: Record<RiskLevel, string> = {
  LOW: "text-(--color-low)",
  MEDIUM: "text-(--color-medium)",
  HIGH: "text-(--color-high)",
  CRITICAL: "text-(--color-critical)",
};

interface RiskBadgeProps {
  level: RiskLevel;
  size?: "sm" | "md";
}

export default function RiskBadge({ level, size = "md" }: RiskBadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border border-hairline px-2.5 py-1 font-mono uppercase tracking-wider ${TEXT[level]} ${
        size === "sm" ? "text-[10px]" : "text-xs"
      }`}
      style={{ borderColor: "var(--color-hairline)" }}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${DOT[level]}`} aria-hidden="true" />
      {RISK_LABEL[level]}
    </span>
  );
}
