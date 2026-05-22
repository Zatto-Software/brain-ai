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

## Branch + PR workflow

Every agent that writes code or config MUST work on a dedicated branch and open a Pull Request when done. NEVER commit directly to `main` / `master` / `production`.

**Standard flow:**

```bash
# 1. Branch from latest main
git checkout main && git pull
git checkout -b <type>/<short-slug>      # e.g. feat/auth-flow

# 2. Work — small focused commits, conventional format
git add <specific files>                  # never `git add .` / `git add -A`
git commit -m "feat: add login endpoint"

# 3. Push the branch
git push -u origin <branch>

# 4. Open PR with summary + verification + reviewers
gh pr create --title "..." --body "..."   # or `glab` / `forgejo` equivalent

# 5. Return the PR URL to the orchestrator
```

**Branch naming:** `<type>/<short-slug>` — types from conventional commits (`feat/`, `fix/`, `refactor/`, `chore/`, `docs/`, `test/`, `perf/`).

**PR description must include:**
- What changed and why (1-3 sentences)
- Verification: command run + result (`✓ 47/47 passed`)
- Screenshots for UI changes
- Linked issue / story (if any)
- Anything reviewer should focus on

**NEVER:**
- Commit directly to protected branches
- Push to someone else's branch without asking
- Force-push to `main` / `master` / shared branches
- Open a PR without running tests + linter locally first
- Mark the task done before reporting the PR URL

**Used by:** `borys-developer`, `pixel-designer`, `daga-dba`, `olek-devops`, `klio-writer` (any agent that writes files).

## Output to orchestrator

Every subagent returns a condensed report (~1-2k tokens):

```markdown
## Summary
<1-2 sentences on what was done>

## Branch + PR
- Branch: `feat/<slug>`
- PR: <URL to the PR>
- Status: open / draft / merged

## Files changed
- path/to/file.ts:42-78 — <what changed>
- path/to/other.tsx:10 — <what changed>

## Verification
$ npm test
✓ 47/47 passed

## Follow-ups (not done, noted for later)
- <thing you noticed but is out of scope>
```

For agents that DON'T write files (`rena-reviewer`, `straz-security` audit-only, `sowa-researcher`, `nika-analyst` planning-only): omit the Branch + PR section, keep the rest.

**Used by:** all subagents.

## Delegation template (O/CT/OF/TG/TB/SC)

For non-trivial delegations to a subagent, structure the prompt with these six fields:

- **O** (Objective) — one sentence, concrete goal
- **CT** (Context) — what is already known / excluded, with file:line refs
- **OF** (Output Format) — exact shape of the deliverable
- **TG** (Tools Granted) — explicit allowlist (≤5)
- **TB** (Tools Blocked) — explicit deny list (always include if anything is destructive)
- **SC** (Success Criteria) — how the orchestrator will verify, ≤3 points

Full template, examples, and per-agent tool defaults: [SUBAGENT_PROMPTS.md](./SUBAGENT_PROMPTS.md).

**Used by:** the orchestrator, every time a subagent is launched for a task >5 minutes or >3 files.
