#!/usr/bin/env python3
"""
Regenerate manifest.json + infra.json from the current AI-Brain state.

manifest.json = every KMF file (agents, decisions, runbooks, knowledge,
                conversations, stacks)
infra.json    = infrastructure structure parsed from INDEX.md
                (cluster nodes, VMs, domains, SSH, ports, issues)

Run: python3 scripts/regen-manifest.py

Adapt the folder names below to match your brain structure.
"""
import json
import re
import pathlib

# Adjust this if the script lives elsewhere relative to the brain root.
BRAIN = pathlib.Path(__file__).resolve().parent.parent

# Folders to scan. Adapt to your brain structure.
AGENTS_DIR = "Agents"
DECISIONS_DIR = "Decisions"
RUNBOOKS_DIR = "Runbooks"          # or "Homelab/Plans" etc.
KNOWLEDGE_DIR = "Knowledge"
CONVERSATIONS_DIR = "Conversations"
STACKS_DIR = "Stacks"               # or "Homelab/Stacks" etc.
INDEX_FILE = "INDEX.md"


def fm(p: pathlib.Path) -> dict:
    """Parse YAML frontmatter loosely (single-line scalar values + flat lists)."""
    try:
        s = p.read_text()
    except Exception:
        return {}
    if not s.startswith("---"):
        return {}
    parts = s.split("---", 2)
    if len(parts) < 3:
        return {}
    out = {}
    for line in parts[1].strip().split("\n"):
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        out[k] = v
    return out


def build_manifest() -> dict:
    agents, decisions, runbooks, knowledge, convs, stacks = [], [], [], [], [], []

    agents_root = BRAIN / AGENTS_DIR
    if agents_root.exists():
        for d in sorted(agents_root.iterdir()):
            if not d.is_dir() or d.name.startswith("_"):
                continue
            sk = d / "SKILL.md"
            if not sk.exists():
                continue
            f = fm(sk)
            agents.append({
                "id": f.get("id", f"agent-{d.name}"),
                "name": f.get("name", d.name),
                "aliases": f.get("aliases", []),
                "description": f.get("description", ""),
                "tags": f.get("tags", []),
                "refs": f.get("refs", []),
                "path": f"{AGENTS_DIR}/{d.name}/SKILL.md",
            })

    decisions_root = BRAIN / DECISIONS_DIR
    if decisions_root.exists():
        for p in sorted(decisions_root.glob("*.md")):
            f = fm(p)
            decisions.append({
                "id": f.get("id", p.stem),
                "title": p.stem,
                "tags": f.get("tags", []),
                "updated": f.get("updated", ""),
                "path": f"{DECISIONS_DIR}/{p.name}",
            })

    runbooks_root = BRAIN / RUNBOOKS_DIR
    if runbooks_root.exists():
        for p in sorted(runbooks_root.glob("*.md")):
            f = fm(p)
            runbooks.append({
                "id": f.get("id", f"runbook-{p.stem.lower()}"),
                "title": p.stem,
                "tags": f.get("tags", []),
                "path": f"{RUNBOOKS_DIR}/{p.name}",
            })

    knowledge_root = BRAIN / KNOWLEDGE_DIR
    if knowledge_root.exists():
        for p in sorted(knowledge_root.glob("*.md")):
            f = fm(p)
            knowledge.append({
                "id": f.get("id", f"know-{p.stem.lower()}"),
                "title": p.stem,
                "tags": f.get("tags", []),
                "path": f"{KNOWLEDGE_DIR}/{p.name}",
            })

    conv_root = BRAIN / CONVERSATIONS_DIR
    if conv_root.exists():
        for p in sorted(conv_root.glob("*.md")):
            convs.append({
                "id": f"conv-{p.stem}",
                "title": p.stem,
                "path": f"{CONVERSATIONS_DIR}/{p.name}",
            })
        for sub in sorted(conv_root.iterdir()):
            if sub.is_dir():
                for p in sorted(sub.glob("*.md")):
                    convs.append({
                        "id": f"conv-{sub.name}-{p.stem}",
                        "title": f"{sub.name}/{p.stem}",
                        "path": f"{CONVERSATIONS_DIR}/{sub.name}/{p.name}",
                    })

    stacks_root = BRAIN / STACKS_DIR
    if stacks_root.exists():
        for env_dir in sorted(stacks_root.iterdir()):
            if not env_dir.is_dir():
                continue
            for s in sorted(env_dir.iterdir()):
                if s.is_dir():
                    stacks.append({
                        "id": f"stack-{env_dir.name.lower()}-{s.name}",
                        "env": env_dir.name,
                        "name": s.name,
                        "path": f"{STACKS_DIR}/{env_dir.name}/{s.name}",
                    })

    return {
        "kmf_version": 1,
        "updated": _today(),
        "counts": {
            "agents": len(agents),
            "decisions": len(decisions),
            "runbooks": len(runbooks),
            "knowledge": len(knowledge),
            "conversations": len(convs),
            "stacks": len(stacks),
        },
        "agents": agents,
        "decisions": decisions,
        "runbooks": runbooks,
        "knowledge": knowledge,
        "conversations": convs,
        "stacks": stacks,
    }


def parse_md_table(lines):
    rows = []
    table_lines = [l for l in lines if l.strip().startswith("|") and "---" not in l]
    if len(table_lines) < 2:
        return rows
    headers = [h.strip() for h in table_lines[0].strip("|").split("|")]
    for line in table_lines[1:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def build_infra() -> dict:
    """Parse INDEX.md into structured infra.json. Headings expected:
       '## Cluster ...', '## VMs / CTs ...', '## Domains ...', '## SSH access',
       '## Ports on <host>', '## ZFS ...', '## Open issues'.
       Adapt section names to match your INDEX.md."""
    idx_path = BRAIN / INDEX_FILE
    if not idx_path.exists():
        return {"updated": _today(), "note": f"{INDEX_FILE} missing"}
    idx = idx_path.read_text()

    sections, cur_h, cur_body = {}, None, []
    for line in idx.split("\n"):
        if line.startswith("## "):
            if cur_h:
                sections[cur_h] = cur_body
            cur_h = line[3:].strip()
            cur_body = []
        else:
            cur_body.append(line)
    if cur_h:
        sections[cur_h] = cur_body

    infra = {
        "updated": _today(),
        "cluster": {},
        "nodes": [],
        "vms": [],
        "domains": [],
        "ports": {},
        "ssh": [],
        "zfs_pools": [],
        "open_issues": [],
        "decommissioned": [],
    }

    for k in sections:
        if k.lower().startswith("cluster"):
            for r in parse_md_table(sections[k]):
                infra["nodes"].append({
                    "ip": r.get("IP", ""),
                    "host": r.get("Hostname", "").split(" ")[0],
                    "role": r.get("Role", r.get("Rola", "")),
                    "ram": r.get("RAM", ""),
                    "cpu": r.get("CPU", ""),
                })

    for key in ("VMs / CTs", "VMs", "Hosts"):
        for k in sections:
            if k.lower().startswith(key.lower()):
                for r in parse_md_table(sections[k]):
                    name = r.get("Name", "").split(" ")[0]
                    infra["vms"].append({
                        "ip": r.get("IP", ""),
                        "name": name,
                        "node": r.get("Node", ""),
                        "vmid": r.get("VMID", ""),
                        "os": r.get("OS / Kernel", r.get("OS", "")),
                        "service": r.get("Service", ""),
                        "id": f"infra-{name.lower()}" if name else None,
                    })
                break

    for k in sections:
        if k.lower().startswith("domain"):
            for r in parse_md_table(sections[k]):
                infra["domains"].append({
                    "domain": r.get("Domain", ""),
                    "target": r.get("→ IP:port", r.get("Target", "")),
                    "notes": r.get("Notes", ""),
                })

    for k in sections:
        if k.lower().startswith("ssh"):
            for r in parse_md_table(sections[k]):
                infra["ssh"].append({
                    "host": r.get("Host", ""),
                    "user": r.get("User", ""),
                    "auth": r.get("Auth", ""),
                })

    for k in sections:
        if "open issue" in k.lower() or "otwarte issue" in k.lower():
            for line in sections[k]:
                line = line.strip()
                if line.startswith("- "):
                    infra["open_issues"].append(line[2:])

    for k in sections:
        if k.lower().startswith("decommission"):
            for line in sections[k]:
                line = line.strip()
                if line.startswith("- "):
                    infra["decommissioned"].append(line[2:])

    for k in sections:
        if "ports on" in k.lower() or "porty" in k.lower():
            host_match = re.search(r"\.(\d+)", k)
            if host_match:
                host = f"_unknown_.{host_match.group(1)}"
                ports = []
                for line in sections[k]:
                    if line.strip():
                        for m in re.finditer(r"(\d+)\s+([A-Za-z][\w\.\-]+(?:\s+[A-Z][\w\.\-]*)*)", line):
                            ports.append({"port": int(m.group(1)), "svc": m.group(2).strip()})
                infra["ports"][host] = ports

    for k in sections:
        if "zfs" in k.lower():
            for line in sections[k]:
                line = line.strip()
                if line.startswith("- "):
                    infra["zfs_pools"].append(line[2:])

    return infra


def _today() -> str:
    import datetime
    return datetime.date.today().isoformat()


def main():
    manifest = build_manifest()
    infra = build_infra()

    (BRAIN / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    (BRAIN / "infra.json").write_text(json.dumps(infra, ensure_ascii=False, indent=2))

    print(f"manifest.json: {(BRAIN / 'manifest.json').stat().st_size} B  counts: {manifest['counts']}")
    print(f"infra.json:    {(BRAIN / 'infra.json').stat().st_size} B  "
          f"nodes={len(infra['nodes'])} vms={len(infra['vms'])} "
          f"domains={len(infra['domains'])} ssh={len(infra['ssh'])} "
          f"issues={len(infra['open_issues'])}")


if __name__ == "__main__":
    main()
