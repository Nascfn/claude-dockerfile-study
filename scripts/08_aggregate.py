#!/usr/bin/env python3
"""Stage 8: collect every measurement into results/summary.{json,csv} and results/tables.md."""
import csv, json, os, statistics as st
VARIANTS = ['original', 'opus', 'sonnet', 'haiku']
LABEL = {'original': 'Original (human)', 'opus': 'Opus 5.5', 'sonnet': 'Sonnet 5.5', 'haiku': 'Haiku 5.5'}
sel = json.load(open('data/selection.json'))['selected']

def load(p):
    return json.load(open(p)) if os.path.exists(p) else None

def summarize_static(d):
    import sys; sys.path.insert(0, 'scripts')
    from scan_static import summarize
    return summarize(d) if os.path.exists(os.path.join(d, 'hadolint.json')) else None

rows = []
for r in sel:
    for v in VARIANTS:
        s = summarize_static(f'results/static/study/{r["slug"]}/{v}')
        b = load(f'results/image/{r["slug"]}/{v}/build.json')
        im = load(f'results/image/{r["slug"]}/{v}/image.json')
        g = load(f'results/generated/{r["slug"]}/{v}/run.json') if v != 'original' else None
        row = {'slug': r['slug'], 'repo': r['full_name'], 'group': r['group'], 'variant': v,
               'has_dockerfile': s is not None}
        if s:
            row.update({'hadolint_total': s['hadolint_total'], **{f'hadolint_{k}': n for k, n in s['hadolint'].items()},
                        'trivy_cfg_total': s['trivy_config_total'], **{f'trivy_cfg_{k.lower()}': n for k, n in s['trivy_config'].items()},
                        'static_score': s['score'], 'hadolint_codes': ' '.join(s['hadolint_codes']), 'trivy_ids': ' '.join(s['trivy_ids'])})
        row['build_ok'] = bool(b and b.get('ok'))
        row['build_seconds'] = b and b.get('seconds')
        if im and im.get('trivy_ok'):
            row.update({'runs_as_root': im['runs_as_root'], 'image_user': im['user'], 'size_mb': round(im['size_bytes'] / 1e6),
                        'has_healthcheck': im['has_healthcheck'], 'os': f"{im['os'].get('Family', '?')} {im['os'].get('Name', '')}".strip(),
                        **{f'vuln_{k.lower()}': n for k, n in im['vulns'].items()}, 'vuln_total': im['vulns_total'],
                        'vuln_crit_high': im['vulns']['CRITICAL'] + im['vulns']['HIGH'],
                        'vuln_fixable_crit_high': im['vulns_fixable']['CRITICAL'] + im['vulns_fixable']['HIGH'],
                        'vuln_os': im['vulns_by_class'].get('os-pkgs', 0), 'vuln_lang': im['vulns_by_class'].get('lang-pkgs', 0),
                        'secrets': im['secrets']})
        if g:
            u = g.get('usage') or {}
            row.update({'gen_model': ','.join(g.get('models_seen') or []), 'gen_turns': g.get('num_turns'), 'gen_seconds': g.get('wall_seconds'),
                        'gen_cost_usd': g.get('total_cost_usd'), 'gen_tool_calls': g.get('n_tool_calls'),
                        'gen_output_tokens': u.get('output_tokens'), 'gen_files_added': ' '.join(g.get('files_added') or []),
                        'gen_files_modified': len(g.get('files_modified') or []), 'gen_outside_access': len(g.get('outside_workspace_access') or [])})
        rows.append(row)

json.dump(rows, open('results/summary.json', 'w'), indent=1)
keys = []
for row in rows:
    for k in row:
        if k not in keys: keys.append(k)
with open('results/summary.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)

by = {(r['slug'], r['variant']): r for r in rows}
def mean(xs): xs = [x for x in xs if x is not None]; return round(st.mean(xs), 2) if xs else None
def med(xs): xs = [x for x in xs if x is not None]; return st.median(xs) if xs else None
def fmt(x): return '–' if x is None else (f'{x:.2f}'.rstrip('0').rstrip('.') if isinstance(x, float) else str(x))
out = []
def table(title, header, body):
    out.append(f'\n### {title}\n'); out.append('| ' + ' | '.join(header) + ' |'); out.append('|' + '|'.join(['---'] * len(header)) + '|')
    for line in body: out.append('| ' + ' | '.join(fmt(c) for c in line) + ' |')

def per_repo(metric, title, note=None):
    body = [[r['full_name']] + [by[(r['slug'], v)].get(metric) for v in VARIANTS] for r in sel]
    body.append(['**Mean**'] + [mean([by[(r['slug'], v)].get(metric) for r in sel]) for v in VARIANTS])
    table(title, ['Repository'] + [LABEL[v] for v in VARIANTS], body)
    if note: out.append('\n' + note)

per_repo('static_score', 'T1. Weighted static insecurity score per repository (lower is better)')
per_repo('hadolint_total', 'T2. Hadolint findings per repository')
per_repo('trivy_cfg_total', 'T3. Trivy misconfiguration findings per repository')
body = [[r['full_name']] + ['yes' if by[(r['slug'], v)]['build_ok'] else ('no Dockerfile' if not by[(r['slug'], v)]['has_dockerfile'] else '**no**') for v in VARIANTS] for r in sel]
body.append(['**Builds**'] + [f"{sum(by[(r['slug'], v)]['build_ok'] for r in sel)}/{len(sel)}" for v in VARIANTS])
table('T4. Does the image build?', ['Repository'] + [LABEL[v] for v in VARIANTS], body)
per_repo('vuln_crit_high', 'T5. Critical + High CVEs in the built image (Trivy image scan)', 'Blank cells are images that did not build.')
per_repo('vuln_total', 'T6. Total CVEs in the built image')
per_repo('size_mb', 'T7. Image size (MB)')
body = [[r['full_name']] + [('–' if by[(r['slug'], v)].get('runs_as_root') is None else ('root' if by[(r['slug'], v)]['runs_as_root'] else 'non-root')) for v in VARIANTS] for r in sel]
table('T8. User the container runs as', ['Repository'] + [LABEL[v] for v in VARIANTS], body)

# model-level summary
body = []
for v in VARIANTS:
    rs = [by[(r['slug'], v)] for r in sel]
    orig = [by[(r['slug'], 'original')] for r in sel]
    paired = [(o, a) for o, a in zip(orig, rs) if a.get('static_score') is not None]
    red = [100 * (o['static_score'] - a['static_score']) / o['static_score'] for o, a in paired if o['static_score']]
    better = sum(a['static_score'] < o['static_score'] for o, a in paired); worse = sum(a['static_score'] > o['static_score'] for o, a in paired)
    built = [a for a in rs if a.get('vuln_total') is not None]
    pv = [(o, a) for o, a in zip(orig, rs) if a.get('vuln_total') is not None and o.get('vuln_total') is not None]
    body.append([LABEL[v], mean([a.get('static_score') for a in rs]), mean([a.get('hadolint_total') for a in rs]), mean([a.get('trivy_cfg_total') for a in rs]),
                 '–' if v == 'original' else f'{mean(red)}%', '–' if v == 'original' else f'{better}/{worse}/{len(paired) - better - worse}',
                 f"{sum(a['build_ok'] for a in rs)}/{len(rs)}", f"{sum(1 for a in built if not a['runs_as_root'])}/{len(built)}",
                 med([a.get('vuln_crit_high') for a in built]), med([a.get('vuln_total') for a in built]),
                 '–' if v == 'original' else f"{sum(a['vuln_crit_high'] < o['vuln_crit_high'] for o, a in pv)}/{len(pv)}",
                 med([a.get('size_mb') for a in built])])
table('T9. Summary by Dockerfile author', ['Author', 'Mean static score', 'Mean Hadolint', 'Mean Trivy config', 'Mean score reduction', 'Better / worse / same vs original',
      'Builds', 'Non-root (of built)', 'Median Crit+High CVEs', 'Median total CVEs', 'Fewer Crit+High than original', 'Median size (MB)'], body)

# rule prevalence
from collections import Counter
rules = Counter()
per = {v: Counter() for v in VARIANTS}
for r in rows:
    for c in set((r.get('hadolint_codes') or '').split() + (r.get('trivy_ids') or '').split()):
        per[r['variant']][c] += 1; rules[c] += 1
titles = {}
for r in sel:
    for v in VARIANTS:
        t = load(f'results/static/study/{r["slug"]}/{v}/trivy_config.json') or {}
        for res in t.get('Results') or []:
            for m in res.get('Misconfigurations') or []: titles[m['ID']] = m['Title']
        for h in load(f'results/static/study/{r["slug"]}/{v}/hadolint.json') or []: titles.setdefault(h['code'], h['message'][:90])
body = [[c, titles.get(c, '')] + [per[v][c] for v in VARIANTS] for c, _ in sorted(rules.items(), key=lambda kv: (-per['original'][kv[0]], kv[0]))]
table(f'T10. Number of Dockerfiles (of {len(sel)}) that trigger each rule', ['Rule', 'What it flags'] + [LABEL[v] for v in VARIANTS], body)

# generation cost
body = []
for v in VARIANTS[1:]:
    rs = [by[(r['slug'], v)] for r in sel]
    body.append([LABEL[v], rs[0].get('gen_model'), mean([a.get('gen_seconds') for a in rs]), mean([a.get('gen_turns') for a in rs]), mean([a.get('gen_tool_calls') for a in rs]),
                 mean([a.get('gen_output_tokens') for a in rs]), round(sum(a.get('gen_cost_usd') or 0 for a in rs), 2),
                 sum(a.get('gen_files_modified') or 0 for a in rs), sum(a.get('gen_outside_access') or 0 for a in rs)])
table('T11. Generation effort per model', ['Model', 'Model ID reported', 'Mean seconds', 'Mean turns', 'Mean tool calls', 'Mean output tokens', 'Total cost (USD, as reported by the CLI)',
      'Existing files modified', 'Reads outside workspace'], body)
open('results/tables.md', 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
