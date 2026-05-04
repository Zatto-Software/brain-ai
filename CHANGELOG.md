# Changelog

All notable changes to Ai-Brain-Open are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added — KMF layer
- `KMF.md` — Knowledge Memory Format spec: typed frontmatter (`id`, `type`, `v`, `tags`, `refs`, `updated`), per-type section schema (`agent` / `adr` / `runbook` / `infra` / `knowledge` / `conv`), symbol shorthand (`→`, `@`, `>`, `!`), semantic refs (`@agent:<name>`, `@adr:<id>`, `@infra:<host>`, `@secrets:<key>`)
- `scripts/regen-manifest.py` — generate `manifest.json` (every KMF file) + `infra.json` (parsed from `INDEX.md` tables) in one pass; replaces dozens of greps with a single read
- `templates/CLAUDE.md.brain.tmpl` — top-level coordinator instructions auto-loaded by Claude Code; lookup priority, KMF cheatsheet, workflow per query type
- `templates/CLAUDE.md.subfolder.tmpl` — per-folder hints auto-loaded when the folder enters context (e.g. `Agents/CLAUDE.md`, `Decisions/CLAUDE.md`)
- `templates/manifest.json.tmpl` + `templates/infra.json.tmpl` — schema examples for the generated files
- `docs/kmf.md` — practical guide: token math, folder layout, migration path from plain-markdown brains
- `docs/obsidian-graph.md` — fix Obsidian graph view (12× "SKILL" → 12 named nodes) via `title:` frontmatter + Front Matter Title plugin; includes scripts to add titles + configure the plugin programmatically
- `docs/caveman-integration.md` — full caveman ecosystem map: caveman (output), caveman-compress (input), caveman-shrink (MCP), graphify (knowledge graph), cavemem (storage), cavekit (orchestration); recommended adoption order

### Added
- `agents/` — eleven specialized subagents with explicit triggers, anti-triggers, tools allowlists, model recommendations, safety rails, output format, and anti-patterns:
  `borys-developer`, `atlas-architect`, `daga-dba`, `teo-qa`, `rena-reviewer`, `straz-security`, `pixel-designer`, `olek-devops`, `sowa-researcher`, `nika-analyst`, `klio-writer`
- `agents/_shared/SAFETY.md` — Tier 1/2/3 destructive action policy (refuse / approval-gate / autonomous)
- `agents/_shared/PATTERNS.md` — TDD, debugging, verification, conventional commits, naming, **branch + PR workflow** (every code-writing agent must branch + PR + return URL, never commit to main)
- `agents/README.md` — roster, common pipelines, install instructions, model tier recommendations
- `examples/orchestrator-prompt.md` — coordinator template (the meta-agent that routes work to the eleven subagents)
- `NOTICE` — Apache 2.0 attribution file

### Changed
- License: **MIT → Apache 2.0** (patent grant + termination clause are meaningful for AI tooling)
- `templates/agent_SKILL.md.tmpl` — expanded with frontmatter (`tools`, `model`), explicit triggers / anti-triggers, safety rails section, output format spec, anti-patterns section
- `README.md` — added agent team section + install steps for agents and orchestrator prompt

### Original initial commit
- Repository skeleton
- README outlining the four core ideas (3-layer persistence, 4 memory types, flat lookup, lifecycle, conflict detection)
- Folder structure: `docs/`, `templates/`, `hooks/`, `slash-commands/`, `examples/`
