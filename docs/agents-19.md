---
title: The 19-agent team
---

# The 19-agent team

This is the full roster — 19 roles (13 base + 5 v3 additions + 1 external CLI). The orchestrator (the main Claude session) routes work through these specialized subagents; each carries an explicit scope, an allowlisted tool set, a model recommendation, and shared safety rails so no agent can accidentally drop production tables or leak a secret.

## Roster

| Slug | Role | Model | Folder |
|------|------|-------|--------|
| `atlas-architect` | Solution Architect — system design, API contracts, ADRs | opus | [agents/atlas-architect/](../agents/atlas-architect/) |
| `borys-developer` | Senior Full-Stack Dev — features, fixes, TDD | sonnet | [agents/borys-developer/](../agents/borys-developer/) |
| `daga-dba` | DBA — Postgres, Redis, schema, migrations, indexing | sonnet | [agents/daga-dba/](../agents/daga-dba/) |
| `teo-qa` | QA Engineer — test design, Vitest / Playwright | sonnet | [agents/teo-qa/](../agents/teo-qa/) |
| `rena-reviewer` | Code Reviewer — correctness, security, perf, style | sonnet | [agents/rena-reviewer/](../agents/rena-reviewer/) |
| `straz-security` | Security — OWASP Top 10, audits, external repo recon | opus | [agents/straz-security/](../agents/straz-security/) |
| `pixel-designer` | UI/UX Designer — design systems, a11y, image gen | sonnet | [agents/pixel-designer/](../agents/pixel-designer/) |
| `olek-devops` | DevOps — Docker, CI/CD, deploys, monitoring | sonnet | [agents/olek-devops/](../agents/olek-devops/) |
| `sowa-researcher` | Researcher — tech scouting, benchmarks, ADR input | opus | [agents/sowa-researcher/](../agents/sowa-researcher/) |
| `nika-analyst` | Business Analyst — user stories, sprint planning, metrics | sonnet | [agents/nika-analyst/](../agents/nika-analyst/) |
| `klio-writer` | Writer — docs, READMEs, UI copy, SEO | sonnet | [agents/klio-writer/](../agents/klio-writer/) |
| `graffy-observability` | Observability — Grafana, PromQL, SQL, alert design | sonnet | [agents/graffy-observability/](../agents/graffy-observability/) |
| `hire-recruiter` | Agent Recruiter — designs SKILL.md from market research | opus | [agents/hire-recruiter/](../agents/hire-recruiter/) |
| **`bibliotekarz-curator`** | Memory Curator — Karpathy 3-layer wiki, consolidate, lint | sonnet | [agents/bibliotekarz-curator/](../agents/bibliotekarz-curator/) |
| **`iso-quincy`** | QMS Lead Auditor — ISO 9001:2015 / 2026, audit programmes | opus | [agents/iso-quincy/](../agents/iso-quincy/) |
| **`twoseven-isms`** | ISMS Lead Auditor — ISO/IEC 27001:2022, Annex A, SoA | opus | [agents/twoseven-isms/](../agents/twoseven-isms/) |
| **`kompresor-economist`** | Token Economist — manifest bloat, cache hit, model routing (placeholder) | haiku | [agents/kompresor-economist/](../agents/kompresor-economist/) |
| **`gemini-auditor`** | Deep Auditor (external CLI) — parallel multi-subagent sweeps | external | [agents/gemini-auditor/](../agents/gemini-auditor/) |

Bold rows are the v3 additions.

## Pipelines

Standard sequences the orchestrator routes through:

```
Feature           nika → atlas → borys → teo → rena → olek
Bug               borys → teo → rena
Research          sowa → atlas (ADR)
Security          straz (audit) → borys (fix) → straz (verify)
Quality (QMS)     iso-quincy → rena → teo
ISMS audit        twoseven-isms → straz | olek | daga | borys (impl fixes per clause) → rena → twoseven (closure)
Form design       iso-quincy → atlas → borys → teo → rena
Audit programme   iso-quincy → rena → klio (publish)
Dashboard         atlas → graffy → borys → olek → teo
UI                pixel → borys → teo → rena
Memory curate     bibliotekarz (daily → topics consolidate + lint orphans/contradictions/stale/dupes)
Token audit       kompresor (when implemented) — monthly cron
Deep audit        gemini (external) → straz | daga | atlas | borys (fixes) → rena
Sprint            nika → tracker (Plane / Linear / GitHub Projects)
New agent         hire → sowa (tech deep-dive opt) → hire (audit + integration)
```

## Model routing

- **Opus** — architects, researchers, security auditors, ISO lead auditors, recruiter. Used for tasks where wrong answers are expensive (ADRs, audit verdicts, agent design).
- **Sonnet** — developers, DBAs, QA, devops, writers, designers, curators. The 70% bulk of the work.
- **Haiku** — kompresor-economist (planned). Token-economy audits don't need deep reasoning; speed + cheap wins.
- **External** — gemini-auditor uses Google Gemini via shell wrapper for parallel sweeps; reports back to the orchestrator like any other agent.

See [`docs/token-budget.md`](./token-budget.md) for how to verify your routing in practice (`/token-budget 7`).

## Safety rails

Every agent reads [`agents/_shared/SAFETY.md`](../agents/_shared/SAFETY.md) (Tier 1 / 2 / 3 destructive-action policy) and [`agents/_shared/PATTERNS.md`](../agents/_shared/PATTERNS.md) (TDD, debugging, verification, branch+PR workflow). The recruiter agent (`hire-recruiter`) enforces these for every new agent added to the team.

## Adding a 20th agent

1. Brief the recruiter: domain, scope (≤3 sub-domains), output language, pipeline integration point.
2. `hire-recruiter` runs DEDUP-check against `manifest.json` — if overlap >60%, extend the existing agent instead.
3. Research phase: Tier 1-4 channels, min 5 sources, ≥2 independent per key skill.
4. Draft SKILL.md (≤100 lines) + REFERENCE.md, KMF frontmatter mandatory.
5. 10-point audit, fix weak points, rewrite.
6. Integration: add to `agents/<slug>/`, add a row in this file, update pipelines in root `CLAUDE.md`.
7. `python3 scripts/regen-manifest.py` — agent becomes discoverable.
