# Hooks

Shell scripts that run on Claude Code events. They keep the memory system honest without manual effort.

## Files

| Script | Trigger | Purpose |
|--------|---------|---------|
| `post-memory-write.sh` | After Write/Edit on a memory file | Scan for conflicts (same IP/domain in 3+ files) |
| `session-start.sh` | Session start | Surface conflicts, stale projects, oversized MEMORY.md lines |
| `memory-rotate.sh` | Manual / weekly cron | List `project_*` files ready for archival |

## Install

```bash
mkdir -p ~/.claude/hooks
cp hooks/*.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh
```

## Register in `~/.claude/settings.json`

The exact schema lives in [the Claude Code hooks docs](https://docs.claude.com/en/docs/claude-code/hooks). Minimal example:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "bash ~/.claude/hooks/session-start.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "bash ~/.claude/hooks/post-memory-write.sh" }
        ]
      }
    ]
  }
}
```

## Configuration

All scripts read environment variables:

| Variable | Default | Used by |
|----------|---------|---------|
| `MEMORY_DIR` | `~/.claude/projects/$USER/memory` | all |
| `BRAIN_LOG` | `~/.claude/brain-conflicts.log` | post-memory-write, session-start |
| `STALE_DAYS` | `28` | session-start |
| `LINE_CAP` | `80` | session-start |
| `CONFLICT_THRESHOLD` | `3` | post-memory-write |

Set them in your shell profile or in the hook command line:

```json
{ "type": "command", "command": "MEMORY_DIR=/custom/path bash ~/.claude/hooks/session-start.sh" }
```

## Tuning

- **Too many false-positive conflicts** → raise `CONFLICT_THRESHOLD` to 4
- **Too many "stale project" warnings** → raise `STALE_DAYS` to 60
- **Conflict scan slow** → not a real concern below ~1000 memory files; if you hit that, you have other problems
