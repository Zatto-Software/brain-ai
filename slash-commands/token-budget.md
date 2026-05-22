---
description: Daily Claude Code token-spend + cache hit-rate analysis. Wrapper on ccusage daily JSON.
---

# /token-budget [N_days]

Report token spend and cache efficiency over the last N days (default 7). Wraps `scripts/token-budget.py`, which itself wraps `ccusage daily --json`.

## What it does

1. `python3 scripts/token-budget.py [N_days]` — fetch + analyze ccusage daily breakdown.
2. Per-day table: cost USD, total tokens, cache hit %, models used.
3. Summary line: total cost, total tokens, avg/median cost per day, avg/min hit rate.
4. Anomaly detection:
   - Day with cost >2× rolling median → flag
   - Day with hit rate <50% → flag (cache invalidation or large eval)
5. Recommendation block (only when anomalies present): which agent / SKILL / manifest likely to blame.

## Auto-trigger

Offer this command when the user says:
- "how much did I spend on Claude"
- "session cost"
- "cache hit rate"
- "token spend"
- "what's my budget"

## Output format

```
Token budget — last 7d

date         cost$       tokens   hit%   models
------------------------------------------------------------
2026-05-16     12.34   2,345,678   78.2  OSH
2026-05-17      8.21   1,234,567   82.1  OS
...
------------------------------------------------------------
TOTAL: $XX.XX (YY,YYY,YYY tokens) — avg $A/d, hit B%

ANOMALIES (if any):
  ! 2026-05-19 — >2× median ($30)
  ! 2026-05-22 — low cache hit (38%)
```

Model codes: O=opus, S=sonnet, H=haiku.

## Dependencies

- `ccusage` CLI installed and authenticated (`npm install -g ccusage` or equivalent).

## Related

- Owner agent (planned): `agents/kompresor-economist/SKILL.md`
- Script: `scripts/token-budget.py`
- Doc: `docs/token-budget.md`
