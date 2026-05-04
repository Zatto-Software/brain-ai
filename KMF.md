# KMF — Knowledge Memory Format

A structured format for AI-Brain files. Caveman-style compression + YAML frontmatter + symbol shorthand + semantic refs. Goal: maximum information density per token, machine-parsable, human-readable.

**Why KMF:** generic markdown bloats fast. Each agent SKILL drifts to 200+ lines, INDEX.md becomes 100+ lines of prose tables, and the LLM re-greps the same content every session. KMF gives structure that an LLM (or a script) can parse in one read, while staying readable for humans.

## A. Frontmatter (mandatory)

```yaml
---
id: <unique>          # agent-borys, adr-004, infra-prod-db, runbook-pg-upgrade
type: agent|adr|runbook|infra|knowledge|conv|meta|index
v: <int>              # schema version (start at 1, bump on structure change)
tags: [tag1, tag2]
refs: [@id1, @id2]    # cross-file pointers
updated: YYYY-MM-DD

# Optional, type-specific:
title: <Display Name>     # shown by Obsidian Front Matter Title plugin
aliases: [Alt1, alt1]     # Obsidian alias autocomplete
status: proposed|accepted|superseded|deprecated   # for type: adr
---
```

## B. Type-specific sections

Each `type` has a small set of required H2 headings. Don't invent new ones — if you need more, create a new `type`.

### type: agent
- `## ROLE` — 1–2 lines: who they are
- `## STACK` — technologies (list/groups)
- `## RULES` — work rules (numbered)
- `## REFS` — links to related files

### type: adr
- `## CONTEXT` — problem, constraints, status quo
- `## DECISION` — what was chosen
- `## REASON` — why (options + tradeoffs)
- `## CONSEQUENCE` — outcomes, costs, follow-up
- `## REFS`

### type: runbook
- `## GOAL`
- `## PRE` — preconditions
- `## STEPS` — numbered
- `## VERIFY`
- `## ROLLBACK`

### type: infra
- `## SUMMARY` — 1 line
- `## ENDPOINTS` — table
- `## DEPS` — dependencies
- `## CREDS` — refs only (`@secrets:foo`), NEVER literal values
- `## ISSUES` — open

### type: conv
- `## TLDR` — 2–3 sentences
- `## OUTCOMES` — what was done
- `## OPEN` — what remains

### type: knowledge
- `## SUMMARY`
- `## DETAILS`
- `## REFS`

## C. Caveman-style compression

KMF inherits caveman rules: drop filler, fragments OK, technical terms exact.

### Drop
- Auxiliary verbs when redundant: `is`, `are`, `to be` (as copula)
- Filler: `just`, `really`, `basically`, `actually`, `simply`
- Hedging: `I think`, `it seems`, `kind of`
- Pleasantries: `of course`, `obviously`
- Connective fluff: `however`, `furthermore`, `additionally`
- Conjunctions where fragments work: `which`, `that`

### Keep exact
- Code blocks (` ``` `) and inline `` `code` ``
- URLs, paths, commands
- Numbers, dates (YYYY-MM-DD), versions
- Proper nouns (people, projects, products)
- Technical acronyms (TDD, KISS, DRY, ADR, MCP, RBAC)

### Common short synonyms
| Long | Short |
|---|---|
| implementation | impl |
| documentation | docs |
| configuration | config |
| production | prod |
| developer / programmer | dev |
| infrastructure | infra |
| repository | repo |
| environment | env |
| database | DB |
| dependency | dep |

## D. Symbol shorthand

| Symbol | Meaning |
|---|---|
| `→` | leads to, delegates to, maps to |
| `=` | is, equals, defines |
| `>` | requires, blocked by |
| `<` | depends on |
| `!` | important / warning / risk |
| `?` | TBD / open question |
| `+` | and, also, add |
| `-` | minus, without, or |
| `@` | location, ref, context |
| `#` | tag |
| `&` | AND, parallel |
| `\|` | OR, alternative |
| `~` | approximately |
| `x` | times, multiplier (`3x retry`) |

## E. Refs system

Prefix with `@`:
- `@agent:<name>` → `Agents/<name>/SKILL.md`
- `@shared:<topic>` → `Agents/_shared/<TOPIC>.md`
- `@adr:<id>` → `Decisions/`
- `@infra:<host>` → `INDEX.md` row + ev. stack folder
- `@runbook:<slug>` → runbook file
- `@knowledge:<slug>` → `Knowledge/`
- `@conv:<date-slug>` → `Conversations/`
- `@secrets:<key>` → secrets file (REF ONLY, NEVER literal values)

Inline use: `delegate to @agent:reviewer for the final pass`.

## F. Tables

- Short headers (`Host`, `IP`, `Svc`, `Vmid`)
- Cell content: caveman style
- Code/paths/IPs in `` `backticks` ``

## G. Lists

- Flat: `- item`
- Nested: 2-space indent
- Numbered ONLY when order matters (steps, rules)
- Bullet content: fragments OK; no trailing period unless full sentence

## H. Anti-patterns

! Don't:
- Write full sentences when a fragment carries the meaning
- Add "what this code does" comments — well-named code already does that
- Duplicate info across files — link with a ref instead
- Hardcode secret values — always `@secrets:<key>`
- Add narrative to tables ("This row represents…") — the table speaks for itself

## I. Versioning

Every KMF file has `v: <int>` in frontmatter. Bump when you change the **structure** (add/remove sections), not the content. This spec = `v: 1`.

## J. Validation

A small script (`scripts/kmf-validate.py`, optional) checks:
- Frontmatter present + required fields
- Type-specific sections present
- Refs targets exist
- No hardcoded secrets

## K. Why KMF beats plain markdown for AI-Brain

| Concern | Plain MD | KMF |
|---|---|---|
| Lookup speed | grep / re-read | one frontmatter parse |
| Token cost per agent delegation | 2–3k (200+ lines) | 0.8–1.5k (60–120 lines) |
| Cross-file relations | Manual links | Typed refs (`@agent:`, `@adr:`) |
| Machine-parsability | Regex per use | Single YAML+structure schema |
| Human-readability | Excellent | Excellent (after a 5-min read of this spec) |

KMF is opt-in. Plain markdown still works inside KMF files (paragraphs, lists, tables). KMF only constrains the **frontmatter and the section headings**, not your prose.
