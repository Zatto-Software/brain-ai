# Lifecycle — write → update → archive

Memory left on its own grows monotonically. This document is the rule set that makes it shrink in the right places.

## States

```
                ┌─────────┐
                │  fresh  │  just written, in MEMORY.md
                └────┬────┘
                     │ refined
                     ▼
                ┌─────────┐
                │  active │  in active rotation
                └────┬────┘
                     │
            ┌────────┼────────┐
            ▼        ▼        ▼
       ┌────────┐ ┌──────┐ ┌──────┐
       │updated │ │stale │ │closed│
       └────┬───┘ └──┬───┘ └──┬───┘
            │        │        │
            │        │        ▼
            │        │   ┌────────┐
            │        │   │archived│
            │        │   └────────┘
            │        │
            ▼        ▼
       ┌─────────┐ ┌────────┐
       │ active  │ │ deleted │
       └─────────┘ └────────┘
```

## Write rules

When saving a new memory:

1. **Check for existing.** Grep memory dir for the topic. If a memory exists, update — don't create new.
2. **Pick the right type.** See `memory-types.md` decision tree.
3. **Frontmatter required.** Name, description, type. Description is what Claude uses to decide whether to load — be specific.
4. **For `feedback` / `project`:** include **Why** and **How to apply** lines. A rule without rationale rots fastest.
5. **Add to MEMORY.md** as a one-line entry, ≤80 chars.
6. **Convert relative dates.** "Thursday" → `2026-03-05`. "Two weeks ago" → absolute.

## Update rules

When facts change:

1. **Update in place.** No `_v2.md` suffix. No dated copies. Git history is the version log.
2. **Update frontmatter** if the description no longer matches.
3. **Update MEMORY.md** entry if the description changed enough to matter.
4. **If the update conflicts with a sibling memory** (e.g., two memories now disagree about the same IP) — that's a signal to consolidate. See `conflict-detection.md`.

## Archive rules

A memory archives when it's no longer load-bearing for current work but should survive as institutional memory.

**Triggers:**
- All pending items in `project_*` are resolved
- Project on ice >2 weeks (move out; resurrect later if revived)
- A successor decision has been made (link both)
- A `reference_*` describes a system that no longer exists

**Procedure:**
1. Write an ADR in `<AI-Brain>/Decisions/<YYYY-MM-DD>-<slug>.md` containing:
   - Status (closed / superseded)
   - Driver (what forced the decision)
   - Outcome (what was decided / what shipped)
   - Lessons learned (the part that survives — institutional memory)
2. Delete the original memory file.
3. Remove the entry from `MEMORY.md`.
4. Commit (`archive: <slug>`).

**Don't archive a memory just because it's old.** Long-lived `reference_*` memories are fine. Only archive when the topic is *closed*.

## Delete rules

Some memories should die outright, not archive:

- The fact turned out to be wrong
- The user explicitly asks to forget
- It's a duplicate that lost the consolidation

Delete cleanly: `git rm` the file, remove from `MEMORY.md`, commit (`delete: <slug>`). The git history preserves the body.

## Cadence

There's no fixed schedule, but a useful proxy is:

- **Weekly self-check:** is `MEMORY.md` longer than 30 entries? Are any `project_*` >4 weeks old? Run `/brain-status`.
- **After every closed feature/incident:** archive the `project_*` to ADR.
- **After major infra change:** verify all `reference_*` files in the affected area; update or archive.

Automation lives in `hooks/session-start.sh` — surfaces stale projects at session start so the cleanup happens without effort.

## What to do when the file says X but reality says Y

The memory is wrong. Reality wins. Update the memory before acting on it. If you act on stale memory and only later notice the conflict, fix the memory in the *same* commit as whatever you did — or you'll forget and step on it again.
