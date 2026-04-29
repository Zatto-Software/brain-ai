---
name: Q2 platform migration
description: ECS → Fargate migration, deadline 2026-06-30
type: project
---

Migrating all 12 services from ECS (EC2-backed) to Fargate. Deadline: **2026-06-30**.

## Pending
- [ ] Service A — health check tuning
- [ ] Service B — IAM role consolidation
- [ ] Service C — secrets via Parameter Store
- [ ] Cost review — Fargate spot integration

## Done (recent)
- 2026-04-15: First 8 services migrated, no incidents
- 2026-04-20: Cost analysis baseline established

**Why:** Reducing on-call burden — the EC2 fleet's patching cycle has caused 4 incidents in the last 6 months.
**How to apply:** When suggesting infra changes, prefer Fargate-compatible patterns. Flag any change that would re-introduce EC2 dependencies.

<!-- When all pending items are done: archive to Decisions/2026-XX-XX-q2-migration.md -->
