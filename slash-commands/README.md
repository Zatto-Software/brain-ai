# Slash commands

Three commands for managing the brain. They're prompt-style command files — Claude reads them on invocation and follows the spec.

## Files

| Command | Purpose | Mutates? |
|---------|---------|----------|
| `/brain-status` | Health report (sizes, conflicts, stale, budget) | No |
| `/brain-rotate` | Find archive candidates, draft ADRs, archive on confirmation | Yes (with confirmation) |
| `/brain-conflict` | Resolve conflicts surfaced by the hook | Yes (with confirmation) |

## Install

In Claude Code, slash commands live in `~/.claude/commands/<name>.md`. Copy:

```bash
mkdir -p ~/.claude/commands
cp slash-commands/*.md ~/.claude/commands/
```

The `description` frontmatter line is what shows in the Claude Code command palette.

## Usage rhythm

- **Daily:** rely on `session-start.sh` to surface issues at session start.
- **Weekly:** `/brain-status` for the full report.
- **On flag:** `/brain-conflict` when the session-start hook reports conflicts.
- **End of project:** `/brain-rotate` after a feature ships or an incident closes.

## Customizing

Each command is a markdown spec read by Claude as a prompt. Edit them to match your repo conventions:

- Different memory dir → update path references in the command body
- Different ADR format → update the template in `/brain-rotate`
- Different archival rules → update the decision rules in `/brain-conflict`

The hooks (`hooks/`) provide the deterministic detection; the slash commands provide the judgment + writes.
