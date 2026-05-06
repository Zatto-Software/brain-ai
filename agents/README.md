# Agents

Twelve specialized AI subagents for Claude Code. Battle-tested at Zatto Software, refactored for general use.

Each agent lives in its own folder with a `SKILL.md` that defines:
- **Frontmatter:** `name`, `description` (with explicit triggers + anti-triggers), `tools` allowlist, `model`
- **Role + workflow:** what they own, how they work
- **Safety rails:** destructive actions they MUST refuse without approval
- **Output format:** what they return to the orchestrator
- **Anti-patterns:** what they NEVER do

## Roster

| Agent | Role | Use when |
|-------|------|----------|
| [`borys-developer`](borys-developer/SKILL.md) | Senior Full-Stack Developer | Implement features, fix bugs, refactor |
| [`atlas-architect`](atlas-architect/SKILL.md) | Solution Architect | System design, ADRs, pattern selection |
| [`daga-dba`](daga-dba/SKILL.md) | Database Administrator | Schema design, query tuning, migrations |
| [`teo-qa`](teo-qa/SKILL.md) | QA Engineer | Test plans, unit/integration/E2E tests |
| [`rena-reviewer`](rena-reviewer/SKILL.md) | Code Reviewer | PR review against OWASP + perf + readability |
| [`straz-security`](straz-security/SKILL.md) | Security Engineer | Audits, threat modeling, hardening |
| [`pixel-designer`](pixel-designer/SKILL.md) | UI/UX + Frontend | Visual design + frontend implementation |
| [`olek-devops`](olek-devops/SKILL.md) | Infrastructure Engineer | Docker, CI/CD, deploys, monitoring |
| [`graffy-observability`](graffy-observability/SKILL.md) | Observability & Data-Viz Specialist | Grafana dashboards, PromQL/SQL, alerts, metric design |
| [`sowa-researcher`](sowa-researcher/SKILL.md) | Tech Research Analyst | Library / framework / pattern evaluation |
| [`nika-analyst`](nika-analyst/SKILL.md) | Business Analyst | User stories, sprint planning, KPIs |
| [`klio-writer`](klio-writer/SKILL.md) | Tech Writer | Docs, README, changelogs, UI copy |

## How they work together

The agents do NOT talk to each other. A coordinator (the main Claude session, or you) routes work through them. See [`examples/orchestrator-prompt.md`](../examples/orchestrator-prompt.md) for a coordinator template.

## Default git workflow — branch + PR, always

Every agent that writes files MUST work on a dedicated feature branch and open a PR when done. **Direct commits to `main` / `master` / `production` are a Tier 1 prohibited action** (see [`_shared/SAFETY.md`](_shared/SAFETY.md)).

The agent returns the PR URL to the orchestrator as part of its standard output (see [`_shared/PATTERNS.md#branch--pr-workflow`](_shared/PATTERNS.md#branch--pr-workflow)). The orchestrator (or human) reviews + merges — agents do not self-merge.

## Common pipelines

```
Feature        nika-analyst → atlas-architect → borys-developer → teo-qa → rena-reviewer → olek-devops
Bug fix        borys-developer (diagnose+fix) → teo-qa (regression test) → rena-reviewer
Research       sowa-researcher → atlas-architect (ADR)
Security audit straz-security (audit) → borys-developer (fixes) → straz-security (verify)
New page       pixel-designer (design+UI) → borys-developer (logic) → teo-qa → rena-reviewer
Sprint plan    nika-analyst → orchestrator (push to Plane / Linear / Jira)
DB optimize    daga-dba (analyze+plan) → borys-developer (apply ORM changes) → teo-qa
Dashboard      atlas-architect (what to measure) → graffy-observability (panels+alerts) → borys-developer (instrumentation) → olek-devops (provision) → teo-qa
Metric drop    graffy-observability (RCA) → borys-developer (fix) → teo-qa (regression)
```

## Naming convention

Format: `<name>-<role>`, e.g. `borys-developer`. The personal name is a project tradition (Zatto's AI team has names); the role suffix makes the directory self-documenting and improves orchestrator routing. You can drop the personal name when forking — `developer/`, `architect/`, etc. all work.

## Installing

### As project-level subagents (`.claude/agents/`)
```bash
# In your project root
mkdir -p .claude/agents
cp -r path/to/Ai-Brain-Open/agents/* .claude/agents/
```

### As user-level subagents (`~/.claude/agents/`)
```bash
mkdir -p ~/.claude/agents
cp -r path/to/Ai-Brain-Open/agents/* ~/.claude/agents/
```

### Pick a subset
You don't need all 12. For a typical web app project, the minimum useful set is:
- `borys-developer`
- `teo-qa`
- `rena-reviewer`
- `straz-security`

Add the others as your project grows.

## Model recommendations

The `model:` field in each SKILL.md is a default — override per project / cost target.

| Tier | Agents | Why |
|------|--------|-----|
| **Opus** | `atlas-architect`, `rena-reviewer`, `straz-security`, `sowa-researcher` | Reasoning-heavy, low frequency, high stakes |
| **Sonnet** | `borys-developer`, `daga-dba`, `pixel-designer`, `olek-devops`, `graffy-observability`, `teo-qa`, `nika-analyst`, `klio-writer` | Execution + good-enough reasoning, high frequency |
| **Haiku** | (none default — but `teo-qa` and `klio-writer` work well on Haiku for simple tasks) | Speed / cost-sensitive routine work |

## Customizing

Every SKILL.md is a starting point — fork and adapt. Common changes:

- **Stack section** — replace our defaults (PostgreSQL / Next.js / Tailwind) with yours
- **Tool allowlist** — restrict further per your security posture
- **Anti-patterns** — add the ones you've been bitten by
- **Pipelines** — your team's actual flows

Keep the structure: the consistency across agents is what makes routing reliable.

## See also

- [`_shared/SAFETY.md`](_shared/SAFETY.md) — destructive action policy that ALL agents follow
- [`_shared/PATTERNS.md`](_shared/PATTERNS.md) — TDD, debugging, verification, naming
- [`../examples/orchestrator-prompt.md`](../examples/orchestrator-prompt.md) — example coordinator
