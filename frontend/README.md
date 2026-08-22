# CORTANA — Frontend

This is the frontend/UI layer for CORTANA, built around the existing
`CORTANA_FINAL_v1.0.0` ML core (Model 1 / Model 2 / Rule Engine / Fusion
Engine). This package does not modify, retrain, or reinterpret any ML
artifact — it only presents them.

## Stack

React + TypeScript + Vite + Tailwind CSS v4, with Framer Motion, Lucide
icons, and Recharts.

## Getting started

```bash
npm install
npm run dev       # start local dev server
npm run build     # type-check + production build to dist/
npm run preview   # preview the production build locally
```

No environment variables are required to run the app today — see
`.env.example` for what the future backend integration will need.

## Project structure

```
src/
  types/            TypeScript interfaces mirroring the future backend contract
  data/
    cortanaConfig.ts   Real values from the release ZIP (weights, rules, eval metrics)
    mock/              Isolated mock-data layer — see data/mock/README.md
  utils/            Risk-level, currency, and timestamp formatting helpers
  components/       Reusable pieces (RiskBadge, RiskScore, SignalCard, FusionVisualization, …)
  layouts/          AppLayout — the app shell (sidebar / bottom nav + content)
  sections/         Landing-page scroll-story sections and the hero
  dashboard/         Command Center charts
  alerts/           AlertTable
  pages/            Route-level screens (Landing, CommandCenter, Transactions, …)
```

## What's implemented

- Landing page: cinematic hero with a restrained, original CORTANA mark
  (never a literal face, never Microsoft's Cortana), an 8-section scroll
  story walking through Observe → Detect → Challenge → Investigate → Fuse →
  Calculate → Explain → Decide, and an entry CTA into the application.
- Application shell: sidebar nav (desktop) / bottom nav (mobile).
- Command Center: headline metrics, risk distribution, decision trend,
  "needs attention" queue, and the real final-test fraud-detection metrics.
- Transactions: filterable list (dataset context + risk level) and a
  detail/investigation view showing Model 1, Rules, and Model 2 signals
  with the correct PaySim/ULB separation, the fused risk score, and which
  rules triggered and why.
- Alerts: filterable alert queue.
- Investigations: case list and a case detail page with analyst actions
  (Confirm fraud / Mark legitimate / Escalate / Add note) and a full audit
  trail.
- Model Intelligence: the real architecture and evaluation numbers pulled
  from the release ZIP's evaluation artifacts — nothing invented.
- System: operational status per component, including the services that
  don't exist yet (database, API gateway, LLM layer), clearly marked
  "Planned".

## Mock data

Everything under `src/data/mock/` is placeholder data, seeded for
consistency across reloads. See `src/data/mock/README.md`. It is isolated
from `src/data/cortanaConfig.ts`, which holds only real values read from
the release package.

## API-ready design

`src/types/index.ts` is the contract the FastAPI backend should implement.
See `API_CONTRACT.md` for suggested endpoints and how to swap the mock
layer for live calls without touching components.

## Assumptions made

- Fields not present in the release artifacts (individual field-level
  values inside `TriggeredRule`, exact per-transaction balances, etc.) are
  represented as mock data only, clearly isolated, per the brief's
  instruction not to invent real model output.
- The AI Explanation panel is a placeholder UI (disabled buttons, "coming
  soon" label) since no LLM service is connected yet; it never computes or
  displays a risk decision.
- Currency is assumed USD for display formatting; the backend can send a
  currency code per transaction (already in the `Transaction` type) and the
  formatter will respect it.
- Model Intelligence page metrics are static, taken directly from
  `evaluation/final_test_results.json` and `evaluation/final_model_comparison.csv`
  in the release ZIP. If those artifacts change in a future release, this
  page should be regenerated from the new ZIP rather than hand-edited.

## Do not

- Do not run or retrain `models/model_1` or `models/model_2` in this
  package.
- Do not change fusion weights (0.80 / 0.10 / 0.10) or the decision
  threshold (0.98) here — they belong to `fusion/fusion_config.json` in the
  ML core and are only *displayed* by the frontend.
