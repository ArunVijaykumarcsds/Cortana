import type { ServiceState } from "../types";

const CONFIG: Record<ServiceState, { color: string; label: string }> = {
  OPERATIONAL: { color: "bg-(--color-low)", label: "Operational" },
  DEGRADED: { color: "bg-(--color-medium)", label: "Degraded" },
  OFFLINE: { color: "bg-(--color-critical)", label: "Offline" },
  PLANNED: { color: "bg-mute-2", label: "Planned" },
};

export default function SystemStatusIndicator({ state }: { state: ServiceState }) {
  const c = CONFIG[state];
  return (
    <span className="inline-flex items-center gap-2 font-mono text-xs uppercase tracking-wider text-mute">
      <span className={`h-1.5 w-1.5 rounded-full ${c.color}`} aria-hidden="true" />
      {c.label}
    </span>
  );
}
