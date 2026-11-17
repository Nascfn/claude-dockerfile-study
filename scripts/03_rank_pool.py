#!/usr/bin/env python3
"""Stage 3: scan every pool Dockerfile statically and rank the pool.

Ranking rule (fixed in advance): descending weighted insecurity score from
scan_static.py; ties keep discovery order. Output: data/pool_ranking.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from scan_static import scan

pool = json.load(open('data/pool.json'))['pool']
rows = []
for i, p in enumerate(pool):
    s = scan(f'data/originals/{p["slug"]}/Dockerfile', f'results/static/pool/{p["slug"]}')
    rows.append({'order': i, 'slug': p['slug'], 'full_name': p['full_name'], 'group': p['group'],
                 'stars': p['stars'], 'commit': p['commit'], 'base_images': p['base_images'], **s})
rows.sort(key=lambda r: (-r['score'], r['order']))
for rank, r in enumerate(rows, 1): r['rank'] = rank
json.dump(rows, open('data/pool_ranking.json', 'w'), indent=1)
for r in rows:
    print(f"{r['rank']:>2} {r['score']:>3} {r['group']:<6} {r['full_name']:<45} H{r['hadolint_total']:>2} T{r['trivy_config_total']} {','.join(r['base_images'])[:50]}")
