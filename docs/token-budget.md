# Token budget

What loading "memory" actually costs, measured.

## Per-turn fixed cost

Every turn loads:

| Source | Tokens (avg) | Tokens (worst) |
|--------|--------------|----------------|
| `~/.claude/CLAUDE.md` | 500–800 | 2000+ |
| `<project>/memory/MEMORY.md` | 400–600 | 1500+ |
| System prompt + tool defs | (fixed by harness) | (fixed) |
| **Total fixed memory cost** | **~1000–1400** | **3500+** |

Numbers are tokens per turn. Multiply by every message you ever send. A 60-turn working session at the worst case is ~210K tokens — just for memory boilerplate, before any actual work.

## On-demand cost

Loaded when relevant:

| Source | Frequency | Tokens |
|--------|-----------|--------|
| Single memory file | Per task | 200–500 |
| `INDEX.md` (flat lookup) | Once per topic | 800–1500 |
| Agent `SKILL.md` (uncompressed) | Per delegation | 1500–3000 |
| Agent `SKILL.md` (compressed) | Per delegation | 600–1200 |

## Where budget actually leaks

In a 60-turn session, the costs ranked from most to least controllable:

1. **`MEMORY.md` bloat.** Every line that exceeds 80 chars or duplicates info costs N×60 tokens. Fix: hard cap. ROI: 10–30% of memory tokens.
2. **`CLAUDE.md` duplication.** Tables that exist elsewhere; verbose explanations. Fix: replace with link. ROI: 30–50% of CLAUDE tokens.
3. **Stale `project_*` files.** Loaded "just in case" because Claude greps. Fix: archive to `Decisions/`. ROI: depends on stale count, often 5–15%.
4. **Uncompressed agent SKILLs.** Per-delegation cost. Fix: compress prose, keep code blocks. ROI: 50–60% per delegation.
5. **Multiple files for one topic.** Conflict-driven token waste. Fix: consolidate (see `conflict-detection.md`). ROI: variable, but high signal value.

## Real-world before/after

From the Zatto private setup that this framework was extracted from:

| Metric | Before | After |
|--------|--------|-------|
| `CLAUDE.md` lines | 60 | 32 |
| `MEMORY.md` lines | 33 | 33 (but descriptions trimmed) |
| `MEMORY.md` avg description chars | 152 | 68 |
| Memory files (active) | 31 | 29 (after consolidation) |
| Memory files (archived) | 0 | 2 (in Decisions/) |
| Agent SKILL avg lines | 240 | ~120 (compressed) |
| Estimated per-turn fixed cost | ~2800 tokens | ~1100 tokens |
| **Approximate savings per 60-turn session** | — | **~100K input tokens** |

(Token counts are estimates based on character counts; actual tokenizer output varies.)

## Sizing guidance

Targets per category:

| Item | Target | Hard cap |
|------|--------|----------|
| `CLAUDE.md` | ≤30 lines | 50 |
| `MEMORY.md` | ≤25 entries | 30 |
| `MEMORY.md` line | ≤80 chars | 100 |
| Memory file body | 30–50 lines | 80 |
| Agent SKILL | ≤120 lines (compressed) | 200 |
| `INDEX.md` | ≤80 lines | 120 |

## Measuring your own setup

Quick check:

```bash
echo "CLAUDE.md:    $(wc -l < ~/.claude/CLAUDE.md) lines"
echo "MEMORY.md:    $(wc -l < <PROJECT>/memory/MEMORY.md) lines"
echo "Memory files: $(ls <PROJECT>/memory/*.md | wc -l) files"
echo "Avg memory:   $(awk 'END{print int(NR/FNR)}' <PROJECT>/memory/*.md) lines"
echo "Long MEMORY entries (>80c): $(awk 'length > 80' <PROJECT>/memory/MEMORY.md | wc -l)"
```

If any of those exceeds the target column above, you have token leak. The slash command `/brain-status` automates this check.

## What this isn't

This is a budget for *fixed* memory cost — what's loaded automatically each turn. It's not a budget for the conversation itself, tool outputs, or files Claude reads during work. Those are unbounded by nature; the goal here is to make the part you control as small as possible so the part you don't has more room.
