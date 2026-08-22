# Mock data layer

Everything in `src/data/mock/` is placeholder data for frontend development.
None of it comes from the real CORTANA models — the `.pkl` artifacts in the
release ZIP are never loaded or executed in the browser.

- `generator.ts` — deterministic, seeded mock transactions (PaySim + ULB
  contexts, kept architecturally separate per `fusion_config.json`).
- `alerts.ts` — alerts derived from the mock transactions.
- `investigations.ts` — mock case files + audit trails for the
  human-in-the-loop workflow.
- `systemStatus.ts` — mock operational status for services that don't
  exist yet (database, API gateway, LLM explanation layer).

When the FastAPI backend exists, replace the imports from this folder with
calls to `src/data/api.ts` (to be added) implementing the same TypeScript
interfaces from `src/types/index.ts`. No component should need to change —
only the data source.
