#!/usr/bin/env bash
# post-memory-write.sh
#
# Scans the memory directory for conflicts after a write.
# Conflicts = the same identifier (IP, hostname, domain) appearing in 3+ files.
# Writes findings to ~/.claude/brain-conflicts.log; surface at next session start.
#
# Install:
#   1. Copy to ~/.claude/hooks/post-memory-write.sh
#   2. chmod +x ~/.claude/hooks/post-memory-write.sh
#   3. In ~/.claude/settings.json, add:
#      "hooks": { "PostToolUse": [{ "matcher": "Write|Edit", ... }] }
#      See https://docs.claude.com/en/docs/claude-code/hooks for the schema.

set -euo pipefail

# CONFIG — point this at your memory dir
MEMORY_DIR="${MEMORY_DIR:-$HOME/.claude/projects/$(basename "$HOME")/memory}"
LOG_FILE="${BRAIN_LOG:-$HOME/.claude/brain-conflicts.log}"
THRESHOLD="${CONFLICT_THRESHOLD:-3}"

[ -d "$MEMORY_DIR" ] || exit 0
mkdir -p "$(dirname "$LOG_FILE")"

# Extract IP-like and domain-like tokens from all memory files,
# count file appearances, flag any token in >= THRESHOLD files.
{
  echo "# brain-conflict scan $(date -Iseconds)"

  # IPv4 candidates
  grep -hoE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' "$MEMORY_DIR"/*.md 2>/dev/null \
    | sort -u \
    | while read -r ip; do
        count=$(grep -lE "\\b${ip//./\\.}\\b" "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
        if [ "$count" -ge "$THRESHOLD" ]; then
          files=$(grep -lE "\\b${ip//./\\.}\\b" "$MEMORY_DIR"/*.md | xargs -n1 basename | tr '\n' ' ')
          echo "IP $ip in $count files: $files"
        fi
      done

  # Domain candidates — adjust the suffix list to your TLDs / internal zones
  # Default: catches *.local, *.internal, *.example.com, *.test
  domain_regex='\b[a-zA-Z0-9][-a-zA-Z0-9.]*\.(local|internal|test|example\.com)\b'
  [ -n "${EXTRA_DOMAIN_SUFFIXES:-}" ] && domain_regex="\\b[a-zA-Z0-9][-a-zA-Z0-9.]*\\.($EXTRA_DOMAIN_SUFFIXES|local|internal|test|example\\.com)\\b"
  grep -hoE "$domain_regex" \
       "$MEMORY_DIR"/*.md 2>/dev/null \
    | sort -u \
    | while read -r dom; do
        count=$(grep -l "$dom" "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
        if [ "$count" -ge "$THRESHOLD" ]; then
          files=$(grep -l "$dom" "$MEMORY_DIR"/*.md | xargs -n1 basename | tr '\n' ' ')
          echo "DOMAIN $dom in $count files: $files"
        fi
      done
} > "$LOG_FILE.tmp"

if [ -s "$LOG_FILE.tmp" ] && [ "$(wc -l < "$LOG_FILE.tmp")" -gt 1 ]; then
  mv "$LOG_FILE.tmp" "$LOG_FILE"
else
  rm -f "$LOG_FILE.tmp" "$LOG_FILE"
fi

exit 0
