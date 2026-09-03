import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, CheckCircle2, XCircle, ArrowUpCircle, StickyNote } from "lucide-react";
import {
  appendInvestigationEvent,
  fetchInvestigationById,
  updateInvestigation,
} from "../data/api";
import type { Investigation } from "../types";
import RiskBadge from "../components/RiskBadge";
import DecisionPill from "../components/DecisionPill";
import AuditTimeline from "../components/AuditTimeline";
import { formatTimestamp, pct } from "../utils/risk";

export default function InvestigationDetail() {
  const { id } = useParams();
  const [investigation, setInvestigation] = useState<Investigation | null | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [note, setNote] = useState("");

  useEffect(() => {
    let mounted = true;
    async function load() {
      if (!id) {
        setInvestigation(null);
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        setError(null);
        const data = await fetchInvestigationById(id);
        if (mounted) setInvestigation(data || null);
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : "Failed to load investigation";
          setError(msg);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, [id]);

  async function handleConfirmFraud() {
    if (!id || actionLoading) return;
    try {
      setActionLoading(true);
      const updated = await updateInvestigation(id, {
        resolution: "FRAUD_CONFIRMED",
        actor: investigation?.assigned_to || "Analyst",
        note: note.trim() || "Confirmed as fraudulent by analyst review.",
      });
      setInvestigation(updated);
      setNote("");
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to confirm fraud");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleMarkLegitimate() {
    if (!id || actionLoading) return;
    try {
      setActionLoading(true);
      const updated = await updateInvestigation(id, {
        resolution: "LEGITIMATE",
        actor: investigation?.assigned_to || "Analyst",
        note: note.trim() || "Reviewed and marked legitimate.",
      });
      setInvestigation(updated);
      setNote("");
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to mark legitimate");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleEscalate() {
    if (!id || actionLoading) return;
    try {
      setActionLoading(true);
      const updated = await updateInvestigation(id, {
        status: "ESCALATED",
        actor: investigation?.assigned_to || "Analyst",
        note: note.trim() || "Escalated for senior analyst review.",
      });
      setInvestigation(updated);
      setNote("");
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to escalate case");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleAddNote() {
    if (!id || !note.trim() || actionLoading) return;
    try {
      setActionLoading(true);
      const updated = await appendInvestigationEvent(id, {
        action: "NOTE_ADDED",
        actor: investigation?.assigned_to || "Analyst",
        note: note.trim(),
      });
      setInvestigation(updated);
      setNote("");
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to add note");
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[300px] items-center justify-center">
        <span className="label-eyebrow animate-pulse">Loading Case File…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-5 py-10 md:px-8">
        <div className="panel border-ruby/40 p-6 text-center">
          <p className="text-sm text-ruby">Error: {error}</p>
          <Link to="/app/investigations" className="mt-4 inline-block text-sm text-intel hover:underline">
            Back to investigations
          </Link>
        </div>
      </div>
    );
  }

  if (!investigation) {
    return (
      <div className="px-5 py-10 md:px-8">
        <p className="text-sm text-mute">Case '{id}' not found.</p>
        <Link to="/app/investigations" className="mt-3 inline-block text-sm text-intel hover:underline">
          Back to investigations
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center gap-3 border-b border-hairline px-5 py-6 md:px-8">
        <Link to="/app/investigations" className="text-mute hover:text-ivory">
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
        </Link>
        <div>
          <p className="label-eyebrow">Case</p>
          <h1 className="font-display text-2xl text-ivory md:text-3xl">{investigation.id}</h1>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <RiskBadge level={investigation.risk_level} />
          <DecisionPill decision={investigation.decision} />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 px-5 py-6 md:px-8 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="panel p-5">
            <div className="flex flex-wrap items-center gap-x-8 gap-y-3">
              <div>
                <p className="text-[11px] text-mute">Cortana risk</p>
                <p className="mt-0.5 text-lg text-ivory">{investigation.risk_level}</p>
              </div>
              <div>
                <p className="text-[11px] text-mute">Score</p>
                <p className="data-num mt-0.5 text-lg text-ivory">{pct(investigation.risk_score, 1)}</p>
              </div>
              <div>
                <p className="text-[11px] text-mute">Decision</p>
                <p className="mt-0.5 text-lg text-ivory">{investigation.decision}</p>
              </div>
              <div>
                <p className="text-[11px] text-mute">Transaction</p>
                <Link to={`/app/transactions/${investigation.transaction_id}`} className="data-num mt-0.5 block text-lg text-intel hover:underline">
                  {investigation.transaction_id}
                </Link>
              </div>
              <div>
                <p className="text-[11px] text-mute">Opened</p>
                <p className="mt-0.5 text-sm text-ivory">{formatTimestamp(investigation.opened_at)}</p>
              </div>
            </div>

            {investigation.resolution && (
              <div
                className={`mt-4 rounded-md border px-4 py-2.5 text-sm ${
                  investigation.resolution === "FRAUD_CONFIRMED"
                    ? "border-(--color-critical)/40 text-(--color-critical)"
                    : "border-(--color-low)/40 text-(--color-low)"
                }`}
              >
                Resolved: {investigation.resolution === "FRAUD_CONFIRMED" ? "Fraud confirmed" : "Marked legitimate"}
              </div>
            )}
          </div>

          {/* actions */}
          <div className="panel p-5">
            <p className="label-eyebrow mb-4">Analyst actions</p>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <button
                type="button"
                disabled={actionLoading}
                onClick={handleConfirmFraud}
                className="flex flex-col items-center gap-2 rounded-md border border-hairline px-3 py-4 text-xs text-ivory-dim transition-colors hover:border-(--color-critical)/60 hover:text-ivory disabled:opacity-50"
              >
                <XCircle className="h-5 w-5 text-(--color-critical)" aria-hidden="true" />
                Confirm fraud
              </button>
              <button
                type="button"
                disabled={actionLoading}
                onClick={handleMarkLegitimate}
                className="flex flex-col items-center gap-2 rounded-md border border-hairline px-3 py-4 text-xs text-ivory-dim transition-colors hover:border-(--color-low)/60 hover:text-ivory disabled:opacity-50"
              >
                <CheckCircle2 className="h-5 w-5 text-(--color-low)" aria-hidden="true" />
                Mark legitimate
              </button>
              <button
                type="button"
                disabled={actionLoading}
                onClick={handleEscalate}
                className="flex flex-col items-center gap-2 rounded-md border border-hairline px-3 py-4 text-xs text-ivory-dim transition-colors hover:border-amber/60 hover:text-ivory disabled:opacity-50"
              >
                <ArrowUpCircle className="h-5 w-5 text-amber" aria-hidden="true" />
                Escalate
              </button>
              <button
                type="button"
                disabled={actionLoading || !note.trim()}
                onClick={handleAddNote}
                className="flex flex-col items-center gap-2 rounded-md border border-hairline px-3 py-4 text-xs text-ivory-dim transition-colors hover:border-intel/60 hover:text-ivory disabled:opacity-50"
              >
                <StickyNote className="h-5 w-5 text-intel" aria-hidden="true" />
                Add note
              </button>
            </div>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Write a note before adding it to the audit trail…"
              rows={2}
              className="mt-3 w-full rounded-md border border-hairline bg-surface-2 px-3 py-2 text-sm text-ivory placeholder:text-mute-2 focus:border-intel"
            />
          </div>
        </div>

        <div>
          <div className="panel p-5">
            <p className="label-eyebrow mb-4">Audit trail</p>
            <AuditTimeline events={investigation.audit_trail || []} />
          </div>
        </div>
      </div>
    </div>
  );
}
