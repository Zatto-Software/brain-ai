---
type: shared-pattern
description: Cross-agent patterns referenced by multiple SKILL.md files. Single source of truth — change here, applies everywhere.
---

# Shared patterns

Patterns used by 2+ agents. Per-agent SKILL.md links here instead of duplicating.

## TDD — Test-Driven Development

```
1. RED      — write MINIMAL failing test (1 assertion)
2. GREEN    — write SIMPLEST code to pass
3. REFACTOR — clean up, keep tests green
4. REPEAT
```

**Rule:** ZERO production code without a failing test first (when TDD is required for the task).

**Red flags:**
- "Code first, tests later" — NO
- "Too simple to test" — NO, test it
- "Multiple tests at once" — NO, one at a time

**Used by:** `borys-developer`, `teo-qa`.

## Systematic Debugging

Before EVERY bug fix:

```
1. INVESTIGATE — collect evidence (logs, stack trace, reproduction steps)
2. HYPOTHESIZE — formulate what might be wrong
3. TEST       — verify the hypothesis (don't guess)
4. FIX        — only NOW write the fix
5. VERIFY    — fix works AND nothing else broke
```

**Rule:** ZERO fixes without root cause investigation.

**Escalation:** 3+ failed fixes → STOP, question architecture, escalate to architect.

**Used by:** `borys-developer`, `teo-qa`, `rena-reviewer`.

## Verification Before Completion

Before declaring "done":

- Run tests FRESH (not from cache)
- Read FULL output, not the first line
- Report facts: "47/47 passed" not "should work"
- NEVER declare "done" without evidence
- For UI/frontend: open in browser, check golden path + edge cases

**Used by:** all implementing agents.

## Read-before-Edit

Before editing a file in unfamiliar code:

1. Read the whole file (or the relevant section)
2. Understand project conventions (naming, structure, patterns)
3. Check if a solution already exists in the codebase
4. Plan minimal changes — don't refactor surroundings

**Rule:** Edit/Write tools require Read first in the same session.

**Used by:** all implementing agents.

## Conventional Commits

```
feat:     new functionality
fix:      bug fix
refactor: structural change without behavior change
chore:    config, tooling
docs:     documentation
test:     tests
perf:     performance optimization
```

**Format:** `<type>: <imperative summary, lowercase, no period>`

Body optional, max 72 chars per line, describe "why" not "what".

**Used by:** every agent that commits code.

## External Repo Audit

When contributing to an external repo (outside your own org):

1. Read README + CONTRIBUTING (if exists)
2. Check LICENSE — compatibility with your policies
3. Conventions: linter config, CI workflow, commit style
4. Issues / PR template — use if exists
5. Code style: match the project, don't impose your style

**Used by:** orchestrator (shortcut), `straz-security` (deep dive).

## Naming conventions (cross-language)

- **Files:** `lowercase_with_underscores.ext` or `kebab-case.ext` per language convention
- **Branches:** `<type>/<short-slug>` (`feat/auth-flow`, `fix/login-redirect`)
- **Memory files:** `<type>_<topic>.md` (`feedback_`, `project_`, `reference_`, `user_`)
- **Decisions/ADR:** `<YYYY-MM-DD>-<slug>.md`

**Used by:** `borys-developer`, `klio-writer`, orchestrator.

## Output to orchestrator

Every subagent returns a condensed report (~1-2k tokens):

```markdown
## Summary
<1-2 sentences on what was done>

## Files changed
- path/to/file.ts:42-78 — <what changed>
- path/to/other.tsx:10 — <what changed>

## Verification
$ npm test
✓ 47/47 passed

## Follow-ups (not done, noted for later)
- <thing you noticed but is out of scope>
```

**Used by:** all subagents.
