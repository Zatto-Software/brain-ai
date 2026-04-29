# Shared resources

Cross-cutting files referenced by every agent.

| File | What it is | Loaded when |
|------|-----------|-------------|
| `SAFETY.md` | Destructive action policy — Tier 1/2/3 + approval format | Every agent reads on spawn |
| `PATTERNS.md` | TDD, debugging, verification, commits, naming | Linked from agent SKILLs as needed |

## Why split?

Three reasons agents don't duplicate this content inline:

1. **Single source of truth.** Update once → applies to all 11 agents.
2. **Token budget.** Per-agent SKILL stays ≤140 lines. Shared content is loaded only when relevant.
3. **Audit-ability.** Reviewer reads ONE file to know the safety rules, not 11.

## Adding to `_shared/`

A pattern qualifies if:
- It appears verbatim or near-verbatim in 3+ agent SKILLs, OR
- It's a policy that MUST be uniform across the team (safety, compliance)
- It's NOT role-specific (security details stay in `straz-security`, not here)

If only 2 agents share it, keep duplicated until a 3rd appears.
