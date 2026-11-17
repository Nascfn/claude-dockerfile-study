#!/usr/bin/env python3
"""Stage 2: build the candidate pool.

Walks data/candidates_raw.json in discovery order, shallow-clones each
repository that has a root Dockerfile, and applies purely mechanical filters.
Stops per language group once its quota is filled. Output: data/pool.json and
data/originals/<slug>/Dockerfile. Cloned code is only read, never executed.
"""
import json, os, re, subprocess, sys, shutil

WORK = os.environ.get('STUDY_WORK', '/home/user/work/repos')
QUOTA = {'python': 12, 'node': 12, 'go': 8, 'java': 6, 'ruby': 4, 'php': 4, 'rust': 4}   # 50 total
MAX_MB = 100
# Minimum base-image versions that count as "currently supported" (Nov 2026).
MIN_VER = {'python': (3, 10), 'node': (20,), 'golang': (1, 22), 'ruby': (3, 2), 'php': (8, 2),
           'rust': (1, 75), 'openjdk': (17,), 'eclipse-temurin': (17,), 'amazoncorretto': (17,),
           'zulu-openjdk': (17,), 'zulu-openjdk-alpine': (17,), 'maven': (3, 8), 'gradle': (8,), 'ubuntu': (22, 4), 'debian': (12,), 'alpine': (3, 19)}
DOCKERFILE_RE = re.compile(r'(^|/)(dockerfile(\..+)?|.+\.dockerfile)$', re.I)

def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def base_images(text):
    args, out = {}, []
    for line in text.splitlines():
        m = re.match(r'^\s*ARG\s+(\w+)=(.*)$', line, re.I)
        if m: args[m.group(1)] = m.group(2).strip().strip('"\'')
        m = re.match(r'^\s*FROM\s+(?:--\S+\s+)*(\S+)', line, re.I)
        if m:
            img = re.sub(r'\$\{?(\w+)(?::?-([^}]*))?\}?', lambda k: args.get(k.group(1)) or k.group(2) or '', m.group(1))
            out.append(img)
    return out

def old_runtime(images):
    """Return a reason string if any base image is below the supported floor."""
    for img in images:
        if re.search(r'cuda|nvidia/|pytorch/|tensorflow/', img, re.I):
            return f'GPU base image {img} (too large for the build sandbox)'
        name, _, tag = img.split('@')[0].rpartition(':') if ':' in img.split('/')[-1] else (img, '', '')
        short = name.split('/')[-1]
        if short in MIN_VER and tag:
            if short == 'debian':
                code = {'buster': 10, 'bullseye': 11, 'bookworm': 12, 'trixie': 13, 'stretch': 9}
                hit = [v for k, v in code.items() if k in tag]
                nums = (hit[0],) if hit else tuple(int(x) for x in re.findall(r'\d+', tag.split('-')[0])[:1])
            else:
                nums = tuple(int(x) for x in re.findall(r'\d+', tag.split('-')[0])[:len(MIN_VER[short])])
            if nums and nums < MIN_VER[short][:len(nums)]:
                return f'old base image {img}'
        m = re.search(r'(buster|stretch|bullseye|jessie)', tag or '')
        if m: return f'old distro in base image {img}'
    return None

def main():
    raw = json.load(open('data/candidates_raw.json'))
    os.makedirs(WORK, exist_ok=True)
    filled = {g: 0 for g in QUOTA}
    pool, rejected = [], []
    for c in raw['candidates']:
        g = c['group']
        if filled[g] >= QUOTA[g]:
            continue
        if not c.get('root_dockerfile'):
            rejected.append({'full_name': c['full_name'], 'reason': 'no root Dockerfile'}); continue
        slug = c['full_name'].replace('/', '__')
        dest = os.path.join(WORK, slug)
        if not os.path.isdir(os.path.join(dest, '.git')):
            shutil.rmtree(dest, ignore_errors=True)
            r = sh(['git', 'clone', '--quiet', '--depth', '1', f'https://github.com/{c["full_name"]}', dest], timeout=300)
            if r.returncode != 0:
                rejected.append({'full_name': c['full_name'], 'reason': 'clone failed'}); continue
        sha = sh(['git', '-C', dest, 'rev-parse', 'HEAD']).stdout.strip()
        date = sh(['git', '-C', dest, 'log', '-1', '--format=%cI']).stdout.strip()
        files = sh(['git', '-C', dest, 'ls-files']).stdout.splitlines()
        dfiles = [f for f in files if DOCKERFILE_RE.search(f)]
        size_mb = int(sh(['du', '-sm', '--exclude=.git', dest]).stdout.split()[0])
        reason = None
        try:
            text = open(os.path.join(dest, 'Dockerfile'), encoding='utf-8', errors='replace').read()
        except OSError:
            text, reason = '', 'root Dockerfile unreadable'
        n_instr = len([l for l in text.splitlines() if re.match(r'^\s*[A-Z]+\s', l)])
        if reason: pass
        elif dfiles != ['Dockerfile']: reason = f'not exactly one Dockerfile ({len(dfiles)} found)'
        elif os.path.exists(os.path.join(dest, '.gitmodules')): reason = 'uses git submodules'
        elif size_mb > MAX_MB: reason = f'too large ({size_mb} MB)'
        elif n_instr < 4: reason = 'trivial Dockerfile (<4 instructions)'
        else: reason = old_runtime(base_images(text))
        if reason:
            rejected.append({'full_name': c['full_name'], 'reason': reason})
            shutil.rmtree(dest, ignore_errors=True)
            continue
        os.makedirs(f'data/originals/{slug}', exist_ok=True)
        shutil.copy(os.path.join(dest, 'Dockerfile'), f'data/originals/{slug}/Dockerfile')
        filled[g] += 1
        pool.append({**c, 'slug': slug, 'commit': sha, 'commit_date': date, 'size_mb': size_mb,
                     'base_images': base_images(text), 'n_files': len(files)})
        print(f'[{g} {filled[g]}/{QUOTA[g]}] {c["full_name"]} {sha[:8]}', file=sys.stderr)
    json.dump({'quota': QUOTA, 'pool': pool, 'rejected': rejected}, open('data/pool.json', 'w'), indent=1)
    print('pool', len(pool), 'rejected', len(rejected), filled, file=sys.stderr)

if __name__ == '__main__':
    main()
