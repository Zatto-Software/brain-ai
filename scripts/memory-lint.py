#!/usr/bin/env python3
"""
memory-lint — bibliotekarz tool. Static analysis brain memory layer.

Detects:
  - orphans:        @ref:X bez celu w _meta / filesystem
  - stale:          memory/topics/*.md updated >90d + brak dailies
  - duplicates:     pary topics z jaccard token similarity >0.6
  - daily-edit:     non-append modyfikacja historycznych daily (git)
  - missing-fm:     KMF bez wymaganego frontmatter

Output: stdout human-readable + JSON gdy --json.
Run:    python3 scripts/memory-lint.py [--json] [--fix-suggest] [--since YYYY-MM-DD]
"""
import sys, re, json, pathlib, datetime, subprocess, argparse, collections

BRAIN = pathlib.Path(__file__).resolve().parent.parent
MEM = BRAIN / 'memory'
TOPICS = MEM / 'topics'
DECISIONS = BRAIN / 'Decisions'
AGENTS = BRAIN / 'Agents'
KNOWLEDGE = BRAIN / 'Knowledge'
CONVERSATIONS = BRAIN / 'Conversations'

REF_RE = re.compile(r'@(agent|adr|runbook|knowledge|conv|infra|shared|secrets|topic):([A-Za-z0-9_\-\.]+)')
FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
TAG_INLINE_RE = re.compile(r'#([a-z0-9][a-z0-9\-_]{1,40})')
TODAY = datetime.date.today()
STALE_DAYS = 90
DUP_THRESHOLD = 0.6


def load_meta():
    p = BRAIN / '_meta.json'
    return json.loads(p.read_text()) if p.exists() else {}


def parse_fm(text):
    m = FM_RE.match(text)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if ':' in line and not line.startswith(' '):
            k, _, v = line.partition(':')
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


CODE_FENCE_RE = re.compile(r'```.*?```', re.DOTALL)
INLINE_CODE_RE = re.compile(r'`[^`]+`')
DATE_PREFIX_RE = re.compile(r'^\d{4}-\d{2}-\d{2}-')


def scan_refs(path):
    text = path.read_text(errors='ignore')
    text = CODE_FENCE_RE.sub('', text)
    text = INLINE_CODE_RE.sub('', text)
    return [(m.group(1), m.group(2), m.start()) for m in REF_RE.finditer(text)]


def norm(name):
    n = name.lower().strip('.,;:')
    for prefix in ('know-', 'adr-', 'agent-', 'topic-', 'conv-', 'runbook-'):
        if n.startswith(prefix):
            n = n[len(prefix):]
    n = DATE_PREFIX_RE.sub('', n)
    return n


def build_ref_index(meta):
    idx = {'agent': set(), 'adr': set(), 'runbook': set(), 'knowledge': set(),
           'conv': set(), 'infra': set(), 'shared': set(), 'secrets': set(), 'topic': set()}
    for a in meta.get('agents', []):
        idx['agent'].add(norm(a.get('name', '')))
    # agent aliases from SKILL.md frontmatter
    for p in AGENTS.glob('*/SKILL.md'):
        fm = parse_fm(p.read_text(errors='ignore')) or {}
        idx['agent'].add(norm(p.parent.name))
        aliases = fm.get('aliases', '')
        if aliases:
            for a in re.split(r'[,\[\]\s]+', aliases):
                a = a.strip()
                if a:
                    idx['agent'].add(norm(a))
    for d in meta.get('decisions', []):
        idx['adr'].add(norm(d.get('id', '')))
        idx['adr'].add(norm(d.get('title', '')))
    for d in DECISIONS.glob('*.md'):
        idx['adr'].add(norm(d.stem))
    if TOPICS.exists():
        for t in TOPICS.glob('*.md'):
            idx['topic'].add(norm(t.stem))
    if KNOWLEDGE.exists():
        for k in KNOWLEDGE.glob('*.md'):
            idx['knowledge'].add(norm(k.stem))
    sh = AGENTS / '_shared'
    if sh.exists():
        for s in sh.glob('*.md'):
            idx['shared'].add(norm(s.stem))
    # Runbooks may live under any of these conventional locations — first hit wins.
    for runbooks in (BRAIN / 'Runbooks', BRAIN / 'Homelab' / 'Runbooks'):
        if runbooks.exists():
            for r in runbooks.glob('*.md'):
                idx['runbook'].add(norm(r.stem))
            break
    return idx


def check_orphans(idx):
    out = []
    scan_dirs = [MEM, AGENTS, DECISIONS, KNOWLEDGE, BRAIN / 'Projects']
    for base in scan_dirs:
        if not base.exists():
            continue
        for p in base.rglob('*.md'):
            for kind, name, _ in scan_refs(p):
                if kind in ('secrets', 'infra'):
                    continue
                if name in ('X', 'Y', '...', 'name', 'slug', 'id'):
                    continue
                pool = idx.get(kind, set())
                n = norm(name)
                hit = n in pool or any(n and x and (n in x or x in n) for x in pool)
                if not hit:
                    out.append({'ref': f'@{kind}:{name}',
                                'used_in': str(p.relative_to(BRAIN)),
                                'severity': 'warn',
                                'fix': f'Create {kind} or remove ref'})
    return out


def check_stale():
    out = []
    if not TOPICS.exists():
        return out
    daily_tags = set()
    for d in MEM.glob('????-??-??.md'):
        for tag in TAG_INLINE_RE.findall(d.read_text(errors='ignore')):
            daily_tags.add(tag)
    for t in TOPICS.glob('*.md'):
        fm = parse_fm(t.read_text(errors='ignore')) or {}
        u = fm.get('updated', '')
        try:
            age = (TODAY - datetime.date.fromisoformat(u)).days
        except Exception:
            continue
        recent_tagged = any(tag in t.stem or t.stem in tag for tag in daily_tags)
        if age > STALE_DAYS and not recent_tagged:
            out.append({'file': str(t.relative_to(BRAIN)),
                        'updated': u, 'age_days': age,
                        'severity': 'info', 'suggest': 'archive'})
    return out


def tokens(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
    return {w for w in text.split() if len(w) > 3}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def check_duplicates():
    out = []
    if not TOPICS.exists():
        return out
    files = list(TOPICS.glob('*.md'))
    toks = {f: tokens(f.read_text(errors='ignore')) for f in files}
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            s = jaccard(toks[files[i]], toks[files[j]])
            if s >= DUP_THRESHOLD:
                out.append({'files': [str(files[i].relative_to(BRAIN)),
                                       str(files[j].relative_to(BRAIN))],
                            'similarity': round(s, 3),
                            'severity': 'warn',
                            'suggest': 'merge or differentiate'})
    return out


def check_daily_edits(since=None):
    """Use git to detect non-append modifications to historical dailies."""
    out = []
    try:
        ref = 'HEAD'
        cmd = ['git', '-C', str(BRAIN), 'log', '--pretty=%H', '--', 'memory/']
        log = subprocess.check_output(cmd, text=True).splitlines()
    except Exception:
        return out
    for d in MEM.glob('????-??-??.md'):
        try:
            stat = subprocess.check_output(
                ['git', '-C', str(BRAIN), 'log', '--numstat', '--pretty=format:%H %ad', '--date=short', '--', str(d.relative_to(BRAIN))],
                text=True)
        except Exception:
            continue
        # Heuristic: rows with deletions >0 = non-append.
        for line in stat.splitlines():
            parts = line.split('\t')
            if len(parts) == 3 and parts[1].isdigit() and int(parts[1]) > 0:
                out.append({'file': str(d.relative_to(BRAIN)),
                            'severity': 'error',
                            'note': f'historical daily had {parts[1]} deletions (non-append)',
                            'fix': 'Revert or split into new topic'})
                break
    return out


def check_missing_frontmatter():
    out = []
    required = {'id', 'type', 'v', 'tags', 'updated'}
    scan = []
    if TOPICS.exists():
        scan += list(TOPICS.glob('*.md'))
    if KNOWLEDGE.exists():
        scan += list(KNOWLEDGE.glob('*.md'))
    if DECISIONS.exists():
        scan += list(DECISIONS.glob('*.md'))
    if AGENTS.exists():
        scan += list(AGENTS.glob('*/SKILL.md'))
    for p in scan:
        if p.name == 'CLAUDE.md':
            continue
        fm = parse_fm(p.read_text(errors='ignore'))
        if not fm:
            out.append({'file': str(p.relative_to(BRAIN)),
                        'severity': 'error', 'missing': 'frontmatter block',
                        'fix': 'Add KMF frontmatter (id, type, v, tags, updated)'})
            continue
        miss = required - set(fm.keys())
        if miss:
            out.append({'file': str(p.relative_to(BRAIN)),
                        'severity': 'warn', 'missing': sorted(miss),
                        'fix': f'Add fields: {", ".join(sorted(miss))}'})
    return out


def report_human(rep):
    counts = {k: len(v) for k, v in rep.items()}
    print(f'memory-lint — {datetime.datetime.now().isoformat(timespec="seconds")}')
    print(f'counts: {counts}')
    for cat, items in rep.items():
        if not items:
            continue
        print(f'\n## {cat} ({len(items)})')
        for it in items[:50]:
            print(f'  - {json.dumps(it, ensure_ascii=False)}')
        if len(items) > 50:
            print(f'  ... +{len(items)-50} more')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--since')
    args = ap.parse_args()
    meta = load_meta()
    idx = build_ref_index(meta)
    rep = {
        'orphans': check_orphans(idx),
        'stale': check_stale(),
        'duplicates': check_duplicates(),
        'daily_edits': check_daily_edits(args.since),
        'missing_frontmatter': check_missing_frontmatter(),
    }
    if args.json:
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        report_human(rep)
    err = sum(1 for cat in rep.values() for x in cat if x.get('severity') == 'error')
    sys.exit(1 if err else 0)


if __name__ == '__main__':
    main()
