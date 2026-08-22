import type { ReactNode } from "react";

interface MetricCardProps {
  label: string;
  value: string;
  delta?: string;
  deltaTone?: "up" | "down" | "neutral";
  icon?: ReactNode;
  sublabel?: string;
}

export default function MetricCard({ label, value, delta, deltaTone = "neutral", icon, sublabel }: MetricCardProps) {
  const deltaColor =
    deltaTone === "up"
      ? "text-(--color-high)"
      : deltaTone === "down"
      ? "text-(--color-low)"
      : "text-mute";

  return (
    <div className="panel p-5">
      <div className="flex items-start justify-between">
        <span className="label-eyebrow">{label}</span>
        {icon && <span className="text-mute" aria-hidden="true">{icon}</span>}
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="data-num text-3xl font-medium text-ivory">{value}</span>
        {delta && <span className={`data-num text-xs ${deltaColor}`}>{delta}</span>}
      </div>
      {sublabel && <p className="mt-1 text-xs text-mute">{sublabel}</p>}
    </div>
  );
}
