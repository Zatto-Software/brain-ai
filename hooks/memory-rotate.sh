#!/usr/bin/env bash
# memory-rotate.sh
#
# Finds project_*.md files where every checkbox is ticked OR all "pending"
# sections are empty. These are candidates for archival to Decisions/.
#
# Does NOT auto-archive — archival is a human + AI decision (institutional
# memory needs to be extracted into the ADR before the original is deleted).
#
# Run manually or as a weekly cron.

set -euo pipefail

MEMORY_DIR="${MEMORY_DIR:-$HOME/.claude/projects/$(basename "$HOME")/memory}"

[ -d "$MEMORY_DIR" ] || { echo "MEMORY_DIR not found: $MEMORY_DIR" >&2; exit 1; }

echo "Project memories ready for archival review:"
echo

found=0
for f in "$MEMORY_DIR"/project_*.md; do
  [ -e "$f" ] || continue

  # Count unchecked boxes and "pending"/"todo" markers in body
  unchecked=$(grep -cE '^\s*-\s*\[ \]' "$f" || true)
  pending=$(grep -cE '(^|\b)(pending|todo|in[- ]progress|open)(\b|:)' "$f" || true)

  if [ "$unchecked" -eq 0 ] && [ "$pending" -le 1 ]; then
    name=$(basename "$f" .md)
    age_days=$(( ( $(date +%s) - $(stat -c %Y "$f") ) / 86400 ))
    echo "  $name (last edit: ${age_days}d ago)"
    found=$((found + 1))
  fi
done

if [ "$found" -eq 0 ]; then
  echo "  (none — all project_* still active)"
fi

echo
echo "To archive: write ADR in Decisions/, delete project file, remove from MEMORY.md."
