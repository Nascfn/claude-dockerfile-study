#!/usr/bin/env python3
"""Create the "code only" copy of a repository that the models see.

usage: strip_hints.py <pristine_clone> <dest_dir> <report.json>
Rules (applied mechanically, identical for every repository):
  1. .git is not copied (history contains the original Dockerfile).
  2. Container-related files and directories are deleted by name (a directory
     called docker/ only at the repository root).
  3. In documentation files, every line that mentions Docker/containers is
     deleted, together with the fenced code block it sits in; documentation
     files with "docker" in their name are deleted outright.
Source code, build files and Makefiles are left untouched so the project still
builds; the number of residual mentions is recorded in the report.
"""
import fnmatch, json, os, re, shutil, sys

DROP_DIRS = {'.git', '.devcontainer', '.github', '.gitlab', '.circleci', 'docker', '.docker',
             'k8s', 'kubernetes', 'helm', '.kube'}
TOP_LEVEL_ONLY = {'docker', '.docker'}
DROP_FILES = ['Dockerfile', 'Dockerfile.*', '*.dockerfile', '*.Dockerfile', '.dockerignore', '*.dockerignore',
              'docker-compose*.yml', 'docker-compose*.yaml', 'compose*.yml', 'compose*.yaml',
              'docker-entrypoint*', 'entrypoint*.sh', 'docker-bake.hcl', '.hadolint.yaml', '.hadolint.yml',
              '.gitlab-ci.yml', '.travis.yml', 'Jenkinsfile', 'azure-pipelines.yml', 'bitbucket-pipelines.yml',
              'heroku.yml', 'fly.toml', 'render.yaml', 'railway.json', 'railway.toml', 'skaffold.yaml',
              'Tiltfile', 'Earthfile', 'captain-definition', 'cloudbuild.yaml', 'cloudbuild.yml',
              '.trivyignore', 'devcontainer.json']
DOC_EXT = ('.md', '.mdx', '.rst', '.adoc', '.txt')
HINT = re.compile(r'docker|\bcontainer(s|ized|ised|ization)?\b|podman|\bcompose\.ya?ml\b|kubernetes|\bk8s\b|\bhelm\b', re.I)
KEEP_TXT = re.compile(r'(^|/)(requirements[^/]*\.txt|constraints[^/]*\.txt|robots\.txt|CMakeLists\.txt|LICENSE[^/]*|NOTICE[^/]*)$', re.I)

def strip_doc(text):
    out, block, in_block, removed = [], [], False, 0
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith('```') or line.lstrip().startswith('~~~'):
            block.append(line)
            if in_block:
                if any(HINT.search(l) for l in block): removed += len(block)
                else: out.extend(block)
                block, in_block = [], False
            else:
                in_block = True
            continue
        if in_block:
            block.append(line); continue
        if HINT.search(line): removed += 1
        else: out.append(line)
    out.extend(block)
    return ''.join(out), removed

def main(src, dest, report_path):
    rep = {'deleted_paths': [], 'doc_lines_removed': {}, 'residual_mentions': {}}
    shutil.rmtree(dest, ignore_errors=True)
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        for d in list(dirs):
            is_helm_chart = os.path.exists(os.path.join(root, d, 'Chart.yaml'))
            named = d in DROP_DIRS or d.lower() in DROP_DIRS
            if d.lower() in TOP_LEVEL_ONLY and rel != '.':
                named = False                      # e.g. a Go package called "docker" is application code
            if named or is_helm_chart:
                rep['deleted_paths'].append(os.path.normpath(os.path.join(rel, d)) + '/'); dirs.remove(d)
        os.makedirs(os.path.join(dest, rel), exist_ok=True)
        for f in files:
            rp = os.path.normpath(os.path.join(rel, f))
            sp, dp = os.path.join(root, f), os.path.join(dest, rel, f)
            docker_doc = f.lower().endswith(DOC_EXT) and 'docker' in f.lower()
            if docker_doc or any(fnmatch.fnmatch(f, pat) or fnmatch.fnmatch(f.lower(), pat.lower()) for pat in DROP_FILES):
                rep['deleted_paths'].append(rp); continue
            if os.path.islink(sp):
                os.symlink(os.readlink(sp), dp); continue
            shutil.copy2(sp, dp)
            try:
                if os.path.getsize(sp) > 2_000_000: continue
                text = open(sp, encoding='utf-8').read()
            except (UnicodeDecodeError, OSError):
                continue
            if f.lower().endswith(DOC_EXT) and not KEEP_TXT.search(rp):
                new, n = strip_doc(text)
                if n:
                    open(dp, 'w', encoding='utf-8').write(new); rep['doc_lines_removed'][rp] = n
            else:
                n = len(re.findall(r'docker', text, re.I))
                if n: rep['residual_mentions'][rp] = n
    rep['n_deleted'] = len(rep['deleted_paths'])
    rep['n_doc_lines_removed'] = sum(rep['doc_lines_removed'].values())
    rep['n_residual_mentions'] = sum(rep['residual_mentions'].values())
    json.dump(rep, open(report_path, 'w'), indent=1)
    print(json.dumps({k: rep[k] for k in ('n_deleted', 'n_doc_lines_removed', 'n_residual_mentions')}))

if __name__ == '__main__':
    main(*sys.argv[1:4])
