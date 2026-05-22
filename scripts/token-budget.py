#!/usr/bin/env python3
"""
Token-budget analyzer — wrapper na ccusage daily JSON.

Per-day breakdown: cost, total tokens, cache hit rate, anomalies.
Output: text table (default) lub JSON (--json).

Cache hit rate = cache_read / (cache_read + cache_creation + input).
Im wyższy tym mniejszy koszt input/cache_creation.

Usage:
  python3 scripts/token-budget.py [N_days=7] [--json]
"""
import sys, json, subprocess, datetime, statistics


def fetch(days: int) -> dict:
    since = (datetime.date.today() - datetime.timedelta(days=days - 1)).strftime('%Y%m%d')
    p = subprocess.run(
        ['ccusage', 'daily', '--json', '--since', since],
        capture_output=True, text=True, check=False,
    )
    if p.returncode != 0:
        sys.stderr.write(f'ccusage failed (exit {p.returncode}): {p.stderr[:200]}\n')
        sys.exit(1)
    return json.loads(p.stdout)


def hit_rate(d: dict) -> float:
    denom = d['cacheReadTokens'] + d['cacheCreationTokens'] + d['inputTokens']
    if denom == 0:
        return 0.0
    return d['cacheReadTokens'] / denom


def analyze(data: dict) -> dict:
    rows = data.get('daily', [])
    rows.sort(key=lambda x: x['date'])
    per_day = []
    for d in rows:
        per_day.append({
            'date': d['date'],
            'cost_usd': round(d['totalCost'], 2),
            'total_tokens': d['totalTokens'],
            'cache_read': d['cacheReadTokens'],
            'cache_creation': d['cacheCreationTokens'],
            'input': d['inputTokens'],
            'output': d['outputTokens'],
            'hit_rate': round(hit_rate(d) * 100, 1),
            'models': d.get('modelsUsed', []),
        })
    costs = [r['cost_usd'] for r in per_day]
    tokens = [r['total_tokens'] for r in per_day]
    hits = [r['hit_rate'] for r in per_day]
    summary = {
        'days_observed': len(per_day),
        'total_cost_usd': round(sum(costs), 2),
        'total_tokens': sum(tokens),
        'avg_cost_usd_per_day': round(statistics.mean(costs), 2) if costs else 0,
        'median_cost_usd_per_day': round(statistics.median(costs), 2) if costs else 0,
        'avg_hit_rate_pct': round(statistics.mean(hits), 1) if hits else 0,
        'min_hit_rate_pct': round(min(hits), 1) if hits else 0,
    }
    anomalies = []
    if len(costs) >= 3:
        med = statistics.median(costs)
        for r in per_day:
            if med > 0 and r['cost_usd'] > 2 * med:
                anomalies.append({'date': r['date'], 'cost_usd': r['cost_usd'], 'reason': f'>2x median ({med})'})
            if r['hit_rate'] < 50:
                anomalies.append({'date': r['date'], 'hit_rate': r['hit_rate'], 'reason': 'low cache hit (<50%)'})
    return {'per_day': per_day, 'summary': summary, 'anomalies': anomalies}


def text_report(a: dict) -> str:
    s = a['summary']
    out = []
    out.append(f'Token budget — last {s["days_observed"]}d')
    out.append('')
    out.append(f'{"date":<12} {"cost$":>8} {"tokens":>12} {"hit%":>6} models')
    out.append('-' * 60)
    fam = {'opus': 'O', 'sonnet': 'S', 'haiku': 'H'}
    for r in a['per_day']:
        models = ''.join(sorted({fam.get(m.split('-')[1], '?') for m in r['models'] if '-' in m}))
        out.append(f'{r["date"]:<12} {r["cost_usd"]:>8.2f} {r["total_tokens"]:>12,} {r["hit_rate"]:>6.1f} {models}')
    out.append('-' * 60)
    out.append(f'TOTAL: ${s["total_cost_usd"]} ({s["total_tokens"]:,} tokens) — avg ${s["avg_cost_usd_per_day"]}/d, hit {s["avg_hit_rate_pct"]}%')
    if a['anomalies']:
        out.append('')
        out.append('ANOMALIES:')
        for x in a['anomalies']:
            out.append(f'  ! {x["date"]} — {x["reason"]}')
    return '\n'.join(out)


def main():
    args = sys.argv[1:]
    as_json = '--json' in args
    days_args = [a for a in args if a.isdigit()]
    days = int(days_args[0]) if days_args else 7
    if days < 1 or days > 90:
        sys.stderr.write('days must be 1..90\n')
        sys.exit(2)
    raw = fetch(days)
    res = analyze(raw)
    if as_json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(text_report(res))
    return 0


if __name__ == '__main__':
    sys.exit(main())
