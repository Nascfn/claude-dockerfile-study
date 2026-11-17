#!/usr/bin/env python3
"""Stage 11: paired significance tests (n = 10 repositories, so treat as indicative only)."""
import json
from itertools import combinations
from scipy.stats import wilcoxon, binomtest
rows = json.load(open('results/summary.json'))
repos = []
for r in rows:
    if r['repo'] not in repos: repos.append(r['repo'])
by = {(r['repo'], r['variant']): r for r in rows}
LABEL = {'original': 'Original', 'opus': 'Opus 5.5', 'sonnet': 'Sonnet 5.5', 'haiku': 'Haiku 5.5'}
out = ['\n### T14. Paired tests across repositories\n',
       '| Comparison | Metric | Pairs | A lower / B lower / tie | Sign test p | Wilcoxon signed-rank p |', '|---|---|---|---|---|---|']
def test(a, b, metric, name):
    pairs = [(by[(r, a)].get(metric), by[(r, b)].get(metric)) for r in repos]
    pairs = [(x, y) for x, y in pairs if x is not None and y is not None]
    lo = sum(x < y for x, y in pairs); hi = sum(x > y for x, y in pairs); tie = len(pairs) - lo - hi
    sp = binomtest(min(lo, hi), lo + hi, 0.5).pvalue if lo + hi else 1.0
    try: wp = wilcoxon([x for x, _ in pairs], [y for _, y in pairs], zero_method='wilcox').pvalue
    except ValueError: wp = float('nan')
    out.append(f'| {LABEL[a]} (A) vs {LABEL[b]} (B) | {name} | {len(pairs)} | {lo} / {hi} / {tie} | {sp:.3f} | {wp:.3f} |')
for m in ('opus', 'sonnet', 'haiku'):
    test(m, 'original', 'static_score', 'static score')
for m in ('opus', 'sonnet', 'haiku'):
    test(m, 'original', 'vuln_crit_high', 'Critical+High CVEs')
for a, b in combinations(('opus', 'sonnet', 'haiku'), 2):
    test(a, b, 'static_score', 'static score')
for a, b in combinations(('opus', 'sonnet', 'haiku'), 2):
    test(a, b, 'vuln_crit_high', 'Critical+High CVEs')
open('results/tables_stats.md', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
