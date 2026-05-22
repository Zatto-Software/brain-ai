---
id: agent-borys-developer-reference
type: reference
v: 1
tags: [reference, dev, fullstack, tdd, react, trpc]
refs: ["@agent:borys-developer", "@shared:PATTERNS"]
updated: 2026-05-22
---

# Borys — REFERENCE (deep dive)

Deep methods, snippets, deliverables — extracted from SKILL.md (progressive disclosure).

## Stack — details

### FE
- React 19 / Next.js 15 — App Router, Server Components, Server Actions
- TS strict, generics, utility types
- Tailwind v4, shadcn/ui + Radix, Framer Motion
- Zustand / TanStack Query

### BE
- Node — Express, Fastify, Hono
- tRPC e2e typesafe
- Python — FastAPI, Django, Flask
- Go — net/http, chi, gin

### DB
- Prisma / Drizzle (typesafe ORM, migrations)
- PostgreSQL — query, indexes, CTE, window
- Redis — cache, sessions, pub/sub, rate limit
- MongoDB — document modeling, aggregation

### Tools
- Git + conventional commits, feature branches, rebase
- Docker multi-stage, compose, dev containers
- Vitest / Jest (unit + mock)
- Playwright (E2E)

## Rules — full list

### Before writing
1. Read before Edit. Always.
2. Understand conventions (naming, structure, patterns).
3. Minimal change. Don't refactor the surroundings.
4. Check whether a solution already exists in the codebase.

### While writing
- KISS — simplest that works
- DRY — not at all costs. 3× repetition OK.
- YAGNI — don't build for "maybe later"
- Naming > comments
- Types > tests > comments
- Error handling only at boundaries (user input, ext API)

### Patterns ✓
- Composition > inheritance
- Early returns > nested if
- Discriminated unions > boolean flags
- `const` default, `let` only when mutating
- Optional chaining, nullish coalescing
- Barrel exports via `index.ts`

### Anti-patterns ✗
- `any` in TS (use `unknown` + type guard)
- Mutable global state
- God components (>200 lines)
- Prop drilling (use context / zustand)
- String-based enums (use `as const`)
- Premature optimization
- Magic numbers / strings

## Commits
```
feat: new functionality
fix:  bug
refactor: no behavior change
chore: tooling, config
docs: docs
test: tests
```

## React

### Component
```tsx
export function UserCard({ name, email }: UserCardProps) {
  const [isOpen, setIsOpen] = useState(false)
  if (!name) return null
  return (...)
}
```

### Custom hook
Extract when: used in >1 component OR the component becomes hard to read.

### Server Components (Next.js)
- Default = Server Component
- `'use client'` ONLY for: useState/useEffect/event handlers/browser API
- Data fetching in Server Components, not useEffect
- Streaming with Suspense boundaries

## API (tRPC)
```typescript
export const userRouter = router({
  getById: publicProcedure
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ input, ctx }) => {
      return ctx.db.user.findUniqueOrThrow({ where: { id: input.id } })
    }),
  create: protectedProcedure
    .input(createUserSchema)
    .mutation(async ({ input, ctx }) => {
      return ctx.db.user.create({ data: input })
    }),
})
```

## Superpowers

### TDD (default mode)
@shared:PATTERNS#tdd — RED → GREEN → REFACTOR → REPEAT.
! ZERO production code without a failing test.

### Systematic Debugging
@shared:PATTERNS#debugging — INVESTIGATE → HYPOTHESIS → TEST → FIX → VERIFY.
! ZERO fixes without root cause.
! 3+ fixes not working → STOP, escalate to @agent:atlas-architect.

### Verification
- Run tests fresh (not from cache)
- Read the WHOLE output
- Facts: `47/47 passed`, not "should work"
- ! NEVER declare "done" without evidence

### SEO meta (Next.js)
```tsx
export const metadata: Metadata = {
  title: 'Page Title',
  description: 'Under 160 chars',
  openGraph: { title, description, images: [{ url: '/og.png', width: 1200, height: 630 }] },
  twitter: { card: 'summary_large_image', images: ['/twitter-card.png'] },
}
```
Assets → @agent:pixel-designer. Borys integrates.

## Deliverables
- Working + tested code
- Short description of what / why
- List of modified files
- Test results (pass/fail count)
- Known limits / TODO
