import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ChevronDown } from "lucide-react";
import CortanaMark from "../components/CortanaMark";

export default function Hero() {
  return (
    <section className="relative flex min-h-screen flex-col overflow-hidden bg-void">
      {/* atmospheric backdrop */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          backgroundImage:
            "radial-gradient(ellipse 70% 50% at 50% 0%, rgba(111,147,214,0.08), transparent), radial-gradient(ellipse 60% 40% at 80% 100%, rgba(201,154,84,0.05), transparent)",
        }}
        aria-hidden="true"
      />
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.035]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(241,237,228,1) 1px, transparent 1px), linear-gradient(90deg, rgba(241,237,228,1) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
        }}
        aria-hidden="true"
      />

      {/* AI presence — restrained, ~25% of composition, right side */}
      <div
        className="pointer-events-none absolute right-[2%] top-[8%] w-[38%] max-w-[380px] opacity-70 md:right-[6%] md:w-[26%]"
        aria-hidden="true"
      >
        <CortanaMark variant="presence" />
      </div>

      {/* minimal nav */}
      <div className="relative z-10 flex items-center justify-between px-5 py-6 md:px-10 md:py-8">
        <span className="font-display text-sm tracking-[0.2em] text-ivory-dim">CORTANA</span>
        <Link
          to="/app"
          className="rounded-full border border-hairline px-4 py-1.5 font-mono text-[11px] uppercase tracking-wider text-mute transition-colors hover:border-intel/50 hover:text-ivory"
        >
          Enter Cortana
        </Link>
      </div>

      {/* hero copy */}
      <div className="relative z-10 flex flex-1 flex-col justify-center px-5 md:px-10">
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="label-eyebrow"
        >
          Financial risk intelligence
        </motion.p>
        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="mt-3 max-w-3xl font-display text-[clamp(3rem,9vw,7rem)] leading-[0.95] tracking-tight text-ivory"
        >
          Cortana
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.25 }}
          className="mt-6 max-w-md text-lg text-ivory-dim"
        >
          Detect. Understand. Investigate.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.35 }}
          className="mt-3 max-w-md text-sm leading-relaxed text-mute"
        >
          An intelligence operating quietly behind the financial system —
          fusing a supervised fraud model, an independent anomaly model, and
          deterministic behavioral rules into one calibrated risk signal.
        </motion.p>
      </div>

      {/* status strip + scroll indicator */}
      <div className="relative z-10 flex items-center justify-between px-5 py-6 md:px-10 md:py-8">
        <div className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-wider text-mute">
          <span className="h-1.5 w-1.5 rounded-full bg-(--color-low)" aria-hidden="true" />
          System operational
        </div>
        <motion.div
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
          className="flex flex-col items-center gap-1 text-mute"
        >
          <span className="font-mono text-[10px] uppercase tracking-wider">Scroll</span>
          <ChevronDown className="h-4 w-4" aria-hidden="true" />
        </motion.div>
      </div>
    </section>
  );
}
