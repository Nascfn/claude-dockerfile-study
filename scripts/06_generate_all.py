#!/usr/bin/env python3
"""Stage 6: run every (repository, model) generation, three sessions at a time."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
MODELS = ['opus', 'sonnet', 'haiku']
jobs = [(r['slug'], m) for r in json.load(open('data/selection.json'))['selected'] for m in MODELS
        if not os.path.exists(f'results/generated/{r["slug"]}/{m}/run.json')]
def run(job):
    p = subprocess.run([sys.executable, 'scripts/generate.py', *job], capture_output=True, text=True)
    print(p.stdout.strip() or p.stderr.strip()[-300:], flush=True)
with ThreadPoolExecutor(3) as ex: list(ex.map(run, jobs))
