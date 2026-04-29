---
name: No mocks in integration tests
description: Integration tests must hit a real database, not mocks
type: feedback
---

Integration tests must use a real database (Docker container or test instance). Mocks are forbidden for the data layer.

**Why:** Q1 2025 incident — mocked tests passed in CI but the production migration failed because the mock didn't enforce the same constraints as Postgres. ~3 hours of downtime.

**How to apply:** Any test in `tests/integration/` MUST use the test DB container from `docker-compose.test.yml`. Unit tests in `tests/unit/` may use mocks for non-DB collaborators.
