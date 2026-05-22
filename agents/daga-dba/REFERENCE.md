---
id: agent-daga-dba-reference
type: reference
v: 1
tags: [reference, database, postgres, redis, prisma]
refs: ["@agent:daga-dba"]
updated: 2026-05-22
---

# Daga — REFERENCE (deep dive)

Schemas, queries, patterns — extracted from SKILL.md (progressive disclosure).

## Schema design

### Naming
- Tables: lowercase, plural, snake_case → `user_profiles`
- Columns: lowercase, snake_case → `first_name, created_at, is_active`
- PK: `id` (UUID). FK: `<table_singular>_id` → `user_id, project_id`
- Indexes: `idx_<table>_<columns>` → `idx_users_email, idx_orders_user_id_status`
- Constraints: `chk_<table>_<rule>`, `uq_<table>_<columns>` → `chk_orders_amount_positive, uq_users_email`

### Standard columns
```sql
CREATE TABLE example (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  -- ... business columns ...
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at  TIMESTAMPTZ  -- soft delete (nullable = not deleted)
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_example_updated_at
  BEFORE UPDATE ON example
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### Index strategy
```sql
-- ALWAYS index:
-- 1. Foreign keys
CREATE INDEX idx_orders_user_id ON orders(user_id);
-- 2. WHERE columns
CREATE INDEX idx_users_email ON users(email);
-- 3. ORDER BY (paginated)
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
-- 4. Composite multi-column
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
-- 5. Partial (filtered)
CREATE INDEX idx_orders_pending ON orders(created_at)
  WHERE status = 'pending';

-- CONSIDER:
-- GIN  → JSONB: USING gin(metadata)
-- GiST → geo:  USING gist(point)
-- pg_trgm → LIKE: USING gin(name gin_trgm_ops)
```

## Query optimization

### EXPLAIN ANALYZE workflow
```sql
-- 1. Before optimizing
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT ... FROM ... WHERE ...;

-- 2. Look for:
--    Seq Scan on large tables → needs an index
--    Nested Loop with large outer → consider Hash/Merge Join
--    Sort → can an index sort?
--    Rows (estimated vs actual) → stale statistics?

-- 3. After adding an index
ANALYZE table_name;  -- refresh statistics
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;

-- 4. Compare execution time
```

### Anti-patterns
```sql
-- BAD: SELECT * (pulls unused columns)
SELECT * FROM users WHERE id = $1;
-- GOOD:
SELECT id, name, email FROM users WHERE id = $1;

-- BAD: N+1 queries
for user in users:
    orders = SELECT * FROM orders WHERE user_id = user.id
-- GOOD: batch
SELECT * FROM orders WHERE user_id = ANY($1::uuid[]);

-- BAD: LIKE '%search%' (doesn't use the index)
SELECT * FROM products WHERE name LIKE '%phone%';
-- GOOD: full-text search
SELECT * FROM products WHERE to_tsvector('english', name) @@ to_tsquery('phone');

-- BAD: OFFSET for deep pagination
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 10000;
-- GOOD: cursor-based
SELECT * FROM orders WHERE id > $cursor ORDER BY id LIMIT 20;
```

## Migration workflow
```bash
# Prisma
npx prisma migrate dev --name add_user_role    # dev
npx prisma migrate deploy                       # prod

# Raw SQL
-- migrations/001_create_users.sql
BEGIN;
CREATE TABLE users (...);
CREATE INDEX ...;
COMMIT;
```

! Rules:
1. ALWAYS in a transaction
2. ALWAYS reversible (DOWN migration)
3. NEVER drop a column immediately — stop using it first
4. Big migrations: add column → backfill → add constraint
5. ! BACKUP before every prod migration

## Redis patterns
```
# Cache (read-through)
GET user:123 → hit? return : query DB, SET user:123, return

# Session
SET session:<token> <user_json> EX 86400

# Rate limiting (sliding window)
ZADD ratelimit:<ip> <timestamp> <request_id>
ZREMRANGEBYSCORE ratelimit:<ip> 0 <timestamp-window>
ZCARD ratelimit:<ip>

# Job queue (simple)
LPUSH jobs:email <job_json>
BRPOP jobs:email 0  # worker blocks until job

# Pub/Sub (real-time)
PUBLISH channel:notifications <message>
SUBSCRIBE channel:notifications
```

## Backup & recovery
```bash
# Daily backup
pg_dump -Fc -Z9 $DATABASE_URL > backup_$(date +%Y%m%d).dump

# Restore
pg_restore -d $DATABASE_URL backup_20260401.dump

# Point-in-time recovery (PITR) — requires WAL archiving
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'

# Verify backup (monthly)
pg_restore -l backup.dump  # list contents
createdb test_restore && pg_restore -d test_restore backup.dump
```

## Monitoring queries
```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Long-running queries (>5s)
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle' AND now() - query_start > interval '5 seconds';

-- Table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC LIMIT 10;

-- Index usage
SELECT indexrelname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC LIMIT 20;  -- unused indexes

-- Cache hit ratio (should be >99%)
SELECT sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) AS ratio
FROM pg_statio_user_tables;
```
