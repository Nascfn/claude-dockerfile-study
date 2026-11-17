#!/usr/bin/env python3
"""Stage 4: select the study repositories.

Walks data/pool_ranking.json from the worst static score downwards and takes
the first N repositories whose ORIGINAL Dockerfile still builds today, with at
most CAP repositories per language group. A candidate whose original fails to
build is skipped and logged. Output: data/selection.json; the build and image
scan of each selected original is kept under results/image/<slug>/original/.
"""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from image_eval import evaluate

N, CAP, MIN_SCORE = 10, 3, 1
WORK = os.environ.get('STUDY_WORK', '/home/user/work/repos')
ranking = json.load(open('data/pool_ranking.json'))
state_path = 'data/selection.json'
state = json.load(open(state_path)) if os.path.exists(state_path) else {'selected': [], 'skipped': []}
done = {r['slug'] for r in state['selected'] + state['skipped']}
per_group = {}
for r in state['selected']: per_group[r['group']] = per_group.get(r['group'], 0) + 1
for r in ranking:
    if len(state['selected']) >= N: break
    if r['slug'] in done or r['score'] < MIN_SCORE: continue
    if per_group.get(r['group'], 0) >= CAP:
        state['skipped'].append({'slug': r['slug'], 'rank': r['rank'], 'reason': f'language cap ({CAP}) reached for {r["group"]}'})
        continue
    ctx = os.path.join(WORK, r['slug'])
    out = f'results/image/{r["slug"]}/original'
    build, summary = evaluate(ctx, os.path.join(ctx, 'Dockerfile'), f'study/{r["slug"].lower()}:original', out, timeout=1200)
    if build.get('ok') and summary and summary.get('trivy_ok'):
        state['selected'].append({'slug': r['slug'], 'full_name': r['full_name'], 'group': r['group'], 'rank': r['rank'],
                                  'score': r['score'], 'commit': r['commit'], 'stars': r['stars']})
        per_group[r['group']] = per_group.get(r['group'], 0) + 1
        print(f'SELECTED rank {r["rank"]} {r["full_name"]} ({build["seconds"]}s)', flush=True)
    else:
        tail = ' | '.join((build.get('log_tail') or [])[-4:])[-400:]
        state['skipped'].append({'slug': r['slug'], 'rank': r['rank'], 'reason': 'original Dockerfile does not build',
                                 'error': build.get('error'), 'log_tail': tail})
        os.makedirs('results/selection_build_failures', exist_ok=True)
        shutil.rmtree(f'results/selection_build_failures/{r["slug"]}', ignore_errors=True)
        shutil.move(out, f'results/selection_build_failures/{r["slug"]}')
        shutil.rmtree(f'results/image/{r["slug"]}', ignore_errors=True)
        print(f'skipped  rank {r["rank"]} {r["full_name"]}: {tail[-160:]}', flush=True)
    json.dump(state, open(state_path, 'w'), indent=1)
    os.system('docker builder prune -af >/dev/null 2>&1')
print('selected', len(state['selected']), 'skipped', len(state['skipped']))
