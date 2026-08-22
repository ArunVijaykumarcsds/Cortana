import type { Decision } from "../types";

export default function DecisionPill({ decision }: { decision: Decision }) {
  const isReview = decision === "REVIEW";
  return (
    <span
      className={`inline-flex items-center rounded-[3px] px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider ${
        isReview
          ? "bg-(--color-critical)/12 text-(--color-critical)"
          : "bg-(--color-low)/12 text-(--color-low)"
      }`}
    >
      {decision}
    </span>
  );
}
