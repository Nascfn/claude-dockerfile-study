#!/usr/bin/env python3
"""Stage 7: scan and build every generated Dockerfile (same tools as the originals).

Build context for a generated Dockerfile = the ORIGINAL source tree at the
pinned commit, minus the container artifacts that were hidden from the model
(original Dockerfile, .dockerignore, compose files, docker/ scripts, CI), plus
the files the model wrote. The documentation edits made for the model's
reading copy are NOT applied to the build context, because some projects
consume their own docs at build time.
"""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from scan_static import scan
from image_eval import evaluate
WORK = os.environ.get('STUDY_WORK_ROOT', '/home/user/work')
MODELS = ['opus', 'sonnet', 'haiku']
DOC_EXT = ('.md', '.mdx', '.rst', '.adoc', '.txt')

def build_context(slug, model):
    ctx = f'{WORK}/buildctx/{slug}__{model}'
    shutil.rmtree(ctx, ignore_errors=True)
    shutil.copytree(f'{WORK}/repos/{slug}', ctx, symlinks=True)
    for rel in json.load(open(f'data/strip_reports/{slug}.json'))['deleted_paths']:
        if rel.rstrip('/') == '.git' or rel.lower().endswith(DOC_EXT): continue
        p = os.path.join(ctx, rel.rstrip('/'))
        if os.path.isdir(p) and not os.path.islink(p): shutil.rmtree(p)
        elif os.path.lexists(p): os.unlink(p)
    src = f'results/generated/{slug}/{model}/files'
    for d, _, files in os.walk(src):
        for f in files:
            sp = os.path.join(d, f); dp = os.path.join(ctx, os.path.relpath(sp, src))
            os.makedirs(os.path.dirname(dp), exist_ok=True); shutil.copy2(sp, dp)
    return ctx
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
        ctx = build_context(slug, m)
        b, s = evaluate(ctx, f'{ctx}/Dockerfile', f'study/{slug.lower()}:{m}', out, timeout=1200)
        shutil.rmtree(ctx, ignore_errors=True)
        print(slug, m, 'ok' if b.get('ok') else 'BUILD FAILED', b.get('seconds'), s and s.get('vulns'), flush=True)
        os.system('docker builder prune -af >/dev/null 2>&1')
        if shutil.disk_usage('/').free < 15e9:
            os.system('docker image prune -af >/dev/null 2>&1')
    os.system('docker image prune -af >/dev/null 2>&1')      # the sandbox disk is small: drop base images per repository
