#!/usr/bin/env python3
"""
Consolidate memory/ daily logs → memory/topics/.

Trigger: ≥24h since last + ≥5 daily logs accumulated.
Strategy: LLM-driven (manual run pierwsze 2 tygodnie, cron po validacji).

Co robi:
- Skanuje memory/YYYY-MM-DD.md (append-only daily)
- Grupuje wpisy per topic (klient, projekt, infra obszar)
- Wykrywa duplikaty + supersedes
- Outputs: kandydat topic update do memory/topics/<slug>.md
- Update MEMORY.md index z aktywnymi topics

Stan: szkielet. Pełna impl po FAZA 4 polish (potrzebny LLM call).
Manual workflow: Klaudiusz czyta dailies + pisze topics by hand.

Run: python3 scripts/consolidate.py [--dry-run]
"""
import sys, pathlib, re, datetime, json

BRAIN = pathlib.Path(__file__).resolve().parent.parent
MEM = BRAIN / 'memory'
TOPICS = MEM / 'topics'


def list_dailies():
    """Return sorted list of (date, path) dla memory/YYYY-MM-DD.md."""
    out = []
    for p in MEM.glob('????-??-??.md'):
        m = re.match(r'(\d{4}-\d{2}-\d{2})', p.stem)
        if m:
            out.append((m.group(1), p))
    return sorted(out)


def list_topics():
    """Return list (slug, path) dla memory/topics/*.md."""
    return [(p.stem, p) for p in sorted(TOPICS.glob('*.md'))]


def should_run():
    """Trigger check: ≥24h od last consolidate + ≥5 dailies."""
    log = MEM / 'log.md'
    dailies = list_dailies()
    if len(dailies) < 5:
        return False, f'tylko {len(dailies)} dailies (need ≥5)'
    if not log.exists():
        return True, 'first run'
    txt = log.read_text()
    m = re.search(r'## (\d{4}-\d{2}-\d{2}).*consolidate', txt, re.M)
    if not m:
        return True, 'no prior consolidate in log'
    last = datetime.date.fromisoformat(m.group(1))
    delta = (datetime.date.today() - last).days
    if delta < 1:
        return False, f'last consolidate {delta}d ago (need ≥1)'
    return True, f'{delta}d od last consolidate'


def last_consolidate_date():
    """Return last consolidate date z log.md lub None."""
    log = MEM / 'log.md'
    if not log.exists():
        return None
    txt = log.read_text()
    dates = re.findall(r'(\d{4}-\d{2}-\d{2}) consolidate', txt)
    if not dates:
        return None
    return max(datetime.date.fromisoformat(d) for d in dates)


def list_pending():
    """Dailies od last consolidate (inclusive jego daty+1)."""
    last = last_consolidate_date()
    dailies = list_dailies()
    if last is None:
        return dailies
    return [(d, p) for d, p in dailies if datetime.date.fromisoformat(d) > last]


def main():
    args = sys.argv[1:]
    if '--list-pending' in args:
        pend = list_pending()
        out = {
            'last_consolidate': str(last_consolidate_date()) if last_consolidate_date() else None,
            'pending_count': len(pend),
            'pending': [{'date': d, 'path': str(p.relative_to(BRAIN))} for d, p in pend],
            'topics': [{'slug': s, 'path': str(p.relative_to(BRAIN))} for s, p in list_topics()],
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    ok, reason = should_run()
    print(f'Trigger: {"YES" if ok else "no"} — {reason}')
    print(f'Dailies: {len(list_dailies())}')
    print(f'Topics: {len(list_topics())}')
    print(f'Pending od last consolidate: {len(list_pending())}')
    if not ok:
        return 0
    print('Next: invoke skill `consolidate-daily` (Claude does LLM pass + writes topics + logs).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
