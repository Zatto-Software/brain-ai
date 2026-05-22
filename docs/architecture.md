# Architecture — three layers of persistence

The single biggest improvement to Claude Code memory is recognizing that not every memory has the same lifecycle. This framework separates three layers, each with its own write rule and load cost.

```
┌──────────────────────────────────────────────────┐
│   INDEX LAYER — MEMORY.md + CLAUDE.md            │
│   Loaded EVERY turn. Hard cap.                   │
│   ~30–60 lines total. Pure pointers.             │
└────────────────┬─────────────────────────────────┘
                 │
                 │ link to
                 ▼
┌──────────────────────────────────────────────────┐
│   FILE LAYER — one memory per file               │
│   Loaded on demand (grep, relevance, request).   │
│   30–60 lines each. ~30 files max.               │
└────────────────┬─────────────────────────────────┘
                 │
                 │ archive when closed
                 ▼
┌──────────────────────────────────────────────────┐
│   ARCHIVE LAYER — Decisions/ (ADR)               │
│   Loaded only when explicitly referenced.        │
│   Full prose OK. Keep institutional memory.      │
└──────────────────────────────────────────────────┘
```

## Layer 1 — Index

Two files: `~/.claude/CLAUDE.md` (global instructions) and `<project>/memory/MEMORY.md` (per-project memory index).

Both load on **every turn**. Tokens here multiply by every conversation you ever have with Claude. Treat them as cache lines: if it doesn't earn its place, evict it.

**Rules:**
- Total combined ≤ ~80 lines
- Each `MEMORY.md` entry: one line, ≤80 chars: `- [Title](file.md) — one-line hook`
- Each `CLAUDE.md` section: dense bullets, no prose explanations
- Never write content directly into the index — only pointers

**Anti-pattern:** filling `MEMORY.md` with a description that says "see file for details" — the description IS what Claude reads first to decide whether to open the file. Make it specific.

## Layer 2 — Files

One file per memory. Type prefix in filename (`feedback_*`, `project_*`, `reference_*`, `user_*`). Frontmatter declares type formally:

```markdown
---
name: <Memory name>
description: <one-line, used for relevance ranking — be specific>
type: <user|feedback|project|reference>
---

<body>
```

**Loaded when:**
- Filename matches user query (Claude greps memory dir)
- Frontmatter `description` is relevant to current task
- User explicitly references "remember when..."

**Rules:**
- 30–60 lines body. >60 = consider splitting or archiving.
- For `feedback` and `project` types: end body with **Why:** and **How to apply:** lines (rule alone isn't enough; the why is what survives edge cases)
- Update in place when facts change. Don't create `feedback_X_v2.md`.

## Layer 3 — Archive (Decisions/)

When a project closes, an ADR (Architecture Decision Record) is written and the original `project_*.md` is removed from `MEMORY.md`.

ADRs are full-prose documents in `<AI-Brain>/Decisions/`. Format:

```
Decisions/<YYYY-MM-DD>-<slug>.md
```

**ADR contents:**
- Status (closed/superseded)
- Driver (what forced the decision)
- Outcome (what was actually decided)
- Lessons learned (institutional memory — the part that survives even if the decision is reversed later)

**When to archive:**
- All pending checkboxes in the project memory are ticked
- The work has shipped / been abandoned for >2 weeks
- A successor decision has been made (link both)

## Why three layers, not two

Two-layer systems (just MEMORY.md + files) work for ~5–10 memories. Past that:
- `MEMORY.md` becomes too long → truncated at line 200 → silent data loss
- Closed projects clutter the active list → Claude burns cycles re-reading "done" work
- Lessons learned get deleted along with the project → next incident repeats the same mistake

The archive layer is where institutional memory lives. It's cheap to keep (never auto-loaded) and worth its weight in gold the next time something similar happens.

## Sizing guidance

| Project size | MEMORY.md entries | Files | Decisions/ |
|--------------|-------------------|-------|------------|
| Solo / 1 project | 5–10 | 5–10 | 1–3 ADR |
| Team / 3–5 projects | 20–30 | 25–35 | 10–20 ADR |
| Org / 10+ projects | Split per project | 30 per project | 50+ ADR |

If you're past the "Org" size, split `MEMORY.md` per project (Claude Code supports `<project>/memory/` per directory) rather than one giant index.

## L1-L4 brain-search architecture (v3)

The three-layer persistence model above is about **storage**. Brain search is about **lookup**. As the brain grows past ~50 files, even loading the index becomes expensive — and grep loses precision. The v3 architecture splits lookup into four tiers, fastest first:

```
L1 — _meta.json (hot manifest)         ~5 KB    | every turn potential
L2 — _search.json (FTS-ready index)    ~50 KB   | on demand, structured lookup
L3 — ripgrep                            n/a     | fallback fuzzy search
L4 — Basic Memory MCP (Phase 2)         n/a     | semantic, embeddings + FTS
```

### L1 — `_meta.json`
A compact manifest: only agents + decisions + clients (short descriptions, ≤150 chars each). Read first for "who/what" queries. Typical lookup: `python3 -c 'import json; m=json.load(open("_meta.json")); ...'`.

### L2 — `_search.json`
A flat, FTS-ready array of every KMF file in the brain. One entry per file with `title`, `tags`, `aliases`, `description`, `headings` (capped to 12), `first_para` (≤280 chars). Generated by `scripts/regen-manifest.py`. Typical lookup:

```python
import json
s = json.load(open("_search.json"))
[e["id"] for e in s["entries"] if "audit" in e["tags"]]
```

### L3 — ripgrep
The escape hatch. A `search.sh "query"` wrapper around `rg` for cases where you don't know the tag or the title.

### L4 — Basic Memory MCP (Phase 2, planned)
SQLite FTS5 + sqlite-vec embeddings, KMF-native. Queries are semantic — "things similar to Q" rather than exact match. Designed to live alongside L1-L3, not replace them.

**Routing rule (from ADR-008-style decision):** start at the smallest tier that can answer. L1 for "who does what", L2 for "files with tag X / heading containing Y", L3 for unknown territory, L4 for "things like this one".

See `docs/progressive-disclosure.md` for the SKILL.md ≤100 lines + REFERENCE.md split that keeps L1/L2 entries cheap.
