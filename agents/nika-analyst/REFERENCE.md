---
id: agent-nika-analyst-reference
type: reference
v: 1
tags: [reference, ba, product, planning, plane, metrics]
refs: ["@agent:nika-analyst", "@agent:atlas-architect", "@agent:klio-writer"]
updated: 2026-05-22
---

# Nika — REFERENCE (deep dive)

Methods, templates, PM skills catalogue — extracted from SKILL.md (progressive disclosure).

## User stories

### Format
```markdown
## US-XXX: [Title]

**As a** [user type]
**I want** [what I want to do]
**So that** [what value I get]

### Acceptance Criteria
- [ ] GIVEN [context] WHEN [action] THEN [expected outcome]
- [ ] GIVEN [context] WHEN [action] THEN [expected outcome]

### Out of scope
- What is NOT part of this task

### Technical notes
- Notes for the developer (optional)

### Priority: high | medium | low
### Effort: S (1-2h) | M (3-8h) | L (1-3d) | XL (3-5d)
```

### Good user stories — INVEST
- **I**ndependent — standalone
- **N**egotiable — conversation, not contract
- **V**aluable — value to the user
- **E**stimable — can be estimated
- **S**mall — 1-3 days
- **T**estable — clear criteria

## Sprint planning

### Workflow (any tracker — Plane, Linear, GitHub Projects)
```
Backlog → Todo → In Progress → Done

Sprint cycle: 2 weeks
Sprint planning: start of sprint
Sprint review: end of sprint
```

### Prioritization (ICE score)
```
Impact (1-10) × Confidence (1-10) × Ease (1-10) = ICE Score
Sort descending, work from the top.
```

### Velocity tracking
```
Sprint 1: 15 story points done
Sprint 2: 18 story points done
Sprint 3: 16 story points done
Average velocity: ~16 SP / sprint
Next sprint capacity: 14-18 SP (plan 16)
```

## Roadmap

### Format
```markdown
## Q2 2026 Roadmap

### Theme: [overarching quarterly goal]

### Must have (P0)
- [ ] Feature A — [why now]
- [ ] Feature B — [why now]

### Should have (P1)
- [ ] Feature C
- [ ] Feature D

### Nice to have (P2)
- [ ] Feature E
- [ ] Feature F

### Success metrics
- KPI 1: [metric] from [X] to [Y]
- KPI 2: [metric] from [X] to [Y]
```

## Competitive analysis

### Framework
```markdown
## Competitive Analysis: [market/segment]

### Our product
- USP: [what makes us different]
- Target: [for whom]
- Pricing: [pricing model]

### Competitors

#### [Competitor 1]
- URL: ...
- Features: ...
- Pricing: ...
- Strengths: ...
- Weaknesses: ...
- Market position: ...

### Feature comparison matrix
| Feature        | Mine | Comp 1 | Comp 2 | Comp 3 |
|----------------|------|--------|--------|--------|
| Feature A      | +    | +      | -      | +      |
| Feature B      | +    | -      | +      | -      |
| Free tier      | +    | -      | +      | +      |

### Opportunities
- Gaps in market
- Underserved segments
- Unique advantages

### Threats
- Established players
- New entrants
- Substitute products
```

## Metrics

### SaaS metrics
```
MRR         — Monthly Recurring Revenue
Churn       — % users lost per month (<5% good)
CAC         — Customer Acquisition Cost
LTV         — Lifetime Value (LTV:CAC > 3:1)
NPS         — Net Promoter Score (>50 excellent)
DAU/MAU     — Stickiness ratio (>20% good)
Time to value — How fast user gets first win
```

### Product metrics
```
Activation  — % users completing onboarding
Retention   — % users returning after Day 1/7/30
Feature adoption — % users using feature X
Error rate  — % requests failing
Response time — p50, p95, p99 latency
```

## Process mapping

### Workflow
```
Trigger → Step 1 → Decision? → Yes → Step 2a → End
                             → No  → Step 2b → End
```

### RACI matrix
```
| Task           | CEO | CTO | Dev | Design | QA  |
|----------------|-----|-----|-----|--------|-----|
| Requirements   | A   | C   | I   | C      | I   |
| Architecture   | I   | A   | R   | C      | I   |
| Implementation | I   | C   | R   | C      | I   |
| Testing        | I   | I   | C   | I      | R   |
| Deploy         | I   | A   | R   | I      | C   |

R=Responsible A=Accountable C=Consulted I=Informed
```

## PM skills library
Product skills (recommended pack: `phuryn/pm-skills`, MIT). Each skill = a ready-to-use prompt with a template.

### Product Strategy (`skills/pm-product-strategy/`)
`product-vision`, `product-strategy`, `lean-canvas`, `startup-canvas`, `business-model`, `value-proposition`, `swot-analysis`, `pestle-analysis`, `ansoff-matrix`, `porters-five-forces`, `monetization-strategy`, `pricing-strategy`

### Product Discovery (`skills/pm-product-discovery/`)
`brainstorm-ideas-{new,existing}`, `brainstorm-experiments-{new,existing}`, `identify-assumptions-{new,existing}`, `prioritize-assumptions`, `prioritize-features`, `analyze-feature-requests`, `interview-script`, `summarize-interview`, `opportunity-solution-tree`, `metrics-dashboard`

### Execution (`skills/pm-execution/`)
`create-prd` (8 sections), `brainstorm-okrs`, `user-stories` (3 C's + INVEST), `job-stories` (JTBD), `sprint-plan`, `outcome-roadmap`, `stakeholder-map`, `pre-mortem`, `retro`, `release-notes`, `summarize-meeting`, `test-scenarios`, `prioritization-frameworks` (RICE, ICE, MoSCoW), `dummy-dataset`, `wwas`

### Market Research (`skills/pm-market-research/`)
`user-personas` (JTBD), `user-segmentation`, `market-segments`, `market-sizing` (TAM/SAM/SOM), `competitor-analysis`, `sentiment-analysis`, `customer-journey-map`

### Go-to-Market (`skills/pm-go-to-market/`)
`gtm-strategy`, `gtm-motions` (sales-led, product-led), `growth-loops`, `beachhead-segment`, `ideal-customer-profile` (ICP), `competitive-battlecard`

### Marketing & Growth (`skills/pm-marketing-growth/`)
`north-star-metric`, `marketing-ideas`, `value-prop-statements`, `product-name`, `positioning-ideas`

### Data Analytics (`skills/pm-data-analytics/`)
`sql-queries`, `cohort-analysis`, `ab-test-analysis`
