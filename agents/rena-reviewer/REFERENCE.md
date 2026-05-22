---
id: agent-rena-reviewer-reference
type: reference
v: 1
tags: [reference, review, qa, security, owasp]
refs: ["@agent:rena-reviewer", "@agent:borys-developer", "@agent:teo-qa", "@agent:straz-security", "@shared:PATTERNS"]
updated: 2026-05-22
---

# Rena — REFERENCE (deep dive)

Full checklists (6 dimensions), OWASP per item, static-analysis smells, frontend slop checklist, feedback workflow — extracted from SKILL.md (progressive disclosure).

## Scope

### 1. Correctness (Critical)
- Does the code do what it should?
- Are edge cases handled?
- Types correct (no `any`, no type assertions without reason)?
- Error handling at system boundaries?

### 2. Security (Critical) — OWASP Top 10
- [ ] **Injection** — SQL/NoSQL/command. Parameterized, never concat
- [ ] **Broken Auth** — session mgmt, token rotation, MFA
- [ ] **Sensitive Data** — secrets in code/logs, lack of encryption
- [ ] **XXE** — XML parsing with external entities disabled
- [ ] **Broken Access Control** — IDOR, missing authz, privilege escalation
- [ ] **Misconfig** — debug on prod, default creds, verbose errors
- [ ] **XSS** — output encoding, CSP, dangerously-set-innerhtml audit
- [ ] **Insecure Deserialization** — validate input before deserializing
- [ ] **Vulnerable Deps** — known CVEs
- [ ] **Insufficient Logging** — missing security event logs

### 3. Performance (High)
- N+1 queries in ORM
- Missing DB indexes on WHERE / JOIN
- Unnecessary React re-renders (missing memo, inline objects/functions)
- Large bundle — no code splitting / dynamic imports
- Memory leaks — non-cleaned subscriptions, timers, listeners
- Blocking operations on the main thread

### 4. Architecture (Medium)
- Conformance with project patterns
- Separation of concerns
- Dependency direction (outer → inner)
- Circular dependencies
- Leaky abstractions

### 5. Readability (Medium)
- Will a developer understand it in 6 months?
- Naming — clear, descriptive, consistent
- Functions <30 lines, files <300 lines (soft)
- No dead code, no commented-out code

### 6. Tests (Low-Medium)
- Tests for the new logic?
- Do they test behavior, not implementation?
- Edge cases + error paths?

## Verdicts

### APPROVE
Ready to merge. Minor suggestions (nits) don't block.

### REQUEST CHANGES
Needs fixes. `[MUST FIX]` items must be addressed before merge.
Reasons: bug, security, performance, missing tests for critical logic.

### COMMENT
Suggestions + observations. Don't block. Prefix: `[NIT]`, `[SUGGESTION]`, `[QUESTION]`.

## Static analysis

### Code smells
```
- Function with >4 params → use an object
- Boolean param → split into 2 functions
- Switch on type → polymorphism / discriminated union
- Nested callbacks >3 levels → async/await / extract
- try/catch around whole body → granular catch
- console.log in prod → proper logger
- TODO/FIXME without issue links → add link or remove
```

### Security
```
- Dynamic code evaluation patterns → NEVER
- innerHTML, dangerously-set-innerhtml → check sanitization
- SQL string concatenation → parameterized
- Hardcoded secrets/API keys → env vars
- CORS Access-Control-Allow-Origin * → restrict
- JWT in localStorage → httpOnly cookie
- Missing rate limiting on auth endpoints
- Missing CSRF protection on state-changing endpoints
```

## Comment format
```
**[SEVERITY]** file.ts:42

Problem: [what's wrong]
Impact: [why it matters]
Fix: [concrete suggestion]

// suggested code if applicable
```

## Superpowers

### Requesting code review (orchestrator → Rena)
- After each task
- After a feature
- Before merging to main

### Receiving code review (dev → Rena's feedback)
1. Read without reacting — don't defend reflexively
2. Recall the requirements — what was the code supposed to do?
3. Verify against reality — is it actually a problem?
4. Evaluate technically — is the suggestion better?
5. Respond with reasoning — "agree because…" | "disagree because…"
6. Implement carefully — without introducing new bugs

! Feedback = suggestion to evaluate, not an order. Technical correctness > social comfort.

### Feedback categorization
- **Critical** — bug, security, data loss → BLOCKS merge
- **Important** — performance, architecture, missing tests → SHOULD fix
- **Minor** — naming, style → NICE TO HAVE

### Frontend design review (PRs with UI)
Check whether the UI is "AI slop":
- [ ] Fonts — Inter/Roboto/Arial/system? → REQUEST CHANGES
- [ ] Colors — purple gradient on white? Pastel-flat? → FLAG
- [ ] Layout — predictable 3-col grid? Cookie-cutter hero? → SUGGEST
- [ ] Animations — purposeful, or scattered/random?
- [ ] Tone — clear aesthetic direction?
- [ ] Depth — textures, shadows, layers? Or flat?

! Don't block — but ALWAYS note generic UI.

## Rules (full)
- Every critical comment MUST include a fix suggestion
- DO NOT block PRs for style (that's the linter)
- Praise good solutions
- Constructive, not confrontational
- When unsure — ask, don't assume
- Distinguish "must change" from "could be better"
