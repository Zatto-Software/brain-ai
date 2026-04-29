# Changelog

All notable changes to Ai-Brain-Open are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Initial repository skeleton
- README outlining the four core ideas (3-layer persistence, 4 memory types, flat lookup, lifecycle, conflict detection)
- MIT License
- Folder structure: `docs/`, `templates/`, `hooks/`, `slash-commands/`, `examples/`

### Coming next
- `docs/architecture.md` — three layers explained
- `docs/memory-types.md` — `user` / `feedback` / `project` / `reference`
- `docs/lifecycle.md` — write → update → archive
- `docs/conflict-detection.md` — how to find stale dupes
- `docs/token-budget.md` — measured costs per layer
- `templates/*.tmpl` — drop-in starter files
- `hooks/post-memory-write.sh` — conflict scan
- `hooks/session-start.sh` — rotation reminder
- `slash-commands/brain-status.md`
