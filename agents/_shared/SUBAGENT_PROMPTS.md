---
id: shared-subagent-prompts
type: pattern
v: 1
tags: [shared, subagent, delegation, prompt-template, agent-tool]
refs: ["@shared:PATTERNS"]
updated: 2026-05-22
---

# Subagent prompts — O/CT/OF/TG/TB/SC template

A structured prompt format for the `Agent` tool. Eliminates vague briefs ("fix the bug in X" without file/lines/criteria).

## Schema

```
O  (Objective)        — 1 sentence. What concretely is to be achieved. No "based on findings".
CT (Context)          — what is already known / excluded, why it matters, file paths + lines
OF (Output Format)    — output shape (text structure / JSON schema / file(s) to write)
TG (Tools Granted)    — explicit list (Read, Edit, Bash, Grep). Subagent may use only these.
TB (Tools Blocked)    — explicit deny list (e.g. WebFetch, destructive git, network)
SC (Success Criteria) — how the orchestrator verifies. ≤3 points.
```

## Template

```
O: <one-sentence goal>

CT:
- <fact 1: file:line>
- <fact 2: what was tried / excluded>
- <fact 3: motivation / link>

OF:
- <struct 1: e.g. "report ≤200 words">
- <struct 2: e.g. "list of changed files">

TG: [Read, Grep, Bash]
TB: [WebFetch, git push, rm]

SC:
1. <criterion 1>
2. <criterion 2>
```

## Pipeline mapping (sample)

Per agent slug → recommended `Agent.subagent_type`:

| Agent | subagent_type | Tools default | Model |
|---|---|---|---|
| sowa-researcher | general-purpose | [Read, WebFetch, WebSearch, Grep, Bash] | opus |
| atlas-architect | general-purpose | [Read, Edit, Write, Bash, Grep] | opus |
| nika-analyst | general-purpose | [Read, Edit, Write] | sonnet |
| borys-developer | general-purpose | [Read, Edit, Write, Bash, Grep] | sonnet |
| teo-qa | general-purpose | [Read, Edit, Write, Bash] | sonnet |
| rena-reviewer | general-purpose | [Read, Bash, Grep] | sonnet |
| olek-devops | general-purpose | [Read, Edit, Write, Bash, Grep] | sonnet |
| straz-security | general-purpose | [Read, Grep, Bash, WebFetch] | opus |
| twoseven-isms | general-purpose | [Read, Grep, Bash, WebSearch, WebFetch] | opus |
| pixel-designer | frontend-design | [Read, Edit, Write, Bash] | sonnet |
| daga-dba | general-purpose | [Read, Edit, Write, Bash] | sonnet |
| iso-quincy | general-purpose | [Read, Write, Grep, Glob, Bash, WebSearch, WebFetch] | opus |
| bibliotekarz-curator | general-purpose | [Read, Edit, Write, Bash, Grep] | sonnet |
| klio-writer | general-purpose | [Read, Write, Bash] | sonnet |
| graffy-observability | general-purpose | [Read, Edit, Write, Bash] | sonnet |
| hire-recruiter | general-purpose | [Read, Edit, Write, Bash, WebSearch, WebFetch] | opus |

! Per-agent tools **override** — check `agents/<name>/SKILL.md` (authoritative).

## Rules (DO)

- Full absolute paths in CT (no relative paths).
- Explicit O/OF/TG/TB > inline "do whatever needed".
- TG ≤5 tools — more = scope creep.
- TB **always** if anything is destructive (git push, rm, drop table, force).
- SC verifiable by the orchestrator (read file / grep / curl). Not "should work".

## Anti (DON'T)

- ! DO NOT delegate a task <5min or <3 files — spawn overhead > gain
- ! DO NOT "based on your findings, implement" — that pushes synthesis to the subagent. Do the research yourself, then delegate implementation with explicit instructions
- ! DO NOT "fix the bug" without file:line + repro + expected
- ! DO NOT delegate when a midstream human decision is needed — the subagent will block
- ! DO NOT have 2 agents on the same file in parallel — race condition

## Example — bug-fix delegation

```
O: Fix duplicate-render in SearchResults component (apps/web/components/search-results.tsx:42-67).

CT:
- React 18 + Next 15. Component re-renders 3× per query.
- Profiler shows `useEffect` line 51 fires 3× — I checked the dependency `[query, filters]`.
- `filters` is an inline object literal in the parent (search-page.tsx:88) — new ref every render.
- I suspect the fix: `useMemo` on filters in parent. Don't change the logic; only ref stability.

OF:
- Edit search-page.tsx:88 — wrap filters in useMemo with deps [<specific fields>]
- Show diff
- Run `pnpm test components/search` — show exit code

TG: [Read, Edit, Bash]
TB: [WebFetch, git push, Write]

SC:
1. `pnpm test components/search` exits 0
2. Diff is only in search-page.tsx, nothing else
3. Profiler `useEffect` fires 1× after the fix (manual check)
```

## Refs

- `@shared:PATTERNS` — cross-agent patterns (TDD, debugging, code-review)
- `agents/<name>/SKILL.md` — authoritative tools/model per agent
- Pipeline shortcut: see project root `CLAUDE.md`
