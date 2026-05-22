---
title: MCP servers — recommended set for the brain
---

# MCP servers — recommended set for the brain

Model Context Protocol (MCP) servers extend Claude Code with stdio tools that map cleanly to the brain's lookup tiers (L1-L4 in `architecture.md`).

The active set we run in production at the moment is four servers. Each one earns its keep on a specific bottleneck.

## 1. `basic-memory` — KMF-native memory backend (L4)

SQLite FTS5 + sqlite-vec embeddings, KMF-aware. Drop-in semantic search layer for `memory/topics/` and `Knowledge/`. Where ripgrep stops (you don't know the keyword, you know the gist), this server starts.

- Where it shines: "find me notes similar to this one", "what topics did we discuss about X across the last 90 days"
- What it doesn't replace: L1 `_meta.json` is still the cheapest first read for "who/what" queries
- Indexing scope: `memory/`, `Knowledge/`, `Decisions/`, optionally `Agents/`

## 2. `serena` — LSP semantic code search

Tree-sitter + LSP for TypeScript and Python codebases. Brings IDE-grade symbol search to the agent: "find every caller of `createUser`", "rename across the project", "show me the definition of this import".

- Where it shines: refactoring, "what depends on this function", architecture review
- What it doesn't replace: ripgrep for non-code files, free-text search

## 3. `sequential-thinking` — branchable reasoning

Adds a structured chain-of-thought tool with branch / revise / merge semantics. Used by architect and researcher agents when the problem space has many viable options.

- Where it shines: ADR drafting, multi-option benchmark evaluation, "what would we lose if we picked B instead of A"
- What it doesn't replace: just write the plan in markdown when the option set is ≤3

## 4. `repomix` — tree-sitter codebase compression

Packs an entire codebase (or a remote GitHub repo) into a single compressed XML blob with security scanning. Designed for fast bulk analysis — code review across hundreds of files, audit sweeps, documentation generation.

- Where it shines: "audit this repo for OWASP issues", "summarize the architecture of this monorepo", external-repo audits (see `straz-security/REFERENCE.md`)
- What it doesn't replace: targeted file reads when you know exactly what you need

## Configuration sketch

Per-project, in `.claude.json` (Claude Code reads this on session start):

```jsonc
{
  "mcpServers": {
    "basic-memory": { "command": "npx", "args": ["-y", "@basic-memory/mcp"] },
    "serena": { "command": "uvx", "args": ["serena", "mcp"] },
    "sequential-thinking": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"] },
    "repomix": { "command": "npx", "args": ["-y", "repomix-mcp"] }
  }
}
```

After editing `settings.json` / `.claude.json` the user must reload (open `/hooks` or restart Claude Code — the file watcher catches the rest).

## Token economy of MCP

MCP servers cost zero tokens when idle. Their tools / prompts list is loaded once on session start. For very large servers (filesystem, full GitHub, full Slack), consider wrapping them in [`caveman-shrink`](https://github.com/JuliusBrussee/caveman) to compress `tools/list` and `prompts/list` descriptions before they hit the model.

## What NOT to install

A common failure mode is "every MCP server I see on Twitter". Each server adds: (1) startup latency, (2) tools/list descriptions in every system prompt, (3) one more thing to debug when something hangs. The rule of thumb: install when there's a concrete bottleneck this server removes — not preemptively.
