# CORTANA backend deployment

Build from the repository root:

```sh
docker build -f backend/Dockerfile -t cortana-api .
```

Set `ENV=production`, `DATABASE_URL`, `CORS_ORIGINS`, and a long random
`CORTANA_API_KEY`. Use `backend/.env.example` as the template; never commit a
populated environment file. Apply `alembic -c backend/alembic.ini upgrade head`
as a separate deployment step before starting the container. The container
exposes its readiness endpoint at `/api/v1/health`.

Mutating endpoints require `X-API-Key` in production. Configure
`CORS_ORIGINS` with the exact frontend deployment origin(s).
