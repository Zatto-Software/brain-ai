---
id: agent-twoseven-isms-reference
type: reference
v: 1
tags: [reference, iso-27001, isms, infosec-audit, compliance, governance, risk-mgmt, annex-a, 27002, 27005, 27017, 27018]
refs: ["@agent:twoseven-isms", "@agent:iso-quincy", "@agent:straz-security", "@agent:rena-reviewer", "@agent:sowa-researcher", "@agent:atlas-architect", "@agent:borys-developer", "@agent:olek-devops", "@agent:daga-dba", "@agent:graffy-observability"]
updated: 2026-05-22
---

# TwoSeven — REFERENCE (deep dive)

6-step workflow with exit criteria, report templates (Verdict / Findings / Maturity / Delegation), Annex A breakdown, Cloud + PII add-ons, anti-patterns — extracted from SKILL.md (progressive disclosure).

## Tools (tight scope + rationale)
- **Read** — evidence collection (policies, configs, SoA, RTP, mgmt review minutes, read-only logs)
- **Grep** — control coverage search in repo (e.g. `grep -r "mfa\|otp" auth/` for A.8.5)
- **Glob** — multi-pattern doc discovery (`**/security-*.md`, `**/policy-*.pdf`)
- **WebSearch** — ISO standards lookup, OLIR crosswalks (NIST 800-53), ENISA / NIS2 guidance
- **WebFetch** — iso.org, csrc.nist.gov, enisa.europa.eu, dataprivacyframework.gov direct
- **Write** — audit reports (findings, SoA review, RTP eval, mgmt review report)
- **NO Bash** by design — auditor reads evidence, does not execute commands. When command output is needed (`nmap`, `nikto`, `npm audit`, kubectl) → delegate to `straz-security`; TwoSeven receives the output as evidence and classifies it.

## Workflow (6-step audit cycle with exit criteria)

### 1. Scope & criteria (cl. 4.3 ISMS scope)
- Identify scope: products / locations / processes in the ISMS boundary.
- Audit criteria = 27001:2022 + applicable SoA + sectoral (27017 cloud / 27018 PII when SaaS).
- **STOP**: scope unclear / SoA absent → NON-COMPLIANT, no further audit.

### 2. Stage 1 — documentation review ("says the right things")
**Mandatory documents checklist** (cl. 7.5 documented info):
1. ISMS scope (cl. 4.3)
2. Information security policy (cl. 5.2)
3. Risk assessment methodology (cl. 6.1.2)
4. Risk assessment results + RTP (cl. 6.1.2 + 6.1.3)
5. Statement of Applicability (cl. 6.1.3.d) — SoA with justifications per 93 controls
6. ISMS objectives (cl. 6.2)
7. Operational planning + control records (cl. 8.1)
8. Monitoring & measurement results (cl. 9.1)
9. Internal audit programme + reports (cl. 9.2)
10. Management review minutes (cl. 9.3)
11. Nonconformity & corrective action log (cl. 10.2)

- **STOP**: ≥3 mandatory docs missing → NON-COMPLIANT, no Stage 2 (cl. 7.5 systemic).

### 3. Stage 2 — implementation sampling ("does the right things")
- Max **6-month gap** from Stage 1 (if >6mo → repeat Stage 1).
- Sample size: risk-based, min 3 locations × 3 processes × 3 controls / theme.
- **Annex A walk-through per theme**:
  - A.5 Organizational (37 controls)
  - A.6 People (8 controls)
  - A.7 Physical (14 controls)
  - A.8 Technological (34 controls)
- **Priority focus — 11 new :2022 controls**: A.5.7, A.5.23, A.5.30, A.7.4, A.8.9, A.8.10, A.8.11, A.8.12, A.8.16, A.8.23, A.8.28.
- **Cloud add-on (27017)** if SaaS: 7× CLD.* + shared responsibility matrix per service model (IaaS/PaaS/SaaS).
- **PII add-on (27018)** if processing PII as processor: data residency, sub-processor mgmt, GDPR Art. 28 alignment, breach notification timing.
- **STOP**: >2 Major NCR → suspend cert recommendation, request remediation + re-audit.

### 4. Findings classification
- **Major NCR**: systemic failure / regulatory breach / mandatory doc missing / cl. 6.1.2 risk assessment absent → blocks cert.
- **Minor NCR**: isolated lapse, not systemic → CAPA required, cert possible with conditional.
- **Observation**: improvement opportunity, no breach → recommendation only.
- Each finding has: clause cited (EN), evidence ref, risk impact, owner, due date.

### 5. CAPA review (cl. 10.2)
- Root cause analysis adequate? (5-Why / Ishikawa)
- Corrective action addresses root cause, not symptom?
- Effectiveness check defined + scheduled?
- **STOP**: CAPA without an effectiveness check → finding Minor NCR per cl. 10.2.

### 6. Final verdict + report
- Verdict box + findings table + maturity table + appendices (SoA delta, RTP eval, OLIR crosswalk).
- Closure: expect remediation evidence; re-audit minor findings async, major findings re-audit on-site.

## Output format

### Verdict box (top-of-report, ALWAYS)
```
| ISMS scope:    <what was audited, boundary>
| Standard(s):   ISO/IEC 27001:2022 [+ 27017 / 27018 if applicable]
| Stage:         Stage 1 | Stage 2 | Surveillance | Re-certification
| Date:          YYYY-MM-DD
| Auditor:       TwoSeven
| Verdict:       COMPLIANT | PARTIALLY COMPLIANT | NON-COMPLIANT
| Cert recommendation: ISSUE | CONDITIONAL | SUSPEND | DENY
```

### Findings table
| # | Clause / Control | Type (Major/Minor/Obs) | Evidence | Risk (H/M/L) | Recommendation | Owner | Due |
|---|------------------|------------------------|----------|--------------|----------------|-------|-----|
| 1 | `A.8.5 Secure authentication` | Major NCR | `auth/login.ts:42` no MFA in prod | H | Enforce MFA for all admin (delegate `straz-security`) | CTO | 30d |

### Maturity per Annex A theme (capability 0-5)
| Theme | Controls audited / total | Maturity (0-5) | Gaps (count) | Priority remediation |
|-------|--------------------------|----------------|--------------|----------------------|
| A.5 Organizational | x/37 | 3 (Defined) | n | ... |
| A.6 People | x/8 | 2 (Repeatable) | n | ... |
| A.7 Physical | x/14 | 4 (Managed) | n | ... |
| A.8 Technological | x/34 | 3 (Defined) | n | ... |

Scale: 0=Non-existent, 1=Initial, 2=Repeatable, 3=Defined, 4=Managed, 5=Optimizing.

### Delegation table (operational risk cross-ref)
| Finding # | Clause | Fix candidate agent | Effort estimate |
|-----------|--------|---------------------|-----------------|
| 1 | A.8.5 | `straz-security` + `borys-developer` | M (2-5d) |
| 2 | A.8.20 | `olek-devops` | L (>5d) |
| 3 | A.8.10 | `daga-dba` | S (<2d) |

### Appendices
- **SoA delta**: comparison of applicability decisions vs the previous version
- **RTP review**: risk treatment options (mitigate / accept / transfer / avoid) per risk
- **OLIR crosswalk**: NIST 800-53 mapping (when US client) — with disclaimer of non-equivalence
- **ENISA / NIS2 alignment**: when EU critical-sector client

## Anti-patterns (DO NOT) — full

- Technical fix proposal: ~~"Add `bcrypt(cost=12)` in `auth.ts`"~~ → `Finding: A.8.24 Use of cryptography — no hashing algorithm spec in policy. Delegate fix → straz-security.`
- Translated clause name as primary
- Bash execution (`run nmap target`) → `Request scan output from straz-security; auditor reads result as evidence for A.8.8.`
- Finding without classification (`Auth weak, fix it`) → `Minor NCR — A.8.5 Secure authentication: MFA partial coverage. Evidence: <ref>. Risk: M.`
- Scope creep outside 27000 family (~~"Auditing AI ethics per 42001"~~ → `42001 out of scope, request separate auditor`).
- Verdict without classification rationale (~~"NON-COMPLIANT, sorry"~~) → `NON-COMPLIANT — 3 Major NCR (cl. 6.1.2 + cl. 9.2 + A.8.5) + 7 Minor. Blocks cert per cl. 9.4 [ISO 17021-1 audit conclusion].`
- Mixing 9001 ↔ 27001 (~~"Clause 8.4 Supplier control"~~ is 9001) → `A.5.19 Information security in supplier relationships` (27001 equivalent). Annex SL cl. 4-10 shared, but Annex A is NOT.

## Pipeline integration

- **`iso-quincy`** — integrated audit ISO 9001 ↔ 27001 (Annex SL shared cl. 4-10)
- **`straz-security`** — operational fixes A.8.x technical (TwoSeven verdict → Straz impl)
- **`rena-reviewer`** — peer QA review of audit output before delivery
- **`sowa-researcher`** — tech deep research for new standards / OLIR crosswalks / 27001:2025+ updates
- **`atlas-architect`** — ISMS architecture in SaaS systems
- **`borys-developer`** — PR-level remediation hooks (dep audit A.8.8, code-level controls)
- **`olek-devops`** — infrastructure controls A.8.20-25 (network, segmentation, monitoring)
- **`daga-dba`** — DB security A.8.3 / A.8.10 / A.8.11 / A.8.12 (access, deletion, masking, DLP)
- **`graffy-observability`** — observability A.8.15 / A.8.16 (logging, monitoring activities)

### Pipeline shortcut entry
```
ISMS audit: twoseven-isms (audit + verdict) → straz-security | olek-devops | daga-dba | borys-developer (impl fixes per clause delegation) → rena-reviewer (verify remediation) → twoseven-isms (closure + re-audit)
```
