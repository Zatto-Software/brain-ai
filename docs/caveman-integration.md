# Caveman ecosystem integration

The [caveman](https://github.com/JuliusBrussee/caveman) ecosystem composes well with KMF and the AI-Brain framework. This doc covers what each tool does, where it fits, and how to enable it.

## TL;DR

| Layer | Tool | What it compresses | Typical savings |
|---|---|---|---|
| Output | `caveman` | LLM responses | ~75% of output tokens |
| Input — memory files | `caveman-compress` | `CLAUDE.md`, `MEMORY.md`, KMF files | ~46% of input tokens |
| Input — MCP descriptions | `caveman-shrink` | `tools/list` / `prompts/list` payloads | ~30% of MCP overhead |
| Input — corpus query | `graphify` | Document content via knowledge graph | ~70x for large corpora |
| Memory storage | `cavemem` | Cross-agent persistent memory | Compressed SQLite via MCP |
| Build orchestration | `cavekit` | Spec-driven autonomous build loops | Workflow, not tokens |

These all stack. With the full pipeline the typical brain session uses about half the input tokens and a quarter of the output tokens of the unoptimized baseline, with no accuracy loss.

## 1. caveman (output compression)

[github.com/JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)

A Claude Code skill / plugin that makes the agent talk like a caveman — drops articles, filler, hedging, pleasantries. Technical content stays exact. Levels: `lite`, `full`, `ultra`, plus 文言文 (classical Chinese) variants.

Install (Claude Code):
```bash
claude plugin marketplace add JuliusBrussee/caveman
claude plugin install caveman@caveman
```

Or one-line:
```bash
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash
```

Activate per session: `/caveman` or "talk like caveman". Disable: "stop caveman".

**Why it matters for an AI-Brain:** every coordinator-to-agent message and agent-to-coordinator response runs through caveman. On a busy session, that's the difference between 8k output tokens and 2k.

## 2. caveman-compress (memory file input compression)

`/caveman:compress <file>` — a sub-skill that takes a markdown memory file and rewrites it caveman-style. Saves a backup as `<file>.original.md`.

Use it on:
- `CLAUDE.md` (top-level + per-folder)
- KMF files where prose dominates (ADRs, knowledge entries, conversations)
- INDEX.md (if your version has prose, not just tables)

**When NOT to use it:**
- Files that are mostly code (it preserves code blocks but the wrapper prose isn't worth 5%)
- Files that are mostly tables (already terse)
- KMF agent SKILL.md files that you've already manually structured (you'll get more by adopting KMF than by running caveman-compress)

Typical receipt for a non-Polish, prose-heavy memory file:
- 706 → 285 bytes (-60%)
- 1145 → 535 bytes (-53%)
- 1122 → 636 bytes (-43%)

For Polish or other non-English brains, savings are lower (~5–15%) because English-targeted filler-removal rules don't apply cleanly. KMF gives you better results in that case.

## 3. caveman-shrink (MCP middleware)

A stdio proxy that wraps any MCP server and compresses the `description` fields in `tools/list` / `prompts/list` / `resources/list` responses. Code, URLs, paths, identifiers stay byte-for-byte identical.

```jsonc
{
  "mcpServers": {
    "fs-shrunk": {
      "command": "npx",
      "args": ["caveman-shrink", "npx", "@modelcontextprotocol/server-filesystem", "/path"]
    }
  }
}
```

Auto-installed by the caveman installer (`--with-mcp-shrink`, default on). Published on npm as [`caveman-shrink`](https://www.npmjs.com/package/caveman-shrink).

**When you'd skip it:** if you have no MCP servers configured (`claude mcp list` returns empty), there's nothing to wrap.

## 4. graphify (knowledge graph for the brain)

[graphify.net](https://graphify.net) — a Claude Code skill that builds a queryable knowledge graph from any folder of files. Multimodal: code, docs, papers, images.

Install:
```bash
pipx install graphifyy   # the package is graphifyy; the CLI is graphify
graphify install --platform claude
```

Run on your brain:
```
/graphify .
```

What you get:
- `graphify-out/graph.html` — interactive graph view
- `graphify-out/obsidian/` — Obsidian vault of the brain
- `graphify-out/wiki/` — agent-crawlable Wikipedia-style markdown (point any agent at `index.md`)
- `graphify-out/GRAPH_REPORT.md` — god nodes + surprising connections + suggested questions
- `graphify-out/graph.json` — persistent graph; query weeks later without re-reading
- `graphify-out/cache/` — SHA256 cache; re-runs only process changed files

Plus a built-in MCP mode (`/graphify <path> --mcp`) so subagents can query the graph as a tool.

**Cost:** initial build calls Claude per file (cached after). On a 100–200 file brain, plan for $0.50–$2 first run, near-zero after (only changed files re-extract).

**When it shines:** "what connects X to Y?" queries that grep can't answer. Cross-document patterns (an ADR cites a Knowledge entry that cites a Conversation that triggered the ADR). god-node detection (the concepts that everything else hangs off of).

## 5. cavemem (cross-agent memory)

[github.com/JuliusBrussee/cavemem](https://github.com/JuliusBrussee/cavemem) — compressed SQLite-backed memory with an MCP interface, shared across agents.

Use case: when your file-based memory grows past a few hundred entries and you want sub-second key/tag lookups, plus persistent memory across multiple Claude Code projects.

Migration is non-trivial (file-based → SQLite). Evaluate before you commit. The file-based AI-Brain in this repo will keep working fine for most teams; cavemem becomes worth it past ~500 memory entries.

## 6. cavekit (autonomous build orchestration)

[github.com/JuliusBrussee/cavekit](https://github.com/JuliusBrussee/cavekit) — a spec-driven build loop. You write a natural-language spec; cavekit decomposes it, runs parallel agent passes, and verifies the result.

Independent from the AI-Brain; both can compose if your feature pipeline (`analyst → architect → developer → qa → reviewer → devops`) is repetitive enough to script.

Out of scope for most teams adopting AI-Brain for the first time.

## Recommended adoption order

1. **caveman** — install first. Output compression is the lowest-effort, highest-impact change.
2. **graphify** — install when your brain crosses ~50 files. The wiki output alone is worth it.
3. **caveman-shrink** — when (and only when) you add MCP servers.
4. **caveman-compress** — selectively, on non-Polish prose-heavy files. Skip if you've already adopted KMF.
5. **cavemem** — if and when you outgrow file-based memory.
6. **cavekit** — if your build pipeline is mature enough to automate.

You don't need all six. Start with caveman + KMF + the AI-Brain framework. Add the rest as you hit the problems they solve.
