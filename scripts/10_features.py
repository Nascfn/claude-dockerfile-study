#!/usr/bin/env python3
"""Stage 10: structural features of each Dockerfile (independent of the scanners)."""
import json, os, re
VARIANTS = ['original', 'opus', 'sonnet', 'haiku']
LABEL = {'original': 'Original (human)', 'opus': 'Opus 5.5', 'sonnet': 'Sonnet 5.5', 'haiku': 'Haiku 5.5'}
WORK = os.environ.get('STUDY_WORK_ROOT', '/home/user/work')
sel = json.load(open('data/selection.json'))['selected']

def features(text, has_ignore):
    lines = re.sub(r'\\\n', ' ', text).splitlines()
    ins = [l.strip() for l in lines if re.match(r'^\s*[A-Za-z]+\s', l) and not l.strip().startswith('#')]
    froms = [l for l in ins if l.upper().startswith('FROM ')]
    users = [l.split()[1] for l in ins if l.upper().startswith('USER ') and len(l.split()) > 1]
    last_from = froms[-1] if froms else ''
    img = [t for t in last_from.split()[1:] if not t.startswith('--')][0] if last_from else ''
    args = {m.group(1): m.group(2).strip().strip('"\'') for m in re.finditer(r'^\s*ARG\s+(\w+)=(.*)$', text, re.M | re.I)}
    img = re.sub(r'\$\{?(\w+)(?::?-([^}]*))?\}?', lambda k: args.get(k.group(1)) or k.group(2) or '', img)
    secret_args = [l for l in ins if re.match(r'^(ARG|ENV)\s', l, re.I) and re.search(r'(KEY|SECRET|TOKEN|PASSWORD|PASSWD)\w*\s*=?', l, re.I)]
    return {
        'instructions': len(ins), 'stages': len(froms), 'multi_stage': len(froms) > 1,
        'final_user_nonroot': bool(users) and users[-1].split(':')[0] not in ('root', '0'),
        'healthcheck': any(l.upper().startswith('HEALTHCHECK') and 'NONE' not in l.upper() for l in ins),
        'final_base': img, 'final_base_latest_or_untagged': (':' not in img.split('/')[-1] and '@' not in img and not img.startswith('$')) or img.endswith(':latest'),
        'any_digest_pin': any('@sha256:' in l for l in froms) or '@sha256:' in text,
        'small_final_base': bool(re.search(r'alpine|slim|distroless|scratch|chainguard|ubi-micro|busybox', img, re.I)),
        'apt_no_recommends': ('apt-get install' not in text) or ('--no-install-recommends' in text),
        'uses_apt_or_apk': bool(re.search(r'apt-get install|apk add', text)),
        'secret_named_arg_or_env': len(secret_args), 'dockerignore': has_ignore,
        'uses_add': any(l.upper().startswith('ADD ') for l in ins), 'init_process': bool(re.search(r'\btini\b|dumb-init', text)),
        'cache_mounts': '--mount=type=cache' in text,
    }

rows = []
for r in sel:
    for v in VARIANTS:
        if v == 'original':
            p = f'data/originals/{r["slug"]}/Dockerfile'; ign = os.path.exists(f'{WORK}/repos/{r["slug"]}/.dockerignore'); extra = []
        else:
            p = f'results/generated/{r["slug"]}/{v}/files/Dockerfile'
            run = json.load(open(f'results/generated/{r["slug"]}/{v}/run.json'))
            ign = '.dockerignore' in run['files_added']; extra = [f for f in run['files_added'] if f not in ('Dockerfile', '.dockerignore')]
        rows.append({'repo': r['full_name'], 'variant': v, 'extra_files': extra, **features(open(p, errors='replace').read(), ign)})
json.dump(rows, open('results/features.json', 'w'), indent=1)
n = len(sel)
keys = [('multi_stage', 'Multi-stage build'), ('final_user_nonroot', 'Final USER is non-root'), ('healthcheck', 'Defines a HEALTHCHECK'),
        ('small_final_base', 'Slim/Alpine/distroless final base'), ('final_base_latest_or_untagged', 'Final base is `latest` or untagged'),
        ('any_digest_pin', 'Pins an image by digest'), ('dockerignore', 'Has a .dockerignore'), ('init_process', 'Uses tini/dumb-init'),
        ('cache_mounts', 'Uses BuildKit cache mounts'), ('uses_add', 'Uses ADD')]
out = [f'\n### T12. Practices adopted (number of Dockerfiles out of {n})\n', '| Practice | ' + ' | '.join(LABEL[v] for v in VARIANTS) + ' |', '|---|---|---|---|---|']
for k, name in keys:
    out.append(f'| {name} | ' + ' | '.join(str(sum(1 for x in rows if x['variant'] == v and x[k])) for v in VARIANTS) + ' |')
out.append('| Mean instructions per Dockerfile | ' + ' | '.join(f"{sum(x['instructions'] for x in rows if x['variant'] == v) / n:.1f}" for v in VARIANTS) + ' |')
out.append('| Dockerfiles with secret-named ARG/ENV | ' + ' | '.join(str(sum(1 for x in rows if x['variant'] == v and x['secret_named_arg_or_env'])) for v in VARIANTS) + ' |')
out.append('| Runs that wrote extra files (entrypoint scripts etc.) | ' + ' | '.join(str(sum(1 for x in rows if x['variant'] == v and x['extra_files'])) for v in VARIANTS) + ' |')
out.append('\n### T13. Final-stage base image chosen\n'); out.append('| Repository | ' + ' | '.join(LABEL[v] for v in VARIANTS) + ' |'); out.append('|---|---|---|---|---|')
for r in sel:
    out.append(f'| {r["full_name"]} | ' + ' | '.join('`' + next(x['final_base'] for x in rows if x['repo'] == r['full_name'] and x['variant'] == v)[:60] + '`' for v in VARIANTS) + ' |')
open('results/tables_features.md', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
