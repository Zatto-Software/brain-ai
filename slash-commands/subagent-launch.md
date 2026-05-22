---
description: Structured subagent delegation via Agent tool. Builds O/CT/OF/TG/TB/SC prompts per agents/_shared/SUBAGENT_PROMPTS.md template.
---

# /subagent-launch <agent-slug> <task-summary>

Wraps the `Agent` tool with a strict prompt template, eliminating vague briefs ("fix the bug in X" without file/lines/criteria).

## What it does

1. Read `agents/<agent-slug>/SKILL.md` to load authoritative tools + model.
2. Build a six-field prompt:
   - **O** (Objective) — one concrete sentence
   - **CT** (Context) — file:line refs, what was tried/excluded, motivation
   - **OF** (Output Format) — exact deliverable shape
   - **TG** (Tools Granted) — explicit allowlist (≤5, from SKILL.md tools)
   - **TB** (Tools Blocked) — explicit deny list (always include if destructive risk)
   - **SC** (Success Criteria) — how the orchestrator verifies (≤3 points)
3. Invoke the Agent tool with `subagent_type` matching the agent and the structured prompt as the message.
4. Receive the subagent's report and surface it back to the user.

## Auto-trigger

Offer this command when the user says:
- "delegate to <agent>"
- "spawn a subagent"
- "let <agent> do it"

## When NOT to use

- Task <5 minutes — spawn overhead > gain
- Task touching <3 files — just do it in-context
- Task requires mid-flight human decisions — subagent will block

## Template

See `agents/_shared/SUBAGENT_PROMPTS.md` for the full spec, per-agent defaults, and an example.

```
O: <one-sentence goal>

CT:
- <fact 1: file:line>
- <fact 2: what was tried / excluded>
- <fact 3: motivation>

OF:
- <struct 1>
- <struct 2>

TG: [Read, Edit, Bash]
TB: [WebFetch, git push, rm]

SC:
1. <criterion 1>
2. <criterion 2>
```

## Related

- Pattern: `agents/_shared/SUBAGENT_PROMPTS.md`
- Cross-agent patterns: `agents/_shared/PATTERNS.md`
- Lifecycle: `docs/lifecycle.md`
