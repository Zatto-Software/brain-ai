---
description: Identify project memories ready to archive, write ADRs, clean MEMORY.md
---

# /brain-rotate

Walk the rotation: find closed `project_*` files, propose ADRs, archive on confirmation.

## What it does

1. **Find candidates** by running `hooks/memory-rotate.sh` logic:
   - `project_*` files with zero unchecked boxes
   - Files unchanged for >28 days
   - Files with explicit "closed" / "shipped" markers in body

2. **For each candidate, propose**:
   - ADR slug (`<YYYY-MM-DD>-<topic>.md`)
   - Driver / Outcome / Lessons learned summary (drafted from the project file content)
   - Which `MEMORY.md` entry would be removed

3. **Confirm with user** before any write. Show the proposed ADR contents in the chat.

4. **On confirmation**:
   - Write ADR to `<AI-Brain>/Decisions/`
   - Delete the original `project_*.md`
   - Remove the entry from `MEMORY.md`
   - Stage all three changes as a single commit (`archive: <topic>`)

## Anti-patterns to avoid

- **Don't auto-archive.** Always show ADR proposal first.
- **Don't lose institutional memory.** The Lessons learned section is the survivor of the original — extract it carefully.
- **Don't rotate active projects** just because they're old. Check the git log for recent edits to *referenced* files; if work is happening, the memory may still be active.

## Implementation

This is a slash command — Claude reads the candidates, drafts ADRs, asks for confirmation, then writes.
