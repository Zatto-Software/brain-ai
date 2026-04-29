---
type: index
tags: [lookup]
updated: 2026-04-29
---

# INDEX — flat lookup

## Hosts

| Host | Role | Notes |
|------|------|-------|
| api.example.com | API gateway prod | Behind CloudFront |
| api.staging.example.com | API gateway staging | Same VPC as prod |
| db.internal.example.com | Postgres primary | RDS, multi-AZ |
| db-read.internal.example.com | Postgres read replica | Single replica, eu-west-1 |

## Services → Repo

| Service | Repo | Owner |
|---------|------|-------|
| api-gateway | `org/api-gateway` | Platform team |
| service-a | `org/service-a` | Backend team |
| service-b | `org/service-b` | Backend team |
| ... | ... | ... |

## Common ports

- API gateway: 8080 (local), 443 (everywhere else)
- Postgres: 5432
- Redis: 6379
- Prometheus: 9090

## Access

- SSH bastion: `ssh ops@bastion.example.com` (key: `~/.ssh/id_ed25519_work`)
- AWS console: SSO via `https://example.awsapps.com`
- Grafana: `https://grafana.example.com` (Okta SSO)

## Paths

- Memory: `~/.claude/projects/example-team/memory/`
- Brain: `~/AI-Brain/`
- Decisions: `~/AI-Brain/Decisions/`

## Workflows

- Deploy: `make deploy-staging` → smoke test → `make deploy-prod`
- Migration: `make migrate-up` (uses `DATABASE_URL`)
- Rollback: `make deploy-prod-rollback VERSION=<n-1>`
