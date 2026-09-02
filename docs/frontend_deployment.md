# CORTANA frontend deployment

The Vite application is configured for Vercel by `frontend/vercel.json`.
Set `VITE_API_BASE_URL` to the public backend origin and set
`VITE_USE_MOCK_DATA=false` for production. The deployment command is:

```sh
cd frontend
npm ci
npm run build
```

Configure the backend `CORS_ORIGINS` value to include the deployed frontend
origin exactly.
