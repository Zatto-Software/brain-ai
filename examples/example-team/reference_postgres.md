---
name: Postgres conventions
description: Naming, migration tooling, env var for the team's Postgres usage
type: reference
---

## Conventions
- Tables: `snake_case`, plural (`users`, `order_items`)
- Columns: `snake_case`, singular
- Primary keys: `id uuid` default `gen_random_uuid()`
- Timestamps: `created_at`, `updated_at` (timestamptz, default `now()`)

## Migrations
- Tool: `golang-migrate/migrate`
- Path: `db/migrations/<timestamp>_<slug>.up.sql` + `.down.sql`
- Run: `make migrate-up` (uses `DATABASE_URL` env)

## Env
- `DATABASE_URL` → loaded from `.env` (gitignored)
- Format: `postgres://user:pass@host:port/db?sslmode=disable`

**Why:** New team members repeatedly ask about migration tool and column naming.
**How to apply:** Apply when generating new tables, migrations, or DB queries.
