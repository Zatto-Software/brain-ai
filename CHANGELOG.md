# Changelog

All notable changes to Ai-Brain-Open are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `agents/` — eleven specialized subagents with explicit triggers, anti-triggers, tools allowlists, model recommendations, safety rails, output format, and anti-patterns:
  `borys-developer`, `atlas-architect`, `daga-dba`, `teo-qa`, `rena-reviewer`, `straz-security`, `pixel-designer`, `olek-devops`, `sowa-researcher`, `nika-analyst`, `klio-writer`
- `agents/_shared/SAFETY.md` — Tier 1/2/3 destructive action policy (refuse / approval-gate / autonomous)
- `agents/_shared/PATTERNS.md` — TDD, debugging, verification, conventional commits, naming
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
