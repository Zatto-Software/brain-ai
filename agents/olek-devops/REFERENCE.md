---
id: agent-olek-devops-reference
type: reference
v: 1
tags: [reference, infra, devops, docker, cicd, monitoring]
refs: ["@agent:olek-devops"]
updated: 2026-05-22
---

# Olek — REFERENCE (deep dive)

Methods, templates, runbooks — extracted from SKILL.md (progressive disclosure).

## Typical platform (self-hosted example)
- Dokploy (PaaS), Forgejo or Gitea (git+CI), MinIO (S3), Harbor (registry), Traefik (reverse proxy + TLS)
- Proxmox or bare-metal cluster: prod-primary / prod-secondary / test-dev

! Map specific hosts/IPs in your private `infra.json` (do NOT hardcode in SKILL).

## Docker

### Dockerfile multi-stage
```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

### Compose (with healthcheck + limits)
```yaml
services:
  app:
    build: .
    restart: unless-stopped
    env_file: .env
    ports: ["${PORT:-3000}:3000"]
    depends_on:
      db: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy: { resources: { limits: { memory: 512M } } }
  db:
    image: postgres:17-alpine
    restart: unless-stopped
    volumes: [pgdata:/var/lib/postgresql/data]
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
volumes: { pgdata: }
```

## CI/CD (Forgejo / Gitea Actions, GitHub-compatible)
```yaml
name: CI/CD
on: { push: { branches: [main] }, pull_request: { branches: [main] } }
jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run lint && npm run typecheck && npm run test
  build:
    needs: lint-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          docker build -t $REGISTRY/$IMAGE:${{ github.sha }} .
          docker push $REGISTRY/$IMAGE:${{ github.sha }}
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: |
          curl -X POST "$DOKPLOY_URL/api/application.deploy" \
            -H "Authorization: Bearer $DOKPLOY_TOKEN" \
            -d '{"applicationId": "$APP_ID"}'
```

## Monitoring

Prometheus → AlertManager → Slack/email. Grafana dashboards. Loki + Promtail (logs). cAdvisor + node_exporter (metrics).

### Key alerts
```yaml
- alert: HighCPU
  expr: rate(process_cpu_seconds_total[5m]) > 0.8
  for: 5m
- alert: DiskSpaceLow
  expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
  for: 5m
- alert: ContainerDown
  expr: absent(container_last_seen{name="app"})
  for: 1m
- alert: HighMemory
  expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
  for: 5m
```

## Backup
- DB: `pg_dump` daily → MinIO, retain 30d
- Volumes: restic → MinIO, retain 14d
- Configs: git (this repo)
- Secrets: separate encrypted backup
- Test: monthly restore drill

## Deploy checklist
- [ ] CI tests pass
- [ ] Build clean
- [ ] DB backup pre-deploy
- [ ] Test deploy + smoke
- [ ] Prod deploy
- [ ] Grafana metrics (5 min)
- [ ] Loki — errors?
- [ ] Rollback plan (previous image tag)

## File organization
1. ANALYSIS: `ls -la`, `find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn`, `du -sh */ | sort -rh | head -20`
2. DUPLICATES: `find . -type f -exec md5 {} \; | sort | uniq -d`
3. PLAN — current vs proposed, list of changes, decisions
4. EXECUTE after approval: `mkdir -p`, `mv`
5. REPORT

! Safety: ALWAYS ask before `rm`. Log every mv. Archive > delete. STOP on unexpected.

Naming: `YYYY-MM-DD-description.ext`, lowercase-with-hyphens, prefix `01-active`/`02-archive`. No spaces, no non-ASCII.

Structure: `project/{Active/, Archive/{2025/, 2026/}, Templates/}`

Maintenance: weekly (sort inbox) | monthly (review + archive) | quarterly (duplicates) | yearly (archive old)

## Troubleshooting
```bash
# Container won't start
docker logs <container> --tail 100
docker inspect <container> | jq '.[0].State'
# Port in use
ss -tlnp | grep <port>
# Disk full
df -h && docker system df
docker system prune -a --volumes  # ! removes unused
# DNS
dig <domain> @1.1.1.1
# SSL
openssl s_client -connect <host>:443 -servername <domain>
```
