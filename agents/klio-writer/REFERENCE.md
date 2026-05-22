---
id: agent-klio-writer-reference
type: reference
v: 1
tags: [reference, writing, docs, content, seo, ui-copy]
refs: ["@agent:klio-writer", "@agent:pixel-designer", "@agent:atlas-architect", "@agent:nika-analyst"]
updated: 2026-05-22
---

# Klio — REFERENCE (deep dive)

Templates, snippets, patterns — extracted from SKILL.md (progressive disclosure).

## Languages
- **Local** — internal docs, UI copy for local products
- **EN** — README, API docs, OSS, international

## 1. Technical doc structure

```
docs/
  getting-started.md      # quick start <5 min
  guides/{auth,deployment}.md
  reference/{api,config}.md
  architecture/{overview,adr/}.md
  contributing.md
```

! Quick start <5 min to a working example. Code copy-paste-runnable. Up to date (outdated > missing). Searchable headings.

## 2. README template

```markdown
# Project Name
One-line desc + audience.

## Features
- Feature 1 — benefit

## Quick Start
\`\`\`bash
npm install && cp .env.example .env && npm run dev
\`\`\`

## Tech Stack
- Next.js 15 — React framework
- PostgreSQL — DB
- Tailwind — styling

## Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | Postgres conn | Yes |
| NEXTAUTH_SECRET | Session encryption | Yes |

## Deployment | ## License MIT
```

## 3. Changelog

```markdown
## [1.2.0] - 2026-04-01
### Added | Changed | Fixed | Security
- ...
```

## 4. Tech docs (HTML, self-contained)

When: "create API docs", "generate tech docs".
Structure: Overview → Getting Started → API Ref → Code Examples → Architecture (SVG inline) → Workflows.

```html
<!DOCTYPE html><html><head><title>[System] Documentation</title>
<style>
  body { font-family: system-ui; max-width: 1000px; margin: 0 auto; padding: 20px; }
  pre { background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 4px; overflow-x: auto; }
  .endpoint { background: #f7fafc; padding: 15px; margin: 10px 0; border-left: 4px solid #4299e1; }
  code { background: #e2e8f0; padding: 2px 6px; border-radius: 3px; }
</style></head><body><!-- sections --></body></html>
```

API endpoint pattern:
```html
<div class="endpoint">
  <h3><span style="color:#48bb78;">GET</span> /api/users/{id}</h3>
  <p>Retrieve user by ID</p>
  <pre><code>curl -X GET https://api.example.com/users/123</code></pre>
</div>
```

HTTP method colors: GET `#48bb78` | POST `#4299e1` | PUT/PATCH `#ecc94b` | DELETE `#f56565`

! Self-contained (zero CDN/fonts). Responsive. WCAG AA (contrast 4.5:1). File: `[system]-docs.html`.

## 5. UI copy patterns

- **Buttons:** verb + context (Save, Send, Add project). Destructive → "Delete project" + confirm.
- **Error:** What happened + what to do. BAD "Error 500" → GOOD "Could not save. Check your connection and try again."
- **Empty:** BAD "No data" → GOOD "You don't have any projects yet. Create your first to get started." [Create]
- **Loading:** "Loading projects..." (with text, not just a spinner)
- **Success:** "Project created" toast auto-dismiss 3s

## 6. Landing

Hero (Headline 5-8w + Sub 1-2 sent + CTA) → Problem → Solution → Features (3-5 + benefit) → Social proof → CTA.
Headline: [Action] + [Object] + [Benefit] — "Manage projects without chaos", "Deploy in 30s, not 30min".

## 7. Social / OG (CONTENT — designer handles the visual)

OG text: headline 5-8w max, subline 15w max, font min 24px, contrast 4.5:1. Test FB Debugger, Twitter Validator.

Per-page:
- Blog "[Title]" + logo
- Product "[Feature]" + screenshot
- Landing "[Value prop]" + CTA
- Profile "[Name] — [tagline]"

Alt text: descriptive. GOOD "Screenshot of dashboard with a sales chart" | BAD "App dashboard best trading platform".

## 8. SEO

- **On-page**: title <60ch (keyword first), meta desc <160ch (+CTA), 1× H1 (match title), descriptive alt, internal links.
- **Technical**: canonical URLs, OG tags, JSON-LD, sitemap.xml, robots.txt.

## Tone

Competent | Direct (no corporate blah) | Friendly (not infantile) | Technical (when audience is devs).

! Avoid: "innovative/revolutionary/best" (empty). Passive voice ("The project was created" → "You created the project"). Sentences >20 words. Jargon without context.

## PM toolkit (`skills/pm-toolkit/`)

| Skill | Description |
|-------|-------------|
| grammar-check | proofreading |
| draft-nda | NDA draft |
| privacy-policy | privacy policy generator |
| review-resume | resume review |
