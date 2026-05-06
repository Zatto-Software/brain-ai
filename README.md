# Ai-Brain-Open

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0"></a>
  <a href="https://github.com/agentsmd/agents.md"><img src="https://img.shields.io/badge/AGENTS.md-v1.1-blue.svg" alt="AGENTS.md v1.1"></a>
  <a href="./KMF.md"><img src="https://img.shields.io/badge/KMF-v1-orange.svg" alt="KMF v1"></a>
  <a href="https://claude.ai/code"><img src="https://img.shields.io/badge/Claude%20Code-compatible-7C3AED.svg?logo=anthropic&logoColor=white" alt="Claude Code"></a>
  <a href="https://developers.openai.com/codex/guides/agents-md"><img src="https://img.shields.io/badge/Codex-compatible-10A37F.svg?logo=openai&logoColor=white" alt="Codex"></a>
  <a href="https://cursor.com"><img src="https://img.shields.io/badge/Cursor-compatible-1F2937.svg" alt="Cursor"></a>
  <a href="https://github.com/features/copilot"><img src="https://img.shields.io/badge/Copilot-compatible-2DA44E.svg?logo=github&logoColor=white" alt="GitHub Copilot"></a>
</p>

<p align="center">
  <a href="https://github.com/Zatto-Software/brain-ai"><img src="https://img.shields.io/badge/GitHub%20Mirror-Zatto--Software%2Fbrain--ai-181717.svg?logo=github&logoColor=white" alt="GitHub Mirror"></a>
  <a href="https://zatto.dev"><img src="https://img.shields.io/badge/Built%20at-zatto.dev-blueviolet.svg" alt="Built at zatto.dev"></a>
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs welcome">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Memory-Karpathy%20Wiki-FF6B6B.svg" alt="Memory: Karpathy LLM Wiki">
  <img src="https://img.shields.io/badge/Agents-12%20roles-4ECDC4.svg" alt="12 agent roles">
  <img src="https://img.shields.io/badge/Token%20saving-~80%25-success.svg" alt="~80% token reduction">
  <img src="https://img.shields.io/badge/Built%20with-%E2%9D%A4-red.svg" alt="Built with love">
</p>

A practical, file-based memory system and multi-agent framework for [Claude Code](https://claude.ai/code) — production-tested at [Zatto Software](https://zatto.dev).

> **Why this exists:** Claude Code's built-in memory works, but without convention it bloats fast. Files duplicate, descriptions creep past 150 chars, stale data lingers, and every turn loads more tokens than it should. This repo is the framework we built to keep our `AI-Brain` lean while scaling to a multi-agent team.

## What's here

| Folder / file | Contents |
|--------|----------|
| [`agents/`](agents/) | **12 specialized subagents** (developer, architect, DBA, QA, reviewer, security, designer, devops, observability, researcher, analyst, writer) with safety rails + shared patterns |
| [`docs/`](docs/) | Architecture, memory types, lifecycle rules, conflict detection, token budget, **KMF guide**, **Obsidian graph setup**, **Caveman integration** |
| [`templates/`](templates/) | Drop-in `.tmpl` files: `MEMORY.md`, `INDEX.md`, memory entries, agent SKILL, **CLAUDE.md (top + subfolder)**, **manifest.json**, **infra.json** |
| [`hooks/`](hooks/) | Shell hooks: post-memory-write conflict scan, session-start health check, memory rotation |
| [`slash-commands/`](slash-commands/) | `/brain-status`, `/brain-rotate`, `/brain-conflict` |
| [`scripts/`](scripts/) | `regen-manifest.py` — rebuild `manifest.json` + `infra.json` from your KMF files |
| [`examples/`](examples/) | Sanitized real example + [orchestrator-prompt template](examples/orchestrator-prompt.md) |
| [`KMF.md`](KMF.md) | **Knowledge Memory Format spec** — typed frontmatter + section schema + symbol shorthand for token-efficient memory |

## Core ideas

### 1. Three layers of persistence
- **Index layer** — `MEMORY.md` (~30 lines, loaded every turn). Shortlinks only. Hard cap: 80 chars per line.
- **File layer** — one memory per file (`feedback_*`, `project_*`, `reference_*`, `user_*`). Loaded on demand.
- **Archive layer** — `Decisions/` (ADRs). Closed projects move here; out of `MEMORY.md`.

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

### 6. KMF — typed frontmatter + section schema
Once your brain has 50+ files, plain markdown stops scaling. KMF gives every file typed frontmatter (`id`, `type`, `v`, `tags`, `refs`), enforces a small set of H2 sections per type (e.g. `## ROLE / STACK / RULES / REFS` for agents), and uses symbol shorthand (`→`, `@`, `>`, `!`). A `regen-manifest.py` script then builds a single `manifest.json` covering the whole brain — one read replaces dozens of greps. See [`KMF.md`](KMF.md) and [`docs/kmf.md`](docs/kmf.md).

### 7. Per-folder `CLAUDE.md`
Claude Code auto-loads `CLAUDE.md` from the working directory and parents. Drop a 20-line `CLAUDE.md` into each brain subfolder (`Agents/`, `Decisions/`, `Knowledge/`, ...) telling the coordinator where to look first in that folder. Free context, picked up automatically. See [`templates/CLAUDE.md.subfolder.tmpl`](templates/CLAUDE.md.subfolder.tmpl).

### 8. Per-agent model routing
Each agent declares `model:` in its `SKILL.md` frontmatter. Architects → `opus` (slow, expensive, smart). Developers → `sonnet` (fast, cheap, competent). Writers → `haiku` (cheapest). ~70% of work doesn't need `opus` — and now we measure it (see Observability below).

### 9. Skills auto-load — zero token cost when not triggered
Claude Code's [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) load only when their `description:` matches the task. We curate a set per agent role instead of dumping everything into the system prompt.

## Recommended skill set (production-tested)

These are the [Anthropic Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) we wire into agents. Drop them into `~/.claude/skills/` and they activate automatically by description match.

| Category | Skill | Source | Triggers when… |
|----------|-------|--------|----------------|
| Engineering | `systematic-debugging` | [obra/superpowers](https://github.com/obra/superpowers) | a bug, test failure, or unexpected behavior shows up |
| Engineering | `verification-before-completion` | [obra/superpowers](https://github.com/obra/superpowers) | the agent is about to claim "done" / "fixed" / "passing" |
| Engineering | `using-git-worktrees` | [obra/superpowers](https://github.com/obra/superpowers) | feature work needs isolation from current workspace |
| UI / Frontend | `frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) | building UI, design system, or styling work |
| UI / Frontend | `webapp-testing` | [anthropics/skills](https://github.com/anthropics/skills) | browser-based e2e / smoke tests via Playwright |
| Docs | `pdf`, `docx`, `xlsx` | [anthropics/skills](https://github.com/anthropics/skills) | producing or extracting from those file formats |
| Data & Observability | `dashboard-specification` | [nimrodfisher/data-analytics-skills](https://github.com/nimrodfisher/data-analytics-skills) | new dashboard or redesign — gather requirements first |
| Data & Observability | `visualization-builder` | nimrodfisher | choosing chart type, color, layout |
| Data & Observability | `query-validation` | nimrodfisher | SQL review before deploy |
| Data & Observability | `time-series-analysis` | nimrodfisher | trends, anomalies, seasonality, forecasting |
| Data & Observability | `metric-reconciliation` | nimrodfisher | two sources disagree — find the root cause |
| Data & Observability | `root-cause-investigation` | nimrodfisher | spike, regression, on-call debug |

`description:` quality matters more than skill count. A bad description triggers on the wrong tasks and wastes a load. Keep them under 150 chars and lead with the trigger ("Use when…").

## Observability — measure, don't guess

If you can't see what context loads on each turn, you can't optimize it.

We added a self-observation layer: every Claude Code session writes JSONL transcripts; a sync script normalizes them into Postgres; Grafana renders cost-per-session, tokens-per-model, cache hit rate, and top-cost sessions.

```
~/.claude/projects/**/*.jsonl
        │
        ▼
   sync (incremental, idempotent)  ───►  Postgres  ───►  Grafana
        │                                                  ▲
        ▼                                                  │
   Prometheus exporter (ccusage daily) ─────────────────────┘
```

What this unlocks:
- **Per-agent cost slicing** — which `SKILL.md` actually pays back its `opus` routing
- **Cache hit rate** — instantly tells you when `MEMORY.md` index drift is hurting
- **Session distribution** — find the long-tail expensive sessions before they become a habit

The tooling (sync script, exporter, dashboard JSON) lives in our private mirror. We'll publish a sanitized version after first community feedback — open an issue if you want it sooner.

## Token budget — what loading "memory" actually costs

| Layer | Loaded when | Typical size |
|-------|-------------|--------------|
| `CLAUDE.md` (global) | Every turn | 30–60 lines (~500–1500 tok) |
| `MEMORY.md` index | Every turn | ≤30 lines (~600 tok) |
| Individual memory file | On grep / on relevance | 30–60 lines each |
| Agent `SKILL.md` | On delegation only | Compress to ~100 lines |
| Skill (Anthropic) | On description match | 0 when idle, 1–3K when fired |
| `INDEX.md` (lookup) | On `Read` only | ≤100 lines |

**Worst case we observed pre-optimization:** ~6K input tokens per turn just for memory boilerplate. After applying this framework: **~2K** — a sustained ~70% reduction. See [`docs/token-budget.md`](docs/token-budget.md).

## The 12-agent team

A coordinator (the main Claude session) routes work through twelve specialized subagents. Each has a strict scope, an explicit `tools:` allowlist, a dedicated model recommendation, and shared safety rails so it can't accidentally drop your production database, leak a secret, or force-push to main. See [`agents/README.md`](agents/README.md) for the roster + pipelines.

Standard pipelines look like:

```
Feature      analyst → architect → developer → qa → reviewer → devops
Bug          developer → qa → reviewer
Research     researcher → architect (ADR)
Security     security (audit) → developer (fix) → security (verify)
Dashboard    architect → observability → developer → devops → qa
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

# 7. Optional — adopt KMF + the manifest workflow
cp KMF.md <brain>/                                       # the format spec
cp templates/CLAUDE.md.brain.tmpl <brain>/CLAUDE.md      # top-level coordinator hint
cp templates/CLAUDE.md.subfolder.tmpl <brain>/Agents/CLAUDE.md
cp -r scripts <brain>/                                   # manifest regen script
python3 <brain>/scripts/regen-manifest.py                # generate manifest.json + infra.json

# 8. Optional — caveman ecosystem (output / MCP / graph compression)
# See docs/caveman-integration.md for the full menu. Minimal install:
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash

# 9. Optional — wire up the recommended Anthropic Agent Skills
git clone https://github.com/obra/superpowers /tmp/superpowers
git clone https://github.com/anthropics/skills /tmp/anthropics-skills
git clone https://github.com/nimrodfisher/data-analytics-skills /tmp/nfdata
cp -r /tmp/superpowers/skills/{systematic-debugging,verification-before-completion,using-git-worktrees} ~/.claude/skills/
cp -r /tmp/anthropics-skills/skills/{frontend-design,webapp-testing,pdf,docx,xlsx} ~/.claude/skills/
cp -r /tmp/nfdata/skills/* ~/.claude/skills/
```

## What's new

- **2026-05** — Per-agent model routing made measurable. Recommended skill set documented. Observability section added (Postgres + Grafana stack outline). Worked example updated to a 13-agent team.
- **2026-04** — Initial public release. Three-layer persistence, four memory types, flat-lookup `INDEX.md`, lifecycle hooks, conflict detection.

See [CHANGELOG.md](CHANGELOG.md) for the full log.

## Status

This framework is being extracted from a working private setup. The patterns here are battle-tested; tooling (hooks, slash commands, observability bridge) is in active development.

## License

Apache 2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).

Apache 2.0 over MIT for the explicit patent grant + termination clause — relevant for AI tooling where patent risk is non-zero.

## Credits

Maintained by Mariusz Laszewski / [Zatto Software](https://zatto.dev).

Open-sourced because every Claude Code user re-discovers the same memory hygiene and agent-coordination problems independently. Skip that step — fork what works, replace what doesn't.

Inspirations and components we lean on:

- [agentsmd/agents.md](https://github.com/agentsmd/agents.md) — `AGENTS.md` interop spec
- [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — self-maintaining knowledge base pattern
- [Anthropic Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — `SKILL.md` spec
- [obra/superpowers](https://github.com/obra/superpowers), [anthropics/skills](https://github.com/anthropics/skills), [nimrodfisher/data-analytics-skills](https://github.com/nimrodfisher/data-analytics-skills) — production skills we ship to agents
