#!/usr/bin/env bash
# session-start.sh
#
# Runs at Claude Code session start. Surfaces:
# - any conflicts logged by post-memory-write.sh
# - any project_*.md that look ready to archive (>4 weeks old, no recent edits)
# - any MEMORY.md entry exceeding the 80-char hard cap
#
# Install: copy to ~/.claude/hooks/session-start.sh, chmod +x, register as
# "SessionStart" hook in ~/.claude/settings.json.

set -euo pipefail

MEMORY_DIR="${MEMORY_DIR:-$HOME/.claude/projects/$(basename "$HOME")/memory}"
LOG_FILE="${BRAIN_LOG:-$HOME/.claude/brain-conflicts.log}"
STALE_DAYS="${STALE_DAYS:-28}"
LINE_CAP="${LINE_CAP:-80}"

[ -d "$MEMORY_DIR" ] || exit 0

issues=0

if [ -s "$LOG_FILE" ]; then
  echo "⚠ brain-conflict log has entries:"
  sed 's/^/  /' "$LOG_FILE"
  echo "  Run: /brain-conflict to resolve"
  issues=$((issues + 1))
fi

stale=$(find "$MEMORY_DIR" -name 'project_*.md' -mtime +"$STALE_DAYS" 2>/dev/null || true)
if [ -n "$stale" ]; then
  echo "⚠ project_* files unchanged for >${STALE_DAYS}d (consider archiving):"
  echo "$stale" | sed 's|^|  |;s|^.*/||'
  issues=$((issues + 1))
fi

if [ -f "$MEMORY_DIR/MEMORY.md" ]; then
  long=$(awk -v cap="$LINE_CAP" 'length > cap { print NR ": " length " chars" }' "$MEMORY_DIR/MEMORY.md" || true)
  if [ -n "$long" ]; then
    echo "⚠ MEMORY.md lines over ${LINE_CAP} chars:"
    echo "$long" | sed 's/^/  /'
    issues=$((issues + 1))
  fi
fi

if [ "$issues" -eq 0 ]; then
  exit 0
fi

echo
echo "(brain-status: $issues issue(s) — see /brain-status for the full report)"
exit 0
