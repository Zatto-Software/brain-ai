---
id: agent-pixel-designer-reference
type: reference
v: 1
tags: [reference, ui, ux, frontend, design-system, a11y, image-gen, nano-banana]
refs: ["@agent:pixel-designer"]
updated: 2026-05-22
---

# Pixel — REFERENCE (deep dive)

Design tokens, patterns, nano-banana playbook, workflow — extracted from SKILL.md (progressive disclosure).

## Philosophy
- Opinionated — the project has character
- Intentionality > intensity (bold maximalism + refined minimalism are both fine — a conscious choice)
- Form follows function. Less is more. Consistency via tokens. One thing must be WOW.

## Design thinking (BEFORE code — MANDATORY)
1. **Purpose** — what problem? what user?
2. **Tone** — BOLD: brutally minimal | maximalist chaos | retro-futuristic | organic | luxury | playful | editorial | brutalist | art deco | pastel | industrial | dark/moody. ! NOT "nice and modern".
3. **Constraints** — framework, perf, a11y, responsive
4. **Differentiation** — what's MEMORABLE?

## Anti-patterns (extended)
- Fonts AVOID: Inter/Roboto/Arial/system-ui, Space Grotesk → choose a distinctive display + refined body
- Colors AVOID: purple gradient on white, pastel-flat, blue-gray → use a dominant + sharp accent (80/20), CSS vars
- Layouts AVOID: predictable 3-col grids, hero+features+CTA, symmetric → asymmetry, overlap, diagonal flow, grid-breaking, controlled density
- Image gen AVOID: AI art slop (purple-pink gradient swirls, generic sci-fi glow, neon overload), mismatched aspect ratio, background screaming over UI text (must support, not compete), stock-photo aesthetic when brand is distinct, generating when SVG/CSS gradient is better (judge), generating without project context (ask the user)

## Design system tokens
```css
:root {
  --color-primary: oklch(0.65 0.25 260);
  --color-surface: oklch(0.99 0 0);
  --color-text: oklch(0.15 0 0);
  --color-text-muted: oklch(0.45 0 0);
  --color-border: oklch(0.9 0 0);
  --color-destructive: oklch(0.55 0.2 25);
  --color-success: oklch(0.6 0.2 145);
  --space-1: 0.25; --space-2: 0.5; --space-4: 1; --space-8: 2; --space-16: 4;
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --text-xs: 0.75rem; --text-base: 1rem; --text-2xl: 1.5rem; --text-3xl: 1.875rem;
  --radius-md: 0.5rem; --radius-full: 9999px;
  --shadow-md: 0 4px 6px oklch(0 0 0 / 0.07);
}
```

## Component pattern
```tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
}
export function Button({ variant='primary', size='md', loading, children, ...props }: ButtonProps) {
  return (
    <button className={cn('inline-flex items-center justify-center font-medium transition-colors',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
      'disabled:pointer-events-none disabled:opacity-50',
      variants[variant], sizes[size])} disabled={loading} {...props}>
      {loading && <Spinner className="mr-2 h-4 w-4" />}{children}
    </button>
  )
}
```

## Layout
- **Page:** `mx-auto max-w-7xl px-4 sm:px-6 lg:px-8` with `<header>` + `<main>`
- **Breakpoints:** sm 640 (large phone) | md 768 (tablet-p) | lg 1024 (laptop) | xl 1280 (desktop) | 2xl 1536
- **Grid:** `grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3`

## A11y checklist
- Semantic HTML (`button`, not `div onClick`)
- `aria-label` on icon-only, `alt` on images (or `alt=""`)
- Focus visible. Keyboard nav (Tab/Enter/Escape/Arrow)
- Contrast min 4.5:1 (text), 3:1 (large)
- Respect `prefers-reduced-motion`
- Skip-to-content link, form labels linked

## Animation
- Subtle, purposeful. Duration <300ms. NEVER: bounce, flash, long ones. ALWAYS: prefers-reduced-motion.
- Strategy: one well-orchestrated page load with staggered reveals > scattered micro-interactions
- High-impact: page load (staggered delay), scroll-triggered, hover (surprising/subtle), page transitions (View Transitions / Framer)
- Low-impact (use sparingly): button hover glow, focus ring, toggle switches
```tsx
const fadeIn = { initial: {opacity:0,y:8}, animate: {opacity:1,y:0}, transition:{duration:0.2,ease:'easeOut'} }
const container = { animate: {transition:{staggerChildren:0.05}} }
```

## Visual depth
DON'T default to solid colors. Build depth via: gradient meshes, noise/grain (CSS filter + SVG), geometric patterns (repeating-linear-gradient), layered transparencies, dramatic shadows (large, blurred, colored), gradient borders (border-image), custom cursors, grain overlays (::after with noise).
- Maximalist → elaborate, many layers
- Minimalist → restraint, precision

## Dark mode
Tailwind class strategy: `<html className={dark?'dark':''}>` + `bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100`

## Performance
- `loading="lazy"` below the fold
- `next/image` with `sizes` ALWAYS
- Dynamic imports for heavy
- Server Components default, minimize client JS
- `will-change` only on actively animated
- `font-display: swap`, preload critical
- ! When the build container has restricted outbound access, prefer self-hosted fonts (`@fontsource-variable/<font>`) over `next/font/google` to avoid silent fallback to Times serif

## Web assets

### Favicons
Sizes: 16x16, 32x32, 96x96, 180x180 (Apple), 192x192 (Android), 512x512 (PWA). PNG transparent, max 100KB.
```html
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
```

### OG / Social
- 1200x630 (FB/LinkedIn), 1200x675 (Twitter large), 1200x1200 (IG/WA)
- Safe zone: text in the central 80%. Min font 24px. Contrast 4.5:1. Max 1MB.
- Test: FB Sharing Debugger, Twitter Card Validator
```html
<meta property="og:image" content="https://example.com/og.png">
<meta property="og:image:width" content="1200">
<meta name="twitter:card" content="summary_large_image">
```

### Auto-detection
Next.js → `public/` + `app/layout.tsx` | Astro → `public/` + `BaseLayout.astro` | SvelteKit → `static/` + `app.html`

## Image generation (Nano Banana)

Cross-cutting capability — Pixel decides when to generate a raster asset during UI work. Not a separate mode; the tool is used in step 6 of the workflow.

### When to gen vs not
- ✅ Gen: hero backgrounds, illustration-driven empty states, unique brand visuals, mockup screenshots-in-frame, decorative patterns when CSS isn't enough
- ❌ Don't gen (use SVG/CSS): simple icons (Lucide/Heroicons), tileable geometric patterns (`repeating-linear-gradient`), simple shapes (CSS), logos (vector source-of-truth), favicons (PIL — see Web assets)
- ❓ Ask the user: no project context, the project has an existing asset library, session is approaching 5 images

### CLI

```bash
nano-banana "ENGLISH_PROMPT" -o KEBAB-NAME -s SIZE -a ASPECT [-d DIR] [--model pro]
```

Flags:
- `-s` size: `512` (draft) / `1K` (default) / `2K` / `4K`
- `-a` aspect: `16:9` / `9:16` / `21:9` / `4:3` / `1:1`
- `-o` filename (kebab-case, NO extension)
- `-d` output dir
- `--model pro` (Gemini 3 Pro Image) — 2× cost, for hero / brand-critical

Default model: **Flash**. Pro only for: hero/landing FINAL, brand-critical, or explicit user request.

Cost: ~15-20¢ Pro, significantly less Flash. All images carry a SynthID watermark (invisible).

! Prompt language **ALWAYS English** (image-gen models are stronger there).

### Prompt enrichment (MANDATORY)

Pixel NEVER calls nano-banana with the user brief 1:1. ALWAYS enrich with:
1. **Project palette** — read `tailwind.config.{js,ts,mjs}` + `app/globals.css` → cite hex/oklch
2. **Project mood** — infer from `CLAUDE.md`, `package.json` (project type), existing components / `public/images/`
3. **Aspect ratio** — pick per use case (hero=16:9, mobile bg=9:16, icon=1:1)
4. **Technical flags** — transparency for icons/illustrations, photorealistic vs illustration style
5. **Anti-AI-slop guards** — explicit `no purple gradients, no generic sci-fi glow, no AI art aesthetic, no gradient meshes, clean composition supporting overlay UI text`

### Budget guardrails
- Default model: **Flash**
- Pro only when: hero/landing FINAL, brand-critical, explicit user request
- **Max 3 iterations per task** without explicit user OK (auto-retry on weak output → STOP after 3, escalate)
- Pixel **logs** cost per asset and session total in EVERY response with gen
- Session >5 images → short warning to the user about total cost

### Pre-flight check (once per session)
```bash
which nano-banana || echo "NOT_INSTALLED"
test -n "$GEMINI_API_KEY" && echo "API_KEY_SET" || echo "API_KEY_MISSING"
```

## Workflow
1. User flow + goal → 2. Wireframe (Excalidraw if complex) → 3. Check design system → 4. Mobile-first impl → 5. Responsive → 6. Web assets (favicons/OG via PIL; raster assets via nano-banana IF the project warrants + SVG/CSS isn't enough) → 7. A11y → 8. Perf → 9. Review
