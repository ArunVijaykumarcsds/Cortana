# API contract — for the future FastAPI backend

This describes the API surface the frontend expects. It's derived directly
from `src/types/index.ts` and how the mock data layer (`src/data/mock/`) is
consumed by pages. Nothing here is implemented yet — the frontend currently
reads only from the mock layer.

None of this should require changing the CORTANA ML core. The backend's job
is to run the existing `models/model_1`, `models/model_2`, `rules/`, and
`fusion/` artifacts and serve their outputs in this shape.

## Suggested endpoints

| Method | Path                              | Returns                          | Used by |
|--------|------------------------------------|-----------------------------------|---------|
| GET    | `/api/transactions`                | `Transaction[]`                   | Command Center, Transactions |
| GET    | `/api/transactions?context=PaySim` | `Transaction[]` filtered          | Transactions |
| GET    | `/api/transactions/{id}`           | `Transaction`                     | Transaction detail |
| GET    | `/api/alerts`                      | `Alert[]`                         | Alerts |
| GET    | `/api/investigations`              | `Investigation[]`                 | Investigations |
| GET    | `/api/investigations/{id}`         | `Investigation`                   | Investigation detail |
| POST   | `/api/investigations/{id}/actions` | `AuditEvent` (appended)           | Investigation detail (Confirm fraud / Mark legitimate / Escalate / Add note) |
| GET    | `/api/system/status`               | `SystemStatus[]`                  | System page |
| GET    | `/api/model-intelligence`          | model + evaluation metadata       | Model Intelligence (can likely stay static, sourced from the release artifacts, unless you want it live) |

Response shapes should match the interfaces in `src/types/index.ts`
(`Transaction`, `Alert`, `Investigation`, `AuditEvent`, `SystemStatus`,
`FusionResult`, `Model1Signal`, `Model2Signal`, `RulesSignal`,
`TriggeredRule`). That file is the source of truth — please don't invent
extra fields the ML core doesn't actually produce.

## Important: dataset-context separation

`Transaction.model_1` and `Transaction.rules` should only be populated for
`dataset_context: "PaySim"` transactions. `Transaction.model_2` should only
be populated for `dataset_context: "ULB"` transactions. Never synthesize a
fused score that blends all three signals for a single row — that
row-wise fusion does not exist in the ML core (see
`documentation/architecture.md` in the release ZIP).

## Swapping mock data for the real API

1. Add a `src/data/api.ts` implementing the same function signatures as
   `src/data/mock/generator.ts`, `alerts.ts`, `investigations.ts`, and
   `systemStatus.ts` (e.g. `getTransactionById`, exported arrays or
   equivalent async fetchers).
2. Update the page-level imports to pull from `src/data/api.ts` instead of
   `src/data/mock/*`. Components should not need to change — they only
   consume the typed objects.
3. Read `VITE_API_BASE_URL` from `import.meta.env` for the fetch base.

## Not the frontend's job

- Running or retraining `models/model_1` or `models/model_2`.
- Computing fusion weights or the decision threshold — those come from
  `fusion/fusion_config.json` and should stay server-side.
- Deciding whether a transaction is fraudulent — that's the analyst, via
  the investigation actions above.
