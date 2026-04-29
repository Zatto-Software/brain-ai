---
description: Find and resolve conflicting memory files (same identifier in 3+ files)
---

# /brain-conflict

Resolve conflicts surfaced by `hooks/post-memory-write.sh`.

## What it does

1. **Read** `~/.claude/brain-conflicts.log` if present, OR replay the scan inline.

2. **For each flagged identifier**:
   - List the files that mention it
   - Read each file's relevant context
   - Determine: legitimate separation (different roles for same name) or stale duplication?

3. **For each duplication**:
   - Verify ground truth (SSH the host, hit the URL, etc. — *or* ask user to)
   - Pick canonical file (most recent, matches reality)
   - Propose merge: what gets pulled into canonical, what gets archived/deleted
   - Confirm with user before writes

4. **Apply** confirmed merges as commits (`consolidate: <topic> (N files → 1)`).

## Decision rules

- **Two files describe distinct roles** (e.g., panel vs. worker): keep separate, ensure descriptions disambiguate.
- **Two files describe the same thing differently**: one is stale. Merge to canonical.
- **One is a closed project, one is current reference**: archive the project to `Decisions/`, keep the reference.
- **Multiple project files for the same migration**: consolidate to one with current pending items only; archive the historical narratives.

## Output

For each conflict resolved, show a one-line summary:

```
✓ Dokploy: 3 files → 1 (reference_dokploy.md). Archived migration narrative to Decisions/.
```

Then a `git diff --stat` summary of the changes staged.

## Implementation

Slash command — Claude reads, decides with user, writes.
