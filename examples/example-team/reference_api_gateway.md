---
name: API gateway
description: Base URLs and auth header for the internal API gateway
type: reference
---

## Base URLs
- Production: `https://api.example.com`
- Staging: `https://api.staging.example.com`
- Local dev: `http://localhost:8080`

## Auth
- Header: `Authorization: Bearer <token>`
- Token source: env var `API_TOKEN` (loaded from `.env`, gitignored)

## Health check
- `GET /healthz` returns `200 {"status":"ok"}`

**Why:** Repeatedly searching the README for these basics burns time.
**How to apply:** Use these URLs as the source of truth for API calls in code or scripts.
