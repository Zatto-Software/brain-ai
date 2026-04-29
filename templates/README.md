# Templates

Drop-in starter files. Copy what you need into your AI-Brain or memory directory.

## Files

| Template | Goes in | Purpose |
|----------|---------|---------|
| `CLAUDE.md.tmpl` | `~/.claude/CLAUDE.md` | Global instructions, every-turn |
| `MEMORY.md.tmpl` | `<project>/memory/MEMORY.md` | Per-project memory index |
| `INDEX.md.tmpl` | `~/AI-Brain/INDEX.md` | Flat infra lookup |
| `memory_user.md.tmpl` | `<project>/memory/user_*.md` | User profile entry |
| `memory_feedback.md.tmpl` | `<project>/memory/feedback_*.md` | Rules with rationale |
| `memory_project.md.tmpl` | `<project>/memory/project_*.md` | In-flight work |
| `memory_reference.md.tmpl` | `<project>/memory/reference_*.md` | External system pointers |
| `agent_SKILL.md.tmpl` | `~/AI-Brain/Agents/<name>/SKILL.md` | Per-agent role definition |

## Usage

Replace placeholders (`<like this>`) with your own values. Delete comments (`<!-- ... -->` and `{{-- ... --}}`) before saving.

For `MEMORY.md` and `INDEX.md`, the templates include example entries — replace, don't append.
