# Obsidian graph view setup

If you use Obsidian to browse your AI-Brain, the graph view will show every `SKILL.md` as a node literally labelled "SKILL". Same for `CLAUDE.md`, `RULES.md`, `README.md`. Useless visualization.

This doc shows how to fix it without renaming any files (renaming would break Claude Code's skill auto-discovery, which expects `SKILL.md`).

## What we do

1. Add `title:` to every KMF file's frontmatter (one-time, scriptable).
2. Install the **Front Matter Title** Obsidian plugin.
3. Toggle it on for graph + a few related views.

After this: `SKILL.md` files show as `Borys`, `Atlas`, `Pixel`. `CLAUDE.md` files show as `Brain: Agents`, `Brain: Decisions`, etc.

## Step 1 — Add `title:` to all generic-named files

Generic-named = files where the filename gives no information (`SKILL.md`, `CLAUDE.md`, `RULES.md`, `README.md`).

KMF files already have machine-readable IDs in frontmatter. We just add a human-readable `title:` so the Obsidian plugin has something to display.

Use this script (adjust paths/regex to your brain):

```python
import re, pathlib

BRAIN = pathlib.Path("/path/to/your/brain")

def humanize(slug):
    return " ".join(w.capitalize() for w in slug.replace("-", " ").replace("_", " ").split())

def title_for(p: pathlib.Path) -> str | None:
    rel = p.relative_to(BRAIN)
    parts = rel.parts
    name = p.name

    if name == "CLAUDE.md":
        if len(parts) == 1:
            return "Brain"
        return f"Brain: {parts[0]}"
    if name == "README.md":
        if len(parts) == 1:
            return "Brain README"
        return f"{humanize(parts[-2])} README"
    if name == "RULES.md":
        return f"Rules: {humanize(parts[-2])}"
    if name == "SKILL.md":
        # Agents/<name>/SKILL.md
        if len(parts) == 3 and parts[0] == "Agents":
            return humanize(parts[1])
        # Sub-skills: Agents/<agent>/skills/.../<slug>/SKILL.md
        if "skills" in parts:
            return f"{humanize(parts[-2])} ({parts[1]})"
    return None

files = list(BRAIN.rglob("SKILL.md")) + list(BRAIN.rglob("CLAUDE.md")) + \
        list(BRAIN.rglob("RULES.md")) + list(BRAIN.rglob("README.md"))
files = [p for p in files if ".git" not in p.parts]

for p in files:
    title = title_for(p)
    if not title:
        continue
    s = p.read_text()
    if not s.startswith("---\n"):
        # No frontmatter — add a fresh one
        p.write_text(f"---\ntitle: {title}\n---\n\n" + s)
        continue
    parts = s.split("---", 2)
    if len(parts) < 3:
        continue
    fm = parts[1]
    if any(l.strip().startswith("title:") for l in fm.split("\n")):
        continue  # already has a title
    p.write_text("---\ntitle: " + title + fm + "---" + parts[2])
    print(f"  {p}")
```

Run it once. Idempotent — re-running won't double-add.

## Step 2 — Install Front Matter Title

Obsidian → Settings → Community plugins → Browse → search "Front Matter Title" → Install → Enable.

Plugin: [snezhig/obsidian-front-matter-title](https://github.com/snezhig/obsidian-front-matter-title). v3.x.

## Step 3 — Configure

In the plugin settings:

- **Common main template**: `title` (default — reads `title:` from frontmatter)
- **Common fallback template**: `fallback_title` (default — falls back to filename if `title` missing)

Toggle ON for:
- **Graph** (the main goal)
- **Explorer** (file tree shows titles instead of `SKILL`)
- **Tabs** (open tabs show titles)
- **Header** (note header shows title)
- **Suggest** (autocomplete `[[...]]` uses titles)
- **Search** (search results use titles)
- **Backlink** (linked mentions use titles)
- **Inline title** (top-of-note title display)

Skip / optional:
- Alias, Bookmarks, Canvas, Window Frame Title, Note Link

## Step 4 — Reload

Cmd+P → "Reload app without saving".

Open graph view — every `SKILL.md` node now shows its agent name. CLAUDE.md nodes show their folder. The graph is finally readable.

## Programmatic plugin configuration (optional)

After you toggle one feature on manually (so the plugin creates `data.json`), you can edit `<vault>/.obsidian/plugins/obsidian-front-matter-title-plugin/data.json` directly:

```python
import json, pathlib

dj = pathlib.Path("/path/to/vault/.obsidian/plugins/obsidian-front-matter-title-plugin/data.json")
d = json.loads(dj.read_text())
for f in ["explorer", "tab", "header", "suggest", "search", "backlink", "inlineTitle"]:
    d["features"][f]["enabled"] = True
dj.write_text(json.dumps(d, indent=2))
```

Then reload Obsidian.

## What this doesn't fix

The graph still has clusters of disconnected nodes if your KMF files don't link to each other. To create graph edges, use Obsidian wikilinks `[[...]]` in your prose, or the `refs:` field in KMF frontmatter (the plugin doesn't read it as edges, but a custom Obsidian plugin or graphify can).

For deeper structural insights — community detection, "god nodes", cross-document edges — see `docs/graphify.md`.
