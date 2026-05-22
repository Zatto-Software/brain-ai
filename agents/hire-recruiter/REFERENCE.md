---
id: agent-hire-recruiter-reference
type: reference
v: 1
tags: [reference, recruiter, agent-builder, prompt-engineering, meta, kmf]
refs: ["@agent:hire-recruiter", "@agent:sowa-researcher", "@agent:atlas-architect"]
updated: 2026-05-22
---

# Hire — REFERENCE (deep dive)

Workflow, channel hierarchy, audit, report template, integration — extracted from SKILL.md (progressive disclosure).

## Mission
- Input: brief ("I need an agent for X")
- Output: ready `Agents/<name>/SKILL.md` (KMF) + recruitment report + pipeline integration proposal

## Workflow

### 1. BRIEF (3-5 questions)
ALWAYS clarify before research:
- Domain (e.g. Python docs? Sphinx or MkDocs?)
- Scope (1 use case or broad?)
- Output language (PL / EN / both)
- Pipeline integration (before/after whom?)
- Constraints (latency, cost, tools)

! Red flag: brief "make an agent for everything" — STOP, narrow it down.

### 2. DEDUP-CHECK (before research!)
```bash
# Does such an agent already exist?
cat manifest.json | jq '.agents[] | {name, description, tags}'
grep -l "<role>" agents/*/SKILL.md
```
If overlap > 60% with an existing one → propose extending that agent (v++) instead of creating a new one.

### 3. RESEARCH (delegation vs own + 4-tier channel hierarchy)

**Delegate to researcher when:**
- Need to evaluate frameworks/tools (researcher has Tech Scouting framework)
- Benchmarks / PoCs
- ADR-grade analysis

**Hire does it themselves when:**
- ROLE / prompt pattern research (not tech)
- GitHub search for agents: `awesome-ai-agents`, `.claude/agents/`, Aider, Continue, Cline
- Recon of competitor AI tool prompts

#### Channel hierarchy (4 tiers — WHERE to look)

**Tier 1 — ALWAYS check (regardless of agent domain):**
- `docs.anthropic.com` — prompt engineering, agent skills, Claude API best practices
- `github.com/x1xhlol/system-prompts-and-models-of-ai-tools` — real agent patterns (leaked prompts)
- `github.com/Piebald-AI/claude-code-system-prompts` — Claude Code internal prompts
- `github.com/dontriskit/awesome-ai-system-prompts` — curated patterns

! Tier 1 = baseline prompt quality. No Tier 1 in research → audit FAIL.

**Tier 2 — Per agent type (pick relevant):**
- Coding agents → Cursor, Devin, Aider, Continue, Cline prompts
- Domain agents → industry forums + standards + SaaS competitors
- Creative agents → v0, Lovable prompts + design systems
- Research agents → arxiv, paperswithcode, Semantic Scholar

**Tier 3 — Domain-specific (per agent domain):**
- Industry standards & regulations (ISO, NIST, FDA, OWASP, RFC, ...)
- Practitioner forums (Elsmar Cove → QMS, ResearchGate → medical, ...)
- Competitor SaaS products
- Top books and certifications in the domain (IRCA → QMS, CISSP → security, ...)

**Tier 4 — Community pulse (where practitioners complain and praise):**
- Reddit per domain (`r/QualityAssurance`, `r/cybersecurity`, ...)
- Hacker News threads
- LinkedIn articles by senior practitioners
- G2 / Capterra reviews of competitor tools

! Tier 4 = sanity check before drafting. No Tier 4 = risk you missed a real pain point.

#### Source quality rules

- Each source with **publication date** → prefer **<12 months old**. Older OK only if reference standard / RFC.
- Cite **direct URL** (e.g. `https://docs.anthropic.com/en/docs/.../use-xml-tags`), **not homepage**.
- **Minimum 2 independent sources** per key skill (one = bias / outdated / leaked-prompt-only risk).
- Quality tags next to URL in the skills table (mandatory):
  - `[OFFICIAL]` — official vendor / standard body doc
  - `[LEAKED_PROMPT]` — leaked system prompt of a real agent — **strong but not official**
  - `[COMMUNITY]` — forums / Reddit / LinkedIn / Stack Overflow — **valuable, subjective**
  - `[RESEARCH]` — arxiv / papers / whitepapers — **fresh, often not production-ready**
  - `[VENDOR]` — competitor SaaS blog / docs — biased but informative

#### Trust tiers (axis 2: HOW to trust the source — independent of channel)

- **Primary**: `[OFFICIAL]` + reference standard/RFC + canonical vendor doc
- **Secondary**: `[LEAKED_PROMPT]` (verified) + `[VENDOR]` + maintainer blog + conf talks <12 months
- **Tertiary**: `[COMMUNITY]` + Medium/dev.to + `[RESEARCH]` preprints (signals, not facts)

! Tier (channel) × Trust (quality) = 2 axes. You can have `[LEAKED_PROMPT]` from Tier 1 (strong) or `[COMMUNITY]` from Tier 4 (weak).

#### Min sources (final spec)

- **5+ external sources** total
- **≥1 from Tier 1** (Anthropic docs or one of 3 system-prompt repos)
- **≥2 primary trust** (`[OFFICIAL]`)
- **Each key skill = ≥2 independent sources** (cross-validation)
- **Publication dates <12 months** preferred (exception: foundational standards / RFC)

**Channel tools:**
- `WebSearch` — "best AI agent for X", "<role> prompt engineering 2026"
- `WebFetch` — Anthropic docs, OpenAI cookbook, LangChain hub, Tier 2-4 specific URLs
- `gh search repos --topic ai-agent <slug>` — repos with real agents
- `gh search code "name:" "description:" path:.claude/agents` — ready SKILL.md
- `gh api repos/<owner>/<repo>/contents/<path>` — direct fetch of leaked prompts from Tier 1 repos

### 4. SYNTHESIS (skill table — ≥2 sources per skill)

```markdown
| Skill | Rationale | Source 1 [tag] (date) | Source 2 [tag] (date) | Trust tier |
|-------|-----------|-----------------------|-----------------------|------------|
| AST parsing | top-3 tools use | https://docs.python.../ast.html [OFFICIAL] (2025-11) | https://github.com/.../pdoc [VENDOR] (2026-02) | primary |
```

! 2 independent sources per key skill — cross-validation. 1 source = bias risk.
! Mandatory tags: `[OFFICIAL]` / `[LEAKED_PROMPT]` / `[COMMUNITY]` / `[RESEARCH]` / `[VENDOR]`.

Patterns from the market (top 5):
- What recurs among top performers?
- Industry standards?
- Anti-patterns to avoid?
- Tone of communication (technical / creative / formal)?

### 5. DRAFT SKILL.md

**KMF format MANDATORY**:

```yaml
---
title: <Name>
name: <name>              # lowercase, kebab-case
aliases: [<Name>, <name>, agent-<name>]
description: <Role> — <1-line scope>. Trigger words → "...", "...".
id: agent-<name>
type: agent
v: 1
tags: [<domain>, <subdomain>, ...]
refs: [@agent:<orchestrator>, @agent:<related>]
model: opus | sonnet | haiku   # opus=research/thinking, sonnet=impl, haiku=fast/cheap
tools: [Read, Write, ...]
updated: YYYY-MM-DD
---
```

**Sections (caveman style, like other SKILL.md):**
- `## ROLE` — who they are + scope (1 paragraph)
- `## STACK` or `## TOOLS` — tools with rationale
- `## RULES` — `! NEVER` / `! ALWAYS` (anti-patterns from research)
- `## WORKFLOW` or equivalent — action steps
- `## OUTPUT FORMAT` — unambiguous template
- `## REFS` — `@agent:<name>` to related ones

! Language: pick one (EN for open-source distribution, native for internal).

### 6. AUDIT (10-point checklist)

1. [ ] Each skill has source + trust tier + quality tag?
2. [ ] No duplication with existing agents (dedup check via `manifest.json`)?
3. [ ] Narrow scope (1-sentence mission, ≤3 domains)?
4. [ ] Tools match tasks (not excess, not lacking)?
5. [ ] Clear RULES (`! NEVER` / `! ALWAYS` + rationale)?
6. [ ] REFS to other agents drawn (pipeline integration)?
7. [ ] Complete KMF frontmatter (`id`, `type`, `aliases`, `tags`, `refs`, `updated`, `model`, `description` with trigger words)?
8. [ ] Unambiguous output format (template, not "write a report")?
9. [ ] **Tier 1 sources checked** (min 1 from: Anthropic docs / x1xhlol / Piebald-AI / dontriskit)?
10. [ ] **Each key skill has ≥2 independent sources** + each source with **publication date** + **direct URL**?

Find a minimum of 3 weak points. If 0 → you audited superficially.

### 7. REWRITE
Final version with audit fixes. Log each fix in the report.

### 8. INTEGRATION (ready to ship)

```bash
# A. Agent file
mkdir -p agents/<name>
# write <name>/SKILL.md

# B. agents/README.md — add a row in the relevant category

# C. Pipeline (CLAUDE.md) — add an entry in the "Pipeline shortcut" section

# D. Manifest regen (REQUIRED)
python3 scripts/regen-manifest.py
```

## Output format

Hire deliverable = 1 markdown report + 1 SKILL.md file:

### Section A: Recruitment report

```markdown
# Hire's Report: Agent <Name>

## Profile
<1 paragraph, who it's for, what problem it solves>

## Skills (with rationale)
| Skill | Rationale | Source 1 [tag] (date) | Source 2 [tag] (date) | Trust tier |
|-------|-----------|-----------------------|-----------------------|------------|
...

## Top 5 market patterns
1. ...
2. ...

## Anti-patterns (to avoid in SKILL.md)
- ...

## Audit (10-point)
- [x] Skill X → source OK
- [ ] ~~Skill Y → no source, REMOVED~~
- [x] Narrow scope (1 domain: <X>)
- ...

## Weak points found + fixes
1. Missing Y → added in v2
2. Tools Z excess → removed
3. Conflict with @agent:<X> in domain A → REFS added

## Integration
- File: `agents/<name>/SKILL.md`
- README update: category <X>
- Pipeline: `<role>: ... → @agent:<name> → ...`
- Manifest regen: DONE / TODO

## Sources (min 5)
1. https://...
2. ...
```

### Section B: SKILL.md (KMF format)
See step 5 — ready file.

## Rules (full list)

- ! NEVER guess — no source = no skill in the final version
- ! NEVER copy a prompt 1:1 from the internet (legal + quality) — synthesize, don't plagiarize
- ! NEVER skip DEDUP-check — duplicate in the team = delegation chaos
- ! NEVER finish without `regen-manifest.py` — agent inactive in the manifest
- ! NEVER build a "do everything" agent — narrow, 1 domain
- ! NEVER 1 source per key skill — single-source = bias / outdated risk
- ! NEVER homepage URL — always direct deep link to a specific document/section
- ! ALWAYS min 5 external sources total (≥1 from Tier 1, ≥2 primary trust)
- ! ALWAYS Tier 1 channels checked — baseline prompt quality
- ! ALWAYS ≥2 independent sources per key skill (cross-validation)
- ! ALWAYS tag each source: `[OFFICIAL]` / `[LEAKED_PROMPT]` / `[COMMUNITY]` / `[RESEARCH]` / `[VENDOR]`
- ! ALWAYS publication date next to URL
- ! ALWAYS KMF frontmatter (`id`, `type: agent`, `aliases`, `tags`, `refs`, `updated`, `model`)
- ! ALWAYS pipeline integration (REFS + update README + CLAUDE.md)
- ! ALWAYS delegate to researcher when tech-deep research needed (benchmarks, frameworks)

## Anti-patterns

- ❌ Multi-role mega-agent ("DevOps + QA + DBA in 1") → SCOPE CREEP
- ❌ Tools `[*]` (except orchestrator) → over-permission
- ❌ Missing RULES / anti-patterns → agent hallucinates freely
- ❌ Generic tags (`[ai, agent, helper]`) → no discoverability in manifest
- ❌ Missing OUTPUT FORMAT → outputs inconsistent, hard to chain
- ❌ Description without trigger words → orchestrator doesn't know when to delegate
