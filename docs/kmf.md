# KMF in practice

`KMF.md` (root) is the spec. This doc shows you how to actually use it.

## Why we needed KMF

The base AI-Brain framework gives you four memory types and an INDEX. That works until your brain has 100+ files. Symptoms we hit:

- Each agent SKILL.md grew to 200–400 lines (1.5–3k tokens per delegation)
- INDEX.md became a 100-line wall of prose tables — re-greppable, but the LLM read most of it every time
- Cross-file relationships were implicit ("see also Decisions/...") — the LLM had to infer them
- Generic markdown gave the LLM no machine-parsable surface; every lookup ended in `grep`

KMF converts the brain from "prose I happen to grep" into "structured data I can read in one shot, with prose where it adds value."

## The two minute pitch

Three things change in every brain file:

1. **Frontmatter gets typed.** Every file has `id`, `type`, `v`, `tags`, `refs`, `updated`. A script can build a `manifest.json` of the whole brain in one pass.
2. **Sections are constrained per type.** An `agent` file has `## ROLE / STACK / RULES / REFS`. An `adr` has `## CONTEXT / DECISION / REASON / CONSEQUENCE`. The LLM (and you) know what's coming.
3. **Refs are typed.** `@agent:reviewer`, `@adr:004`, `@infra:prod-db`, `@secrets:s3-prod`. Cross-file relationships become first-class.

Body prose stays markdown — KMF only constrains the metadata and section names.

## The single-source-of-truth manifest

Run `scripts/regen-manifest.py` after editing any KMF file:

```bash
python3 scripts/regen-manifest.py
# manifest.json: 15.5 kB  counts: {'agents': 12, 'decisions': 4, 'runbooks': 9, ...}
# infra.json:    8.8 kB   nodes=3 vms=12 domains=9 ssh=13 issues=7
```

Now the LLM (or you) reads `manifest.json` to find any file in the brain — no `find` / `grep` needed for "where is X?" queries.

`infra.json` is parsed from `INDEX.md` tables. If your INDEX has different section headings, adapt the script (search for "Adapt section names" in `scripts/regen-manifest.py`).

## Token math

For a 12-agent brain with the standard delegation pipeline:

| Operation | Plain markdown | KMF |
|---|---|---|
| Lookup "where is service X?" | Read INDEX.md (~3 kB) | Read infra.json once per session (~8 kB), cached |
| Delegate to agent | Read SKILL.md (~5–11 kB) | Read SKILL.md (~4–10 kB) |
| Cross-file query | Multiple greps | Manifest read + targeted file read |
| Total typical session | ~6–10k input tokens for memory boilerplate | ~3–5k |

**Rough rule of thumb:** KMF saves 30–50% of input tokens on lookup-heavy sessions, with no accuracy loss. Output tokens unchanged (caveman handles those).

## Folder layout

```
brain/
├── CLAUDE.md                # Top-level coordinator instructions (auto-loaded)
├── KMF.md                   # The format spec (this folder's contract)
├── README.md                # For humans
├── manifest.json            # Generated — every KMF file
├── infra.json               # Generated — infra.json from INDEX.md
├── INDEX.md                 # Human-readable infra overview
├── scripts/
│   └── regen-manifest.py    # Run after every KMF file edit
├── Agents/
│   ├── CLAUDE.md            # Per-folder hint, auto-loaded
│   ├── _shared/PATTERNS.md  # Cross-agent patterns (TDD, debugging, ...)
│   └── <agent>/SKILL.md
├── Decisions/
│   ├── CLAUDE.md
│   └── ADR-NNN-<slug>.md
├── Knowledge/
│   ├── CLAUDE.md
│   └── <slug>.md
├── Conversations/
│   ├── CLAUDE.md
│   └── YYYY-MM-DD-<slug>.md
└── Homelab/   # or whatever your "infra config" folder is
    ├── CLAUDE.md
    └── ...
```

The `CLAUDE.md` files at each level are the per-folder hints — auto-loaded by Claude Code when the folder is in context. Keep them under 30 lines each.

## When to bump `v:`

Only when you change the **structure** of a `type`. Adding a new section, renaming a section, removing a required field. Content changes don't bump `v:`.

`v: 1` is the version this spec was written against. If you fork and add a new type, you can use `v: 2` for the new shape — but tools should treat `v: 1` files as still valid.

## Migration path from a plain markdown brain

If you already have a working AI-Brain in plain markdown:

1. Keep everything where it is. Don't rename anything yet.
2. Add the frontmatter to one type of file (start with agents — biggest token win).
3. Add `## ROLE / STACK / RULES / REFS` sections — usually you can just rename existing headings.
4. Run `regen-manifest.py`. Verify `manifest.json` has all your agents.
5. Add the per-folder `CLAUDE.md` files (use `templates/CLAUDE.md.subfolder.tmpl`).
6. Commit.
7. Move to the next type (ADRs, runbooks, ...).

You don't have to convert the whole brain in one go. KMF and plain markdown coexist fine — `regen-manifest.py` just won't index files that have no frontmatter.

## See also

- `KMF.md` — the spec
- `templates/CLAUDE.md.brain.tmpl` — top-level coordinator template
- `templates/CLAUDE.md.subfolder.tmpl` — per-folder hint template
- `templates/manifest.json.tmpl` — manifest schema
- `templates/infra.json.tmpl` — infra schema
- `scripts/regen-manifest.py` — generation script
