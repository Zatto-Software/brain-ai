---
id: agent-teo-qa-reference
type: reference
v: 1
tags: [reference, qa, testing, tdd, vitest, playwright]
refs: ["@agent:teo-qa", "@shared:PATTERNS"]
updated: 2026-05-22
---

# Teo — REFERENCE (deep dive)

Methods, snippets, templates — extracted from SKILL.md (progressive disclosure).

## Philosophy

### The pyramid
```
        /  E2E  \        — few, expensive, slow
       / Integration \   — moderate, realistic
      /    Unit tests   \ — many, fast, isolated
```

### Rules
- Test behavior, not implementation — "user sees X", not "useState returns Y"
- Arrange-Act-Assert — clear structure
- One assertion per concept — test fails for one reason
- ! No flaky tests — deterministic, order-independent
- Real > mock — integration > mock-heavy unit when possible
- Edge cases > happy path — happy path is exercised by using the app

## Patterns

### Unit (Vitest)
```typescript
import { describe, it, expect } from 'vitest'

describe('calculateTotal', () => {
  it('sums items with tax', () => {
    const items = [
      { price: 100, quantity: 2 },
      { price: 50, quantity: 1 },
    ]
    expect(calculateTotal(items, { taxRate: 0.23 })).toBe(307.50)
  })

  it('returns 0 for empty cart', () => {
    expect(calculateTotal([], { taxRate: 0.23 })).toBe(0)
  })

  it('throws on negative quantity', () => {
    const items = [{ price: 100, quantity: -1 }]
    expect(() => calculateTotal(items)).toThrow('Invalid quantity')
  })
})
```

### Component (Testing Library)
```typescript
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

it('submits form with valid data', async () => {
  const onSubmit = vi.fn()
  render(<LoginForm onSubmit={onSubmit} />)

  await userEvent.type(screen.getByLabelText('Email'), 'test@example.com')
  await userEvent.type(screen.getByLabelText('Password'), 'secure123')
  await userEvent.click(screen.getByRole('button', { name: 'Log in' }))

  expect(onSubmit).toHaveBeenCalledWith({
    email: 'test@example.com',
    password: 'secure123',
  })
})
```

### E2E (Playwright)
```typescript
import { test, expect } from '@playwright/test'

test('user can create a new project', async ({ page }) => {
  await page.goto('/dashboard')
  await page.getByRole('button', { name: 'New Project' }).click()

  await page.getByLabel('Project name').fill('My Project')
  await page.getByLabel('Description').fill('Test project')
  await page.getByRole('button', { name: 'Create' }).click()

  await expect(page.getByText('My Project')).toBeVisible()
  await expect(page).toHaveURL(/\/projects\/[\w-]+/)
})
```

### API
```typescript
import { describe, it, expect } from 'vitest'
import request from 'supertest'
import { app } from '../src/app'

describe('POST /api/users', () => {
  it('creates user with valid data', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ email: 'new@test.com', name: 'Test User' })

    expect(res.status).toBe(201)
    expect(res.body).toMatchObject({
      email: 'new@test.com',
      name: 'Test User',
      id: expect.any(String),
    })
  })

  it('rejects duplicate email', async () => {
    await request(app).post('/api/users').send({ email: 'dup@test.com', name: 'First' })
    const res = await request(app).post('/api/users').send({ email: 'dup@test.com', name: 'Second' })

    expect(res.status).toBe(409)
  })
})
```

## Test plan
```markdown
## Test Plan: [Feature]

### Scope
What we test and why.

### Scenarios

#### Happy path
- [ ] [Scenario 1] — expected result
- [ ] [Scenario 2] — expected result

#### Edge cases
- [ ] Empty input
- [ ] Max length input
- [ ] Special characters
- [ ] Concurrent requests
- [ ] Network failure

#### Error paths
- [ ] Invalid input — show error
- [ ] Unauthorized — redirect to login
- [ ] Server error — fallback UI

### Environment
- Browser: Chromium, Firefox, WebKit
- Mobile: responsive (375px, 768px, 1280px)
- Auth: logged in / logged out / admin
```

## Bug report
```markdown
## BUG: [short description]

**Severity**: critical | high | medium | low
**Environment**: [browser, OS, URL]

### Steps to reproduce
1. ...
2. ...

### Expected
What should happen.

### Actual
What did happen (screenshot/video if possible).

### Additional context
Logs, network tab, console errors.
```

## Superpowers

### TDD — Red-Green-Refactor
Teo = guardian of the TDD cycle:
1. **RED** — failing test FIRST (1 assertion, 1 concept)
2. **GREEN** — minimal code to pass
3. **REFACTOR** — clean while keeping green
! Don't accept code without tests. Don't write tests after the fact.

### Verification before completion
- After a test run: read the WHOLE output
- Report FACTS: "42/42 passed, 0 failed, coverage 87%"
- ! NEVER: "tests passed" without running them
- Flaky test → fix it, don't ignore it

## Coverage
- Unit: >80% on business logic
- Integration: key flows covered
- E2E: top 5 user journeys
- ! Don't chase 100% — diminishing returns past 85%
