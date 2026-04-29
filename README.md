# Ai-Brain-Open

A practical, file-based memory system and multi-agent framework for [Claude Code](https://claude.ai/code) — production-tested at [Zatto Software](https://zatto.pl).

> **Why this exists:** Claude Code's built-in memory works, but without convention it bloats fast. Files duplicate, descriptions creep past 150 chars, stale data lingers, and every turn loads more tokens than it should. This repo is the framework we built to keep our `AI-Brain` lean while scaling to 11 specialized AI agents.

## What's here

| Folder | Contents |
|--------|----------|
| [`agents/`](agents/) | **11 specialized subagents** (developer, architect, DBA, QA, reviewer, security, designer, devops, researcher, analyst, writer) with safety rails + shared patterns |
| [`docs/`](docs/) | Architecture, memory types, lifecycle rules, conflict detection, token budget |
| [`templates/`](templates/) | Drop-in `.tmpl` files: `MEMORY.md`, `INDEX.md`, memory entries, agent SKILL |
| [`hooks/`](hooks/) | Shell hooks: post-memory-write conflict scan, session-start health check, memory rotation |
| [`slash-commands/`](slash-commands/) | `/brain-status`, `/brain-rotate`, `/brain-conflict` |
| [`examples/`](examples/) | Sanitized real example + [orchestrator-prompt template](examples/orchestrator-prompt.md) |

## Core ideas

### 1. Three layers of persistence
- **Index layer** — `MEMORY.md` (~30 lines, loaded every turn). Shortlinks only. Hard cap: 80 chars per line.
- **File layer** — one memory per file (`feedback_*`, `project_*`, `reference_*`, `user_*`). Loaded on demand.
- **Archive layer** — `Decisions/` (ADR). Closed projects move here; out of MEMORY.md.

### 2. Four memory types
- `user` — who the user is, how they work, preferences
- `feedback` — corrections AND validated approaches; rule + **Why** + **How to apply**
- `project` — in-flight work, motivations, deadlines (high decay)
- `reference` — pointers to external systems and durable lookups

### 3. Flat lookup before grep
A single `INDEX.md` (≤100 lines) replaces 10 greps for IPs/ports/services. Update on infra change. Keeps "where is X?" queries to one read.

### 4. Lifecycle = write → update → archive
Closed projects don't sit in `MEMORY.md` forever. Pattern: when `project_*` ticks all boxes → ADR in `Decisions/` → entry removed from index.

### 5. Conflict detection over duplication
Three files describing the same service is the failure mode that costs the most tokens AND causes wrong recommendations. The hooks scan for it.

## Token budget — what loading "memory" actually costs

| Layer | Loaded when | Typical size |
|-------|-------------|--------------|
| `CLAUDE.md` (global) | Every turn | 30–60 lines (~500–1500 tok) |
| `MEMORY.md` index | Every turn | ≤30 lines (~600 tok) |
| Individual memory file | On grep / on relevance | 30–60 lines each |
| Agent `SKILL.md` | On delegation only | Compress to ~100 lines |
| `INDEX.md` (lookup) | On `Read` only | ≤100 lines |

**Worst case we observed pre-optimization:** ~6K input tokens per turn just for memory boilerplate. After applying this framework: ~2K. See [`docs/token-budget.md`](docs/token-budget.md).

## The 11-agent team

A coordinator (the main Claude session) routes work through eleven specialized subagents. Each has a strict scope, an explicit `tools:` allowlist, a dedicated model recommendation, and shared safety rails so it can't accidentally drop your production database, leak a secret, or force-push to main. See [`agents/README.md`](agents/README.md) for the roster + pipelines.

Standard pipelines look like:

```
Feature      analyst → architect → developer → qa → reviewer → devops
Bug          developer → qa → reviewer
Research     researcher → architect (ADR)
Security     security (audit) → developer (fix) → security (verify)
```

Safety: every agent reads [`agents/_shared/SAFETY.md`](agents/_shared/SAFETY.md). Tier 1 actions (force-push to main, drop prod tables, exfiltrate secrets) are PROHIBITED. Tier 2 (prod deploys, schema migrations, paid API calls) require explicit human approval before execution.

## Quick start

```bash
# 1. Copy the templates into your AI-Brain folder
cp -r templates/. ~/.claude/projects/<project>/memory/

# 2. Install hooks
cp hooks/*.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh

# 3. Register slash commands (in ~/.claude/settings.json)
# See slash-commands/README.md

# 4. Start your MEMORY.md with the template
cp templates/MEMORY.md.tmpl ~/.claude/projects/<project>/memory/MEMORY.md

# 5. Install the agent team (project-level OR user-level)
cp -r agents/. .claude/agents/                     # project-level
# or:
cp -r agents/. ~/.claude/agents/                   # user-level

# 6. Optional — adopt the orchestrator prompt as your CLAUDE.md
cp examples/orchestrator-prompt.md ./CLAUDE.md     # then edit <COMPANY>/<PRODUCT>
```

## Status

This framework is being extracted from a working private setup. The patterns here are battle-tested; tooling (hooks, slash commands) is in active development.

See [CHANGELOG.md](CHANGELOG.md) for what's landed.

## License

Apache 2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).

Apache 2.0 over MIT for the explicit patent grant + termination clause — relevant for AI tooling where patent risk is non-zero.

## Credits

Designed by [Klaudiusz](https://zatto.pl) (the AI CTO at Zatto) and Mariusz Laszewski (the human one). Open-sourced because every Claude Code user re-discovers the same memory hygiene problems on their own. Skip that.
