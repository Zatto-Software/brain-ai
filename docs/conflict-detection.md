# Conflict detection

The single failure mode that costs the most tokens is **two memories that disagree about the same fact**. Claude reads both, picks one (often the wrong one), and acts on stale data. Then someone has to debug why the recommendation pointed at a host that's been gone for a week.

This document covers how to spot conflicts before they cost real time, and the hook that automates it.

## Where conflicts come from

1. **Migration churn.** A service moves from host A to host B. New session writes a fresh `reference_*` instead of updating the existing one. Now you have two.
2. **Naming drift.** Same service, different names. `Dokploy panel` vs `Dokploy access` vs `Dokploy server`. Each session picks whichever is shortest, and the trio diverges.
3. **Description scope creep.** A `project_*` outgrows its slug; another project memory starts overlapping. Both end up containing pending items for the same migration.
4. **Lost archival.** A `project_*` ships, but instead of being archived, it's left "for reference". Two months later it disagrees with the live `reference_*`.

## Detection — manual

Three checks worth running periodically:

### 1. Same-keyword grep

```bash
grep -l "<keyword>" memory/*.md | wc -l
```

If a noun (hostname, IP, service, port) appears in 3+ files, those files are a candidate consolidation set. Sometimes legitimate (one is the panel, one is the worker, one is the database). Often not.

### 2. IP collision

```bash
grep -hoE '192\.168\.[0-9]+\.[0-9]+' memory/*.md | sort -u | while read ip; do
  count=$(grep -l "$ip" memory/*.md | wc -l)
  [ "$count" -gt 1 ] && echo "$ip → $count files"
done
```

An IP appearing in multiple `reference_*` files is fine if they describe the same machine in different roles. An IP appearing in multiple `project_*` files often means stale migration narratives.

### 3. Description duplication

```bash
awk -F'description: ' '/^description:/ {print $2 " -- " FILENAME}' memory/*.md | sort
```

Sort the descriptions. Near-duplicates (e.g., two memories both starting "Dokploy panel host") are the strongest conflict signal.

## Detection — automated (hook)

`hooks/post-memory-write.sh` runs after Claude writes to the memory dir. It does:

1. Greps every IP, hostname, and domain referenced in any memory.
2. Counts files per token.
3. If a token appears in 3+ files **and at least one is a `project_*`**, surfaces the conflict at next session start.
4. Writes a one-line warning to `~/.claude/brain-conflicts.log`.

It does NOT auto-merge. Auto-merge of memory is too risky — the wrong one wins silently. The hook only flags; resolution is human (or an explicit `/brain-conflict` slash command).

See `hooks/post-memory-write.sh` for the implementation.

## Resolution playbook

When a conflict is flagged:

1. **Read all conflicting files.** Don't trust the descriptions; read bodies.
2. **Establish ground truth.** SSH to the host, hit the URL, run the command. Reality wins.
3. **Pick the canonical file.** Usually the most recently updated `reference_*` if it matches reality.
4. **Merge.** Pull useful detail from the others; rewrite canonical file once.
5. **Archive or delete the others.** If they contain institutional memory (a closed migration), archive to `Decisions/`. Otherwise delete.
6. **Update `MEMORY.md`.** One entry, not three.
7. **Commit.** `consolidate: <topic> (N files → 1)`.

## When NOT to consolidate

Some "near-duplicates" are legitimate:

- **Different roles for the same name.** "Dokploy panel" (the manager UI) and "Dokploy worker" (the deployment target) share a name but are distinct things. Two files OK.
- **Different layers of detail.** A `reference_*` with the live API endpoints and a `Decisions/*` with the migration ADR. Different lifecycles, both legitimate.
- **One is current, one is historical.** If the historical entry has clear "as of <date>, deprecated" markers, fine. If it doesn't — add them or archive.

The test: if Claude's next answer about the topic depends on *which* file it reads first, you have a conflict. If both files give the same answer, you have legitimate separation.
