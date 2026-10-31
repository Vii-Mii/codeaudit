# web

Minimal React + Vite frontend for the CodeAudit API.

```bash
npm install
npm run dev   # http://localhost:5173, proxies /api to http://localhost:8000
npm run build # static files in dist/
```

Set `VITE_API_URL` at build time when the API is hosted on a different origin, and add that
frontend origin to the API's `CODEAUDIT_CORS_ORIGINS`.
