---
id: agent-sowa-researcher-reference
type: reference
v: 1
tags: [reference, research, analysis, adr, benchmark]
refs: ["@agent:sowa-researcher"]
updated: 2026-05-22
---

# Sowa — REFERENCE (deep dive)

Methods, templates, source tiering — extracted from SKILL.md (progressive disclosure).

## Methods

### 1. Tech scouting
Evaluation of new frameworks, libraries, tools.
```
Criteria:
- Maturity: age, version, API stability
- Adoption: GitHub stars, npm downloads, Fortune 500 usage
- Community: issue activity, response time, contributors
- Documentation: quality, examples, migration guides
- Performance: benchmarks, bundle size, memory footprint
- DX: developer experience, tooling, IDE support
- Lock-in risk: open source, standard-based, exit strategy
```

### 2. Competitive analysis
```
Framework:
- What is the competition doing? (features, pricing, UX)
- What tech stack? (BuiltWith, Wappalyzer, PageSpeed)
- Weak points? (reviews, complaints)
- How to differentiate?
- Industry trends?
```

### 3. Proof of concept
Quick prototype to validate.
```
PoC rules:
- Max 2-4h of work
- Validate ONE hypothesis
- Throwaway code — don't build prod
- Record conclusions regardless of outcome
- "Doesn't work" = equally valuable result
```

### 4. Benchmarking
```
- Realistic data (not lorem ipsum)
- Min 3 rounds, report medians
- Compare against baseline (current solution)
- Cold start vs warm
- Report conditions (hardware, OS, versions)
```

## Sources

### Primary (trusted)
- Official docs
- GitHub repo (issues, PRs, changelogs)
- RFC / specifications
- Benchmarks with reproducible code

### Secondary (verify)
- Author/maintainer blog posts
- Conference talks (≤12 months)
- Stack Overflow (highly upvoted)
- npm trends, bundlephobia

### Tertiary (handle with care)
- Medium / dev.to
- Reddit (signals, not facts)
- Twitter/X (opinions)
- ! AI-generated — verify EVERYTHING

## Reports

### Short (fast decision)
```markdown
## [Topic]

**Recommendation**: [Option X] because [1-2 sentences]

| Criterion | A | B | C |
|-----------|---|---|---|
| Maturity  | +++ | ++ | + |
| Perf      | ++ | +++ | ++ |
| DX        | +++ | + | ++ |

**Risks**: [main ones]
**Next step**: [what we do]
```

### Full (strategic)
```markdown
## Research Report: [Topic]
Date: YYYY-MM-DD
Author: Researcher

### Context
Why we're researching, what problem.

### Methodology
How, which sources, which criteria.

### Options

#### Option A: [name]
- Description: ...
- Pros: ...
- Cons: ...
- Costs: time to implement, learning curve, maintenance
- Usage examples: who and how

#### Option B: [name]
(same format)

### Comparison
| Criterion | Weight | A | B | C |
|-----------|--------|---|---|---|

### Recommendation
Choice + reasoning. Why not the others.

### Risks and mitigations
What could go wrong, how to prevent.

### Rollout plan
1. ...
2. ...

### Sources
- [link]
```

## ADR
```markdown
## ADR-XXX: [Title]

**Status**: proposed | accepted | deprecated | superseded by ADR-YYY
**Date**: YYYY-MM-DD
**Deciders**: [who]

### Context
Problem, constraints, requirements.

### Considered options
1. ...
2. ...

### Decision
What + WHY.

### Consequences
- Positive: ...
- Negative: ...
- Neutral: ...
```
