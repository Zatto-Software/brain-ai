---
description: Report on the health of the AI-Brain memory system — sizes, conflicts, stale projects
---

# /brain-status

Report on the health of the memory system. No mutations.

## What it does

Run these checks and report:

1. **Sizes**
   - `~/.claude/CLAUDE.md` line count vs. cap (50)
   - `<project>/memory/MEMORY.md` line count vs. cap (30)
   - Number of memory files (active and archived)
   - Average memory file size
   - Largest memory file (line count)

2. **Index hygiene**
   - Lines in `MEMORY.md` exceeding 80 chars
   - Memory files NOT referenced from `MEMORY.md`
   - Entries in `MEMORY.md` pointing to files that don't exist

3. **Lifecycle**
   - `project_*` files unchanged for >28 days
   - `project_*` files with no remaining unchecked boxes (archive candidates)
   - Entries in `MEMORY.md` for memories whose `description` is too vague

4. **Conflicts**
   - Replay the same scan as `hooks/post-memory-write.sh`
   - Show top 5 most-referenced identifiers with their files
   - Flag the ones where files disagree (manual review needed)

5. **Token budget estimate**
   - Approximate tokens loaded per turn (CLAUDE.md + MEMORY.md char count / 4)
   - Compare to target (~1100)

## Output format

Markdown table per section, total under 200 lines. End with a one-line verdict: ✅ healthy / ⚠ N issues / ❌ needs cleanup.

## Implementation

This is a slash command for Claude — there's no script. Claude reads the relevant files and reports. The hooks/ directory holds the helpers; this command pulls them together with judgment.
