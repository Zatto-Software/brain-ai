---
description: Consolidate AI-Brain memory/YYYY-MM-DD.md daily logs into memory/topics/<slug>.md (Karpathy 3-layer LLM-Wiki pattern)
---

# /consolidate-daily

Trigger a daily → topic consolidation pass over the `memory/` layer. Wraps `scripts/consolidate.py` with an LLM pass that does grouping, dedupe, and KMF normalization.

## What it does

1. `python3 scripts/consolidate.py --list-pending` → JSON of dailies not yet consolidated since the last run logged in `memory/log.md`.
2. Load each pending daily, group fragments by inline `#topic-slug` tag.
3. Per group: dedupe, normalize to KMF, append/create `memory/topics/<slug>.md`.
4. Update `MEMORY.md` index — top-N changed topics, one line ≤150 chars each.
5. Append entry to `memory/log.md` (consolidate timestamp + in/out lines + compression).
6. `python3 scripts/regen-manifest.py` — re-index `_search.json`.
7. Suggest commit message: `chore(memory): consolidate daily→topics YYYY-MM-DD (N→M lines, X:1)`.

## Auto-trigger

The slash command should be offered when:
- ≥5 pending dailies AND ≥24h since the last consolidate (per `memory/log.md`)
- User says "consolidate brain", "consolidate memory", "skonsoliduj memory"

## Output format

```
## Consolidate run YYYY-MM-DD HH:MM
- In: N daily files, M raw lines
- Out: P topic files updated/created
- Compression: M:Q (target 9:1)
- New topics: [slug1, slug2]
- Updated topics: [slug3, slug4]
- Anomalies: [list of fragments that didn't fit any topic]
```

## Don't trigger when

- <5 pending dailies (premature — invariant: target 9:1 compression needs enough source)
- A previous consolidate is <24h old
- The user is mid-session writing to a daily — wait until session end

## Related

- Owner agent: `agents/bibliotekarz-curator/SKILL.md`
- Script: `scripts/consolidate.py`
- Schema: `docs/memory-types.md`
- Lint companion: `scripts/memory-lint.py`
