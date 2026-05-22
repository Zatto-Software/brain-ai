# Memory types

Four types. Each has a distinct lifecycle and load pattern. Picking the wrong type is the most common mistake — `project` type masquerading as `reference` type is what creates stale data.

## `user`

**Who the user is and how they work.**

Permanent. Updated rarely. Loaded for almost every task to inform tone and depth.

Good `user` memories:
- Role, seniority, primary languages
- Stack expertise (and gaps)
- Preferred working style (terse vs explanatory; PRs vs commits; CI vs local)
- Time zone or work hours (only if it affects scheduling)

Bad `user` memories:
- Negative judgments ("user gets confused easily")
- One-time observations ("user was tired today")
- Information about the *project* rather than the person

**Filename:** `user_<topic>.md` (e.g., `user_role.md`, `user_polish_speaker.md`)

## `feedback`

**Guidance about how to approach work — corrections AND validated approaches.**

The most underused type. People remember to save corrections ("don't do X") but forget to save validated approaches ("the unusual thing I tried — yes, keep doing that"). Save both. Otherwise Claude drifts toward over-cautious defaults.

Body structure:
```
<rule>

**Why:** <reason — often a past incident or strong preference>
**How to apply:** <when/where this kicks in>
```

The **Why** is what makes feedback survive edge cases. A rule with no rationale becomes dogma; a rule with a rationale lets Claude judge whether the situation actually fits.

**Filename:** `feedback_<topic>.md`

## `project`

**In-flight work — goals, motivations, deadlines, stakeholders.**

High decay. Most stale memory comes from here. Body structure same as `feedback`:

```
<fact or decision>

**Why:** <constraint, deadline, stakeholder>
**How to apply:** <how this should shape suggestions>
```

**Critical rule:** convert relative dates to absolute when saving. "Thursday" → `2026-03-05`. Otherwise the memory becomes uninterpretable in two weeks.

**When to archive:**
- All pending items resolved → Decisions/ADR
- Project on ice >2 weeks → archive (resurrect from Decisions/ if revived)
- Successor project memory exists → link both, archive old

**Filename:** `project_<slug>.md`

## `reference`

**Durable pointers to external systems and lookups.**

Long-lived. Updated on infrastructure change, not on every conversation. Good for: API endpoints, hostnames, ports, where things are tracked, how to access them.

Bad `reference` memories:
- Anything ephemeral (current sprint state, temporary credentials, in-flight migrations) — those belong in `project`
- Anything derivable from code or `git log`

**Filename:** `reference_<topic>.md`

## Type selection — quick decision tree

```
Is the fact about the user (the person)?
   yes → user
   no  ↓
Is it about how to work (rules, do/don't)?
   yes → feedback
   no  ↓
Will this be true in 3 months?
   yes → reference
   no  → project
```

If still unclear: it's `project`. Project memories are the most aggressively cleaned, so the cost of a mis-classification there is lowest.

## Cross-cutting rules

- **One concept per file.** If you're tempted to use sub-headings, you probably need two files.
- **Filename = lowercase + underscores.** No spaces, no dates in filename (dates go in frontmatter or in `Decisions/` slugs).
- **Frontmatter `description` is a load-decision input.** Be specific and concrete. "API endpoints" loses to "Stripe webhook signature validation endpoint and secret env var name".
- **Never duplicate.** Before writing a new memory, grep for the topic. Update existing > create new.

## Anti-patterns we've seen

| Symptom | Likely root cause |
|---------|-------------------|
| Three files describing the same service with different IPs | Each session created new `reference_*` instead of updating existing |
| `MEMORY.md` past 100 entries | No archival happening; closed projects sitting in index |
| Claude recommends a function that doesn't exist | `reference` memory not verified before recommending; should grep first |
| Same correction given multiple times | Feedback memory not saved (or saved but description too vague to surface) |

## Karpathy 3-layer LLM-Wiki (v3 extension)

The four memory types above are the **content typology**. The 3-layer wiki is the **lifecycle typology** — orthogonal, complementary. Both apply.

```
Layer 1 — DAILY   memory/YYYY-MM-DD.md        raw, append-only
              ↓   consolidate.py (≥5 dailies, ≥24h gap)
Layer 2 — TOPICS  memory/topics/<slug>.md     curated, KMF, type: memory-topic
              ↓   promote / archive (traffic + freshness)
Layer 3 — INDEX   MEMORY.md                   hot, always loaded, cap 200 lines
```

### Layer 1 — daily
- Append-only. NEVER edit historical daily logs (audit-trail invariant).
- Fragments + `HH:MM` timestamp.
- Inline `#topic-slug` tags so consolidate can group.
- No frontmatter (raw).

### Layer 2 — topics
KMF frontmatter required:
```yaml
---
id: topic-<slug>
type: memory-topic
v: 1
tags: [...]
refs: [@agent:X, @adr:Y]
updated: YYYY-MM-DD
---
```
- Update when contradicting info arrives → mark old fragment `superseded:`, don't delete.
- 9:1 compression target from source dailies.
- Lifecycle: born (≥5 dailies tagged) → active (linked in MEMORY.md) → stale (>90d, no recent dailies) → archived (moved to `memory/topics/_archive/`).

### Layer 3 — index
- Cap 200 lines (hook truncates beyond).
- One topic = 1 line ≤150 chars.
- Order: active themes > stable contexts > archive.

### Compression budget

| Layer | Avg size | Compression |
|-------|----------|-------------|
| Daily (raw) | 50-200 lines/file | 1:1 |
| Topic (curated) | 80-150 lines | 9:1 vs source dailies |
| Index entry | 1 line/topic | ~100:1 vs topic |

Target: full hot context ≤200 lines, ~30KB cold per active topic.

### Operations

- Append (every session): write to today's daily, no edits to historicals.
- Consolidate (weekly / on demand): `python3 scripts/consolidate.py` → bibliotekarz-curator does the LLM pass.
- Promote / archive: traffic + freshness scoring, manual approval.
- Lint: `python3 scripts/memory-lint.py` — orphan refs, contradictions, stale, duplicates, daily-edit (error).

The curator agent that owns this: `agents/bibliotekarz-curator/SKILL.md`.
