#!/usr/bin/env python3
"""Stage 5: make the stripped ("code only") copy of every selected repository."""
import json, os, subprocess, sys
WORK = os.environ.get('STUDY_WORK_ROOT', '/home/user/work')
os.makedirs('data/strip_reports', exist_ok=True)
for r in json.load(open('data/selection.json'))['selected']:
    out = subprocess.run([sys.executable, 'scripts/strip_hints.py', f'{WORK}/repos/{r["slug"]}', f'{WORK}/stripped/{r["slug"]}',
                          f'data/strip_reports/{r["slug"]}.json'], capture_output=True, text=True)
    print(r['slug'], out.stdout.strip(), out.stderr.strip()[-200:])
