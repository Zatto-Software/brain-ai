#!/usr/bin/env python3
"""
PreToolUse hook — enforce KMF frontmatter on Write/Edit of tracked .md files.

Wejście: JSON z stdin (Claude Code hook spec).
Tool input: {file_path, content (Write) | new_string (Edit)}.

Strategia:
- Tylko *.md w tracked dirs: Agents/, Decisions/, Knowledge/, memory/topics/,
  Projects/, Clients/, Hostings/, SpecKits/
- Write (cały plik): WYMAGA frontmatter z required fields per type. Block on miss.
- Edit (delta): NIE blokuje (delta nie zna pełnego pliku). Warn jeśli new_string
  zaczyna od `---` i brakuje required pola.
- Skip: CLAUDE.md, README.md, AGENTS.md, TEAM.md, MEMORY.md, INDEX.md (entry docs).

Exit:
- 0 = OK
- 2 + stderr = block (Claude widzi powód)

Test:
  echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/x.md","content":"hi"}}' \
    | python3 hook-kmf-check.py
"""
import sys, json, re, os

TRACKED_DIRS = (
    '/Agents/', '/agents/', '/Decisions/', '/Knowledge/', '/memory/topics/',
    '/Projects/', '/Clients/', '/Hostings/', '/SpecKits/',
)
SKIP_NAMES = {'CLAUDE.md', 'README.md', 'AGENTS.md', 'TEAM.md',
              'MEMORY.md', 'INDEX.md', '_index.md', '_meta.md'}

REQUIRED_BY_TYPE = {
    'agent':         ['id', 'type', 'v', 'tags', 'updated', 'name', 'description'],
    'adr':           ['id', 'type', 'v', 'tags', 'updated'],
    'decision':      ['id', 'type', 'v', 'tags', 'updated'],
    'runbook':       ['id', 'type', 'v', 'tags', 'updated'],
    'knowledge':     ['id', 'type', 'v', 'tags', 'updated'],
    'conv':          ['id', 'type', 'v', 'tags', 'updated'],
    'client':        ['id', 'type', 'v', 'tags', 'updated'],
    'project':       ['id', 'type', 'v', 'tags', 'updated'],
    'hosting':       ['id', 'type', 'v', 'tags', 'updated'],
    'speckit':       ['id', 'type', 'v', 'tags', 'updated'],
    'memory-topic':  ['id', 'type', 'v', 'tags', 'updated'],
    'spec':          ['id', 'type', 'v', 'tags', 'updated'],
}
BASE_REQUIRED = ['type', 'tags', 'updated']
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def parse_fm(text):
    if not text.startswith('---'):
        return None
    parts = text.split('---', 2)
    if len(parts) < 3:
        return None
    out = {}
    for line in parts[1].strip().split('\n'):
        m = re.match(r'^(\w+):\s*(.*)$', line)
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip()
        out[k] = v
    return out


def is_tracked(fp):
    if not fp.endswith('.md'):
        return False
    name = os.path.basename(fp)
    if name in SKIP_NAMES:
        return False
    return any(d in fp for d in TRACKED_DIRS)


def validate(content, fp):
    fm = parse_fm(content)
    if fm is None:
        return [f'missing KMF frontmatter block (--- ... --- header)']
    t = fm.get('type', '').strip().strip('"').strip("'")
    required = REQUIRED_BY_TYPE.get(t, BASE_REQUIRED)
    missing = [k for k in required if k not in fm or not fm[k]]
    errs = []
    if missing:
        errs.append(f'missing required fields for type={t or "?"}: {", ".join(missing)}')
    upd = fm.get('updated', '').strip().strip('"').strip("'")
    if upd and not DATE_RE.match(upd):
        errs.append(f'"updated" must be YYYY-MM-DD (got: {upd})')
    return errs


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    tool = data.get('tool_name', '')
    ti = data.get('tool_input', {}) or {}
    fp = ti.get('file_path', '')
    if not fp or not is_tracked(fp):
        return 0
    if tool == 'Write':
        content = ti.get('content', '') or ''
        errs = validate(content, fp)
        if errs:
            print(
                f'BLOCKED by hook-kmf-check: {fp}\n  - ' + '\n  - '.join(errs)
                + '\nFix: add KMF frontmatter (see KMF.md). Required min: '
                + ', '.join(BASE_REQUIRED) + '.',
                file=sys.stderr,
            )
            return 2
    elif tool == 'Edit':
        new = ti.get('new_string', '') or ''
        if new.lstrip().startswith('---'):
            errs = validate(new.lstrip(), fp)
            if errs:
                print(
                    f'WARN hook-kmf-check (Edit, non-blocking): {fp}\n  - '
                    + '\n  - '.join(errs),
                    file=sys.stderr,
                )
    return 0


if __name__ == '__main__':
    sys.exit(main())
