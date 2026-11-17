#!/usr/bin/env python3
"""Stage 7: scan and build every generated Dockerfile (same tools as the originals)."""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from scan_static import scan
from image_eval import evaluate
WORK = os.environ.get('STUDY_WORK_ROOT', '/home/user/work')
MODELS = ['opus', 'sonnet', 'haiku']
for r in json.load(open('data/selection.json'))['selected']:
    slug = r['slug']
    scan(f'data/originals/{slug}/Dockerfile', f'results/static/study/{slug}/original')
    for m in MODELS:
        df = f'results/generated/{slug}/{m}/files/Dockerfile'
        out = f'results/image/{slug}/{m}'
        if not os.path.exists(df):
            print(slug, m, 'NO DOCKERFILE', flush=True); continue
        scan(df, f'results/static/study/{slug}/{m}')
        if os.path.exists(f'{out}/build.json'): continue
        ws = f'{WORK}/runs/{slug}/{m}/ws'
        b, s = evaluate(ws, f'{ws}/Dockerfile', f'study/{slug.lower()}:{m}', out, timeout=1200)
        print(slug, m, 'ok' if b.get('ok') else 'BUILD FAILED', b.get('seconds'), s and s.get('vulns'), flush=True)
        os.system('docker builder prune -af >/dev/null 2>&1')
