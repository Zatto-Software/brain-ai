---
id: agent-graffy-observability-reference
type: reference
v: 1
tags: [reference, observability, grafana, prometheus, monitoring, sql, dashboards, alerting]
refs: ["@agent:graffy-observability"]
updated: 2026-05-22
---

# Graffy — REFERENCE (deep dive)

Queries, dashboard recipes, alert routing — extracted from SKILL.md (progressive disclosure).

## Typical stack (self-hosted)

| Component | Role |
|-----------|------|
| Grafana | Visualization, alert UI |
| Prometheus | TSDB, scrape targets |
| Loki | Log aggregation |
| Alertmanager | Routing, dedup, silences |
| Postgres datasource | Long-term aggregates, materialized views |
| SMTP relay (Resend / SES / etc.) | Outbound notification |

! Specific hostnames/ports live in your private `infra.json` — do NOT hardcode in SKILL.

## Queries — which language where

| Use case | Language | Datasource |
|----------|----------|-----------|
| Live metrics, rates, alerts | **PromQL** | Prometheus |
| Logs, error rates from logs | **LogQL** | Loki |
| Historical aggregates, drill-down, time-aware | **SQL** | Postgres |
| Cost/business metrics with time filter | **SQL** | Postgres (via MV) |

### PromQL — when to use
```
# Rate (events/sec) over 5min
rate(http_requests_total{status=~"5.."}[5m])

# Increase (delta) over range — counter delta
increase(claude_cost_usd_total[24h])

# Quantile over histogram bucket
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_bucket[5m])))

# Alerts: avoid `==` for floats; use `>` `<` with hysteresis
```

**Anti-patterns:** gauge with `{date="..."}` label (label-as-time). Instead: time-series counter + `increase(...[$__range])`.

### SQL for Grafana Postgres datasource
```sql
-- Time-aware with $__timeFilter (Grafana auto-injects)
SELECT
  $__timeGroup(ts, '1h') AS time,
  model,
  SUM(input_tokens + output_tokens + cache_creation_tokens + cache_read_tokens) AS tokens,
  SUM(cost_usd) AS cost
FROM claude_usage
WHERE $__timeFilter(ts)
GROUP BY 1, 2
ORDER BY 1;

-- Per-range aggregates ($__range = picker selection)
SELECT SUM(cost_usd) FROM claude_usage WHERE $__timeFilter(ts);

-- Use materialized view for ranges > 7d (perf)
SELECT bucket AS time, model, total_cost
FROM mv_usage_daily
WHERE $__timeFilter(bucket);
```

**MV refresh strategy:** sync script after INSERT runs `REFRESH MATERIALIZED VIEW CONCURRENTLY ...` (requires UNIQUE INDEX on MV). Skip if zero new rows (saves ~1s).

## Dashboard design

### Information architecture (always)
1. **Hero stats** — top section, 3-6 KPI single-stats. Readable from 3m. Override `timeFrom: now/d` or `now-24h` per panel — ignore global picker so they don't drift.
2. **Trends** — middle section, time-series + bar charts. Sync with global picker.
3. **Drill-down** — bottom section, tables and breakdowns (per service, per user, per model).
4. **Projections / forecasts** — optional, last section. Use `EXTRACT(EPOCH FROM (timeTo-timeFrom))` in SQL because the Postgres datasource doesn't support `$__range` macro reliably.

### Panel type selection
| Use | Panel type |
|-----|------------|
| Single number, trend area | `stat` (`graphMode: area`) |
| Threshold gauge | `gauge` |
| Compare buckets in time | `barchart` (vertical, stacked) |
| Continuous timeseries | `timeseries` |
| Composition % | `piechart` (donut, max 8 slices) |
| Sortable details | `table` with `cellOptions: {type: color-background}` |
| State over time (up/down) | `state-timeline` |
| Distribution | `histogram` |

**Anti-patterns:** pie with 20 slices, line chart for 3 values, gauge without threshold colors.

### Color tokens (Grafana built-in palettes)
- `palette-classic` — categorical, for per-model/per-service breakdown (consistent color per category everywhere)
- `red-yellow-green` — for thresholded metrics (latency, error rate)
- `green-yellow-red` — inverted (cost, error count)
- Fixed colors only for 1-2 panels with deliberate accent

### Templating (variables)
```
$model = SELECT DISTINCT model_short FROM claude_usage
$datasource = standard Grafana var
$bucket = chained — depends on time range
```
Multi-select + "All": `WHERE model_short ~ '${model:regex}'` (regex form handles both).

## Alert design

### Rule structure (Grafana managed alerting)
```
Query A: data source query → returns time series
Query B: __expr__ reduce → last/mean/max/min → scalar
Query C: __expr__ threshold → boolean → fires
```

Without the Reduce step B = "looks like time series data, only reduced data can be alerted on" error.

### Threshold philosophy
- **For: 0s** = fire on first eval = noisy
- **For: 5m** = standard for "X for 5min" (latency, errors)
- **For: 1h** = trends (cost, capacity)
- **For: 30m** = extreme burn rate

### Notification routing
- Default contact point: email via SMTP relay → ops@team
- Subject template: `[ENV] {{ .CommonLabels.alertname }}`
- Group_wait 30s, group_interval 5m, repeat 4h (standard)
- Critical = separate route (SMS, PagerDuty, etc.)

## Operational patterns

### Cardinality budget
- Gauge without label = 1 series. OK.
- `{date="2026-04-21"}` = N series where N = days. OK to retention=90d.
- `{user_id="..."}` = unbounded. **NO**.
- `{session_id="..."}` if top-K (e.g. top 10) — OK.
- Check: `topk(20, count by (__name__)({__name__=~".+"}))` in Prom.

### Performance triage
- Slow query > 2s: check EXPLAIN + indexes + downsample → MV.
- Dashboard load > 5s: reduce panel count (max ~20 per page) or split.
- Prom OOM: lower retention OR drop high-cardinality labels.

### Backup
- Dashboard JSON: export via `GET /api/dashboards/uid/<UID>` → commit to brain
- Prometheus rules: `/srv/compose/monitoring/prometheus/alert-rules.yml`
- Grafana DB: pg_dump grafana DB (delegate to DBA)

## Common recipes

### Cost projection panel (sync with time picker)
```sql
SELECT
  SUM(cost_usd) / EXTRACT(EPOCH FROM ($__timeTo()::timestamp - $__timeFrom()::timestamp)) * 3600 AS cost_per_hour,
  SUM(cost_usd) / EXTRACT(EPOCH FROM ($__timeTo()::timestamp - $__timeFrom()::timestamp)) * 86400 AS cost_per_day,
  SUM(cost_usd) / EXTRACT(EPOCH FROM ($__timeTo()::timestamp - $__timeFrom()::timestamp)) * 86400 * 30 AS cost_per_month
FROM claude_usage WHERE $__timeFilter(ts);
```

### KPI override (panel ignores global picker)
```json
{
  "type": "stat",
  "timeFrom": "24h",
  "title": "Last 24h tokens"
}
```

### Drill-down link (panel → another dashboard with var passed)
```json
"options": {
  "links": [{"title": "Drill", "url": "/d/<UID>?var-model=${__field.labels.model}"}]
}
```

## Delegation lanes

| What | Who |
|----|-----|
| Schema design DB | Atlas + Daga |
| UI layout (color, hierarchy, fonts) | Pixel |
| Query writing (Prom/SQL/LogQL) | **Graffy** |
| Panel JSON | **Graffy** + Borys |
| Sync script / parser | Borys |
| Deploy DB / datasource / cron | Olek |
| Verify dashboard end-to-end | Teo |
| Documentation | Klio |

**Pipeline observability feature:** Atlas (data architecture) → **Graffy** (queries + panel design) → Borys (impl JSON) → Olek (deploy) → Teo (verify) → Klio (docs).

## Anti-patterns (DON'T)
1. Gauge metric with label `date="2026-04-21"` — breaks Grafana time filter
2. Pie chart with >8 slices — unreadable
3. Alert without `for: <duration>` — flapping
4. Dashboard with >25 panels — slow load + cognitive overload
5. Hardcoded thresholds in panel JSON instead of variables — not scalable
6. Same query 5× across 5 panels — extract to recording rule or MV
7. Default Grafana time range "Last 6h" when data is daily — empty dashboard
8. Notification without subject template with context — generic noise
9. `select * from huge_table` in a panel — Grafana freeze
10. Cache hit ratio gauge next to cost gauge — inverted scales = misread

## Quick checks before commit
- [ ] Every panel has a description (tooltip)
- [ ] Time filter tested on 1h / 24h / 30d (KPIs constant, rest sync)
- [ ] All queries <2s on default range
- [ ] Color thresholds follow convention (green/yellow/red — never inverted)
- [ ] Variables work with "All" + multi-select
- [ ] Alerts fired manually (dummy condition)
- [ ] Docs updated
- [ ] Dashboard JSON committed to brain (export via API)
