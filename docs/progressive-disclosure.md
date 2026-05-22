---
title: Progressive disclosure — SKILL.md ≤100 lines + REFERENCE.md
---

# Progressive disclosure for agent SKILL.md

Once the brain has 15+ agents, each loaded SKILL.md becomes a budget item. A 250-line SKILL.md per delegation × 100 delegations/month = a lot of tokens spent on long-form preamble that the agent will re-read every time.

The fix is **progressive disclosure**: a short `SKILL.md` that loads on every delegation, plus a deeper `REFERENCE.md` the agent reads only when it needs the deep methods.

## The shape

```
agents/<name>/
├── SKILL.md        ≤100 lines — role, triggers, rules, anti-patterns, refs
└── REFERENCE.md    1-3 KB     — methods, snippets, templates, deep workflows
```

### `SKILL.md` contains

- Frontmatter: `name`, `description` (with trigger / anti-trigger phrases), `tools`, `model`
- **Role** — 1-2 sentences on who this agent is
- **When to invoke** — concrete scenarios
- **When NOT to invoke** — delegate-to-X for these cases
- **Rules** — short numbered list, the invariants
- **Output format** — exact deliverable shape
- **Anti-patterns** — `NEVER X → DO Y` pairs
- **See also** — links to `REFERENCE.md` and to related agents

### `REFERENCE.md` contains

- Frontmatter: `type: reference`, `tags`, `refs` back to the SKILL.md
- Full method walkthroughs (e.g. "the 6-step audit cycle with exit criteria")
- Code snippets, query templates, JSON examples
- Decision tables (when to use X vs Y)
- Pipeline integration details

## The rule

> Anything the agent needs to **decide whether to engage** lives in SKILL.md.
> Anything the agent needs to **execute the engagement** lives in REFERENCE.md.

A delegation that's purely "shall I take this?" reads SKILL.md alone (cheap). A delegation that's actually "do the work" reads SKILL.md + REFERENCE.md (still cheaper than a 250-line monolithic SKILL.md, because REFERENCE.md is structured for grep / skim, not for cover-to-cover reading).

## Migration playbook

For an existing 200-line SKILL.md:

1. Extract every code snippet, template, table, and multi-step procedure → `REFERENCE.md`
2. Replace each with a one-sentence pointer in SKILL.md ("Deep workflow: see REFERENCE.md")
3. Keep in SKILL.md: role, triggers, rules, anti-patterns, output schema
4. Verify `wc -l SKILL.md` ≤100
5. Add `REFERENCE.md` reference to the SKILL.md "See also" section

## What this is NOT

- It's not just "split the file in two". The split is **semantic** — decision-grade vs. execution-grade content.
- It's not a replacement for caveman compression. Both can be applied; they're orthogonal.
- It's not a free win on every agent. For agents with very thin bodies (`gemini-auditor`, `kompresor-economist` placeholder), a single SKILL.md is fine.

## Measurement

After migrating, run `/token-budget 7` for the week before and after. The cache hit rate should stay flat (because the SKILL.md prefix is smaller and more stable), and the avg per-delegation token cost should drop. If it doesn't, something was extracted into REFERENCE.md that the agent actually needed at decision time — move it back.

## Status

All 13 base agents in this repo follow this pattern (SKILL.md ≤100 lines + REFERENCE.md). The 5 v3 additions (bibliotekarz-curator, iso-quincy, twoseven-isms, kompresor-economist placeholder, gemini-auditor external) follow the same shape — though `kompresor-economist` and `gemini-auditor` ship with SKILL.md only because the body is intentionally minimal.
