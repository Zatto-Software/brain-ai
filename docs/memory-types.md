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
