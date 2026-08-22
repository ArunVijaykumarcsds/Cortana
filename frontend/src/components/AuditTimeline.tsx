import type { AuditEvent } from "../types";
import { formatTimestamp } from "../utils/risk";

const ACTION_LABEL: Record<AuditEvent["action"], string> = {
  CORTANA_FLAGGED: "CORTANA flagged transaction",
  CASE_OPENED: "opened the case",
  EXPLANATION_REQUESTED: "requested an explanation",
  CONFIRMED_FRAUD: "confirmed fraud",
  MARKED_LEGITIMATE: "marked legitimate",
  ESCALATED: "escalated the case",
  NOTE_ADDED: "added a note",
};

export default function AuditTimeline({ events }: { events: AuditEvent[] }) {
  return (
    <ol className="relative border-l border-hairline pl-5">
      {events.map((e) => (
        <li key={e.id} className="mb-6 last:mb-0">
          <span
            className="absolute -left-[4.5px] mt-1.5 h-[7px] w-[7px] rounded-full"
            style={{ background: e.actor === "CORTANA" ? "var(--color-intel)" : "var(--color-amber)" }}
            aria-hidden="true"
          />
          <div className="flex flex-wrap items-baseline gap-x-2">
            <span className="data-num text-xs text-mute">{formatTimestamp(e.timestamp)}</span>
            <span className="text-sm text-ivory">
              <span className="font-medium">{e.actor}</span> {ACTION_LABEL[e.action]}
            </span>
          </div>
          {e.note && <p className="mt-1 max-w-md text-xs leading-relaxed text-mute">{e.note}</p>}
        </li>
      ))}
    </ol>
  );
}
