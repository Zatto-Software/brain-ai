---
id: agent-bibliotekarz-curator-reference
type: reference
v: 1
tags: [reference, memory, curator, karpathy, wiki, consolidation, lint, kmf]
refs: ["@agent:bibliotekarz-curator", "@agent:atlas-architect", "@agent:rena-reviewer"]
updated: 2026-05-22
---

# Bibliotekarz — REFERENCE (deep dive)

Methods, workflows per trigger, output formats — extracted from SKILL.md (progressive disclosure).

## Stack (extended)

- `memory/YYYY-MM-DD.md` — raw append-only daily log
- `memory/topics/<slug>.md` — KMF consolidated (per topic / client / project)
- `memory/log.md` — ops record (consolidate / lint runs)
- `MEMORY.md` (root) — index, cap 200 lines, always loaded
- `memory/schema.md` — 3-layer spec (Karpathy)
- `scripts/consolidate.py` — daily → topic (9:1 compression)
- `scripts/memory-lint.py` — orphan refs / contradictions / stale / dupes

## Rules — full

### Daily
- Append-only. DO NOT edit historical dailies.
- Fragments + `HH:MM` timestamp.
- Inline `#topic-slug` tags so consolidate groups them.

### Topic
- KMF frontmatter: `id`, `type: memory-topic`, `tags`, `refs`, `updated`.
- Update when contradicting info arrives → mark old fragment `superseded:`.
- Min 5 daily entries → candidate to consolidate.
- 9:1 compression target (raw → curated).

### MEMORY.md (index)
- Cap 200 lines (hook truncates).
- Links to top-N active topics (recently updated + high-traffic).
- One topic = 1 line, ~150 chars, hook description.

### Lint pass (weekly)
- Orphan refs: `@agent:X` / `@adr:Y` with no target → flag.
- Contradictions: two topics state conflicting facts → flag + diff.
- Stale: topic `updated:` >90d + no dailies → flag candidate to archive.
- Duplicates: similarity >0.6 between topics → propose merge.

## Methods

### 1. Consolidate (daily → topic)
```
Input: memory/2026-05-01.md ... memory/2026-05-22.md (≥5 files)
Step 1: Group fragments by `#tag`
Step 2: Per group: dedupe, normalize to KMF
Step 3: Append to memory/topics/<slug>.md (or create)
Step 4: Update `updated:` field, regen MEMORY.md index
Step 5: Log to memory/log.md (lines in, lines out, compression ratio)
```
Tool: `python3 scripts/consolidate.py [--dry-run] [--since YYYY-MM-DD] [--list-pending]`

### 2. Lint
```
Run: python3 scripts/memory-lint.py [--json]
Output: report {orphans, contradictions, stale, duplicates, daily_edits, missing_frontmatter}
Per finding: severity (info|warn|error), fix suggestion
```

### 3. Promote / archive topic
- Promote = link in MEMORY.md (active themes).
- Archive = move to `memory/topics/_archive/<slug>.md`, remove from MEMORY.md.
- Decision: traffic last 30d + `updated` freshness.

### 4. Refs audit
```
Goal: every @ref has a target or a TODO marker.
Scan: grep '@(agent|adr|runbook|knowledge|conv|infra|secrets):' memory/ agents/ Decisions/
Cross-check: target exists in _meta.json or agents/<n>/ or Decisions/.
Output: list of orphan refs + use sites.
```

## Workflow

### Trigger "consolidate brain"
1. `python3 scripts/consolidate.py --dry-run` → preview
2. Approve → run live
3. Update MEMORY.md index (top-N changed)
4. `python3 scripts/regen-manifest.py` → re-index `_search.json`
5. Commit: `chore(memory): consolidate daily→topics YYYY-MM-DD (N→M lines, X:1)`

### Trigger "lint brain"
1. Run `memory-lint.py`
2. Report severity warn+ → propose fixes
3. Approve per finding → apply
4. Log to `memory/log.md`

### Trigger "audit refs"
1. Scan + cross-check
2. Per orphan: propose target or `?` marker
3. Apply patches after approval

## Output formats

### Consolidate report
```
## Consolidate run YYYY-MM-DD HH:MM
- In: N daily files, M raw lines
- Out: P topic files updated/created
- Compression: M:Q (target 9:1)
- New topics: [slug1, slug2]
- Updated topics: [slug3, slug4]
- Anomalies: [...]
```

### Lint report
```yaml
orphans:
  - ref: "@adr:adr-009-foo"
    used_in: memory/topics/bar.md:42
    severity: warn
    fix: "Create ADR or remove ref"
contradictions:
  - topics: [a.md, b.md]
    fact: "Service port"
    values: [3001, 3002]
    severity: error
stale:
  - file: memory/topics/old-thing.md
    updated: 2025-12-01
    age_days: 173
    severity: info
    suggest: archive
duplicates:
  - files: [topic-a.md, topic-b.md]
    similarity: 0.91
    severity: warn
    suggest: merge
```
