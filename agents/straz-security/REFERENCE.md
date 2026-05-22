---
id: agent-straz-security-reference
type: reference
v: 1
tags: [reference, security, owasp, audit, hardening]
refs: ["@agent:straz-security", "@agent:rena-reviewer", "@agent:borys-developer", "@agent:olek-devops"]
updated: 2026-05-22
---

# Straz — REFERENCE (deep dive)

OWASP Top 10 breakdown, audit checklists, external repo workflow, report templates — extracted from SKILL.md (progressive disclosure).

## OWASP Top 10 (2025)

### A01: Broken Access Control
Attacks: IDOR, privilege escalation, CORS misconfig, forced browsing.
Defense: deny by default (whitelist), authz on EVERY endpoint (not just UI), don't trust client side, row-level security in DB, audit log permissions.
Test: change ID in URL/body → other people's data? remove token → 401? change role in JWT → server checks DB?

### A02: Cryptographic Failures
Defense: TLS+HSTS, bcrypt(cost=12) / argon2id, secrets in env/vault NEVER in code, encryption at rest for PII, rotate keys.
Test: `grep -r "password\|secret\|key\|token" --include="*.{ts,js,py,env}"`, SSL Labs, hash type check.

### A03: Injection (SQL/NoSQL/command/LDAP)
Defense: parameterized queries ALWAYS, ORM bindings (Prisma/Drizzle), input validation (zod/joi) on EVERY input, no dynamic eval, Content-Type validation.
Test: `'1; DROP TABLE users; --'`, `{"$gt": ""}` Mongo, `; ls -la` in command fields.

### A04: Insecure Design
Threat modeling BEFORE impl. Abuse cases alongside use cases. Rate limiting on auth. Business logic validation server-side.

### A05: Security Misconfiguration
Hardened defaults (no debug/verbose). Remove default creds. Security headers. Least privilege. Regular dep updates.
Headers checklist:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

### A06: Vulnerable Components
`npm audit` / `pip audit` regularly. Dependabot/Renovate. Lock files in repo. Minimal deps.
`npm audit --production`, `npx better-npm-audit audit`.

### A07: Auth Failures
MFA where possible. Account lockout after N. Session timeout (idle + absolute). Secure cookies (httpOnly + SameSite + Secure). Password policy + haveibeenpwned check. JWT: 15min access + 7d refresh, rotate refresh.

### A08: Data Integrity Failures
Verify signatures (updates / packages). CI/CD security (signed commits, protected branches). SRI for CDN scripts. Input deserialization validation.

### A09: Logging & Monitoring
Log: auth events, access control failures, input validation failures.
DON'T log: passwords, tokens, PII, credit cards.
Structured JSON → Loki/ELK. Alert on anomalies. Retain min 90d.
Format: `{"timestamp":"...","level":"warn","event":"auth_failure","ip":"...","path":"/api/login"}`

### A10: SSRF
Whitelist allowed URLs/domains. Block internal IPs (10/172.16/192.168/127). No server-side redirects. Validate schema (https only).

## Audit checklist

### Pre-deploy
- [ ] No secrets in code/git history
- [ ] Deps updated, no CVEs
- [ ] Security headers
- [ ] CORS restricted
- [ ] Rate limiting on auth endpoints
- [ ] Input validation everywhere
- [ ] Error messages don't leak internals
- [ ] HTTPS + HSTS

### Infrastructure
- [ ] SSH key-only
- [ ] Firewall — only needed ports
- [ ] Docker — non-root user, RO filesystem where possible
- [ ] Secrets in env/vault
- [ ] Backups encrypted
- [ ] OS + packages updated

### Code
- [ ] No dynamic eval with user input
- [ ] Parameterized queries
- [ ] Output encoding (XSS)
- [ ] CSRF protection
- [ ] File upload validation (type / size / name)
- [ ] No sensitive data in localStorage

## External repo audit
! MANDATORY when running code from a repo you don't own.

Checklist:
- Read EVERY .sh / .js / .py / .cmd / .ps1
- Look for: `eval`, `Function`, `exec`, `system`, `subprocess`, `child_process`
- Look for: `curl` / `fetch` / `axios` / `requests` to unknown URLs
- Look for: encoded/obfuscated (base64/hex/unicode escapes)
- Hooks (pre-commit, post-install, session-start)
- package.json scripts (postinstall/prepare/preinstall)
- Makefile/Dockerfile for hidden commands
- .github/workflows for secret exfil
- License (MIT/Apache OK, proprietary → warn)

! Red flags STOP: minified/obfuscated code (why are they hiding?), curl to IP instead of domain, env vars sent outbound, dynamic eval from user input/dynamic string, hidden files with exec (`.hidden.sh`), postinstall downloading binaries.

### Repo audit report
```markdown
## External Repo Audit: [owner/repo]
Date: YYYY-MM-DD | URL: [link] | Commit: [hash]

### Verdict: SAFE | SUSPICIOUS | DANGEROUS
### Files reviewed: [count]
### Executable code found: [list]
### External network calls: [list or NONE]
### Security concerns: [list or NONE]
### Recommendation: [use / use with caution / DO NOT USE]
```

## Audit report format
```markdown
## Security Audit: [scope]
Date: YYYY-MM-DD | Auditor: Security Agent

### Executive Summary
[1-2 sentences: overall posture]

### CRITICAL (fix NOW)
| # | Issue | Location | Impact | Fix |
### HIGH (fix this sprint)
### MEDIUM (plan fix)
### LOW (nice to have)
### Positive findings
### Recommendations
```
