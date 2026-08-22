import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import Hero from "../sections/Hero";
import StorySection from "../sections/StorySection";
import {
  ObserveVisual,
  DetectVisual,
  ChallengeVisual,
  InvestigateVisual,
  FuseVisual,
  CalculateVisual,
  ExplainVisual,
  DecideVisual,
} from "../sections/StoryVisuals";

export default function Landing() {
  return (
    <div className="bg-void">
      <Hero />

      <StorySection
        index="01"
        line="I observe."
        title="Every transaction enters the system"
        body="PaySim and ULB transactions arrive on their own streams. CORTANA keeps them in separate dataset contexts from the first moment — no context is guessed or merged."
        visual={<ObserveVisual />}
      />

      <StorySection
        index="02"
        line="I detect."
        title="Model 1 — supervised fraud probability"
        body="A Random Forest classifier trained on PaySim scores the likelihood of fraud, calibrated so its output can be weighed evenly against the other signals."
        visual={<DetectVisual />}
        reverse
      />

      <StorySection
        index="03"
        line="I challenge."
        title="Six behavioral rules"
        body="Deterministic checks — unusual amounts, inconsistent balances, high-risk transaction types — run alongside Model 1 on the same PaySim context."
        visual={<ChallengeVisual />}
      />

      <StorySection
        index="04"
        line="I investigate anomalies."
        title="Model 2 — independent anomaly detection"
        body="An Isolation Forest trained unsupervised on the ULB dataset. It never sees PaySim transactions, and its score is never row-paired with Model 1 or the rules."
        visual={<InvestigateVisual />}
        reverse
      />

      <StorySection
        index="05"
        line="I fuse the signals."
        title="The Cortana Fusion Engine"
        body="Within each dataset's own context, the active signals combine at fixed weights — 0.80 / 0.10 / 0.10 — into one calibrated fused risk score."
        visual={<FuseVisual />}
      />

      <StorySection
        index="06"
        line="I calculate risk."
        title="Four risk levels"
        body="The fused score maps to Low, Medium, High, or Critical. A locked threshold of 0.98 separates a routine Pass from a Review."
        visual={<CalculateVisual />}
        reverse
      />

      <StorySection
        index="07"
        line="I explain."
        title="Deterministic risk factors"
        body="Every flagged transaction shows exactly which rules triggered and why. A future language layer will narrate this in plain English — it will never make the decision."
        visual={<ExplainVisual />}
      />

      <StorySection
        index="08"
        line="You decide."
        title="Human-in-the-loop review"
        body="CORTANA surfaces the case. An analyst confirms, dismisses, or escalates it — and every action is written to a permanent audit trail."
        visual={<DecideVisual />}
        reverse
      />

      {/* closing CTA */}
      <section className="relative border-t border-hairline px-5 py-28 text-center md:px-10">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
        >
          <p className="label-eyebrow">Ready when you are</p>
          <h2 className="mx-auto mt-4 max-w-lg font-display text-4xl text-ivory md:text-5xl">
            Enter Cortana
          </h2>
          <Link
            to="/app"
            className="mt-8 inline-flex items-center gap-2 rounded-full border border-intel/40 bg-intel/10 px-6 py-3 font-mono text-xs uppercase tracking-wider text-intel transition-colors hover:bg-intel/20"
          >
            Open the application →
          </Link>
        </motion.div>
        <p className="mx-auto mt-16 max-w-md text-[11px] leading-relaxed text-mute-2">
          CORTANA_FINAL_v1.0.0 · Phase 6 · This is an original product
          identity — not affiliated with, and does not use assets from,
          Microsoft's Cortana.
        </p>
      </section>
    </div>
  );
}
