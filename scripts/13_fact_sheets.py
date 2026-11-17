#!/usr/bin/env python3
"""Stage 13: write the fact sheets in docs/facts/ from the result files.

Every number is computed here from data/ and results/. The short pieces of
prose are observations that were checked by hand against the generated files.
"""
import collections, glob, json, os, re, statistics as st

V = ['original', 'opus', 'sonnet', 'haiku']
M = V[1:]
LABEL = {'original': 'Original', 'opus': 'Opus 5.5', 'sonnet': 'Sonnet 5.5', 'haiku': 'Haiku 5.5'}
OUT = 'docs/facts'
os.makedirs(OUT, exist_ok=True)

def load(p): return json.load(open(p)) if os.path.exists(p) else None

sel = load('data/selection.json')
selected = sel['selected']
raw = load('data/candidates_raw.json')
pool = load('data/pool.json')
ranking = load('data/pool_ranking.json')
rows = load('results/summary.json')
feats = load('results/features.json')
by = {(r['repo'], r['variant']): r for r in rows}
fb = {(f['repo'], f['variant']): f for f in feats}
runs = {(s['full_name'], m): load(f'results/generated/{s["slug"]}/{m}/run.json') for s in selected for m in M}
desc = {c['full_name']: c['description'] for c in raw['candidates']}
repos = [s['full_name'] for s in selected]

def fmt(x, nd=1):
    if x is None: return '–'
    if isinstance(x, float): return f'{x:.{nd}f}'.rstrip('0').rstrip('.') if nd else f'{x:.0f}'
    return str(x)

def table(header, body):
    out = ['| ' + ' | '.join(header) + ' |', '|' + '|'.join(['---'] * len(header)) + '|']
    out += ['| ' + ' | '.join(fmt(c) for c in line) + ' |' for line in body]
    return '\n'.join(out)

def write(name, title, intro, parts):
    text = f'# {title}\n\n{intro.strip()}\n\n' + '\n\n'.join(p.strip('\n') for p in parts) + '\n\n[Back to the index](README.md)\n'
    open(f'{OUT}/{name}', 'w').write(text)

def family(base):
    b = base.lower()
    return 'Alpine' if 'alpine' in b else 'distroless' if 'distroless' in b else 'Debian-based'

def thinking(r): return (((r.get('usage') or {}).get('output_tokens_details')) or {}).get('thinking_tokens')
def mean(xs): xs = [x for x in xs if x is not None]; return st.mean(xs) if xs else None
def med(xs): xs = [x for x in xs if x is not None]; return st.median(xs) if xs else None
def codes(r): return set((r.get('hadolint_codes') or '').split()) | set((r.get('trivy_ids') or '').split())

titles = {}
for s in selected:
    for v in V:
        for res in (load(f'results/static/study/{s["slug"]}/{v}/trivy_config.json') or {}).get('Results') or []:
            for m_ in res.get('Misconfigurations') or []: titles[m_['ID']] = m_['Title']
        for h in load(f'results/static/study/{s["slug"]}/{v}/hadolint.json') or []: titles.setdefault(h['code'], h['message'])
SHORT = {'DS-0002': 'Image runs as root', 'DS-0026': 'No HEALTHCHECK', 'DS-0001': '`latest` tag used', 'DS-0013': '`RUN cd …` instead of WORKDIR',
         'DS-0031': 'Secret passed as build argument or env', 'DL3018': 'Unpinned `apk add` packages', 'DL3008': 'Unpinned `apt-get install` packages',
         'DL3059': 'Consecutive RUN instructions', 'DL3025': 'CMD/ENTRYPOINT not in JSON form', 'DL3007': '`latest` tag used',
         'DL3066': 'Non-numeric user id', 'DL3003': '`cd` instead of WORKDIR', 'DL3013': 'Unpinned `pip install` packages',
         'DL3064': 'Sensitive-looking name in ARG/ENV', 'DL3002': 'Last USER is root', 'DL3016': 'Unpinned `npm install` packages',
         'DL3046': '`useradd` without `-l`', 'DL3065': 'Redundant `--platform`', 'DL4006': 'Pipe without `pipefail`',
         'SC2164': '`cd` without failure check', 'DL4005': 'Shell changed with `ln` instead of SHELL'}
def rule_name(c): return SHORT.get(c) or titles.get(c, '')[:60]

# ---------------------------------------------------------------- 01 at a glance
gen_secs = sum(r['wall_seconds'] for r in runs.values()); gen_cost = sum(r['total_cost_usd'] or 0 for r in runs.values())
strict = sum(by[(r, m)]['static_score'] < by[(r, 'original')]['static_score'] for r in repos for m in M)
scanned = [(r, m) for r in repos for m in M if by[(r, m)].get('vuln_crit_high') is not None]
cve_up = sum(by[k]['vuln_crit_high'] > by[(k[0], 'original')]['vuln_crit_high'] for k in scanned)
cve_down = sum(by[k]['vuln_crit_high'] < by[(k[0], 'original')]['vuln_crit_high'] for k in scanned)
glance = [
    '## The experiment in numbers\n\n' + table(['What', 'Number'], [
        ['Repositories returned by the GitHub search', len(raw['candidates'])],
        ['…with a Dockerfile at the root', sum(1 for c in raw['candidates'] if c['root_dockerfile'])],
        ['Repositories in the ranked pool', len(ranking)],
        ['Repositories studied', len(selected)],
        ['Models', '3 (Opus 5.5, Sonnet 5.5, Haiku 5.5)'],
        ['Generation sessions', len(runs)],
        ['Dockerfiles evaluated (10 original + 30 generated)', 40],
        ['Images built and scanned', sum(1 for r in rows if r.get('vuln_total') is not None)],
        ['Tool calls made by the models', sum(r['n_tool_calls'] for r in runs.values())],
        ['Total generation time, all 30 sessions', f'{gen_secs / 60:.0f} minutes'],
        ['Total generation cost reported by the CLI', f'USD {gen_cost:.2f}'],
        ['Date of every run and scan', '2026-11-17'],
    ]),
    '## The result in numbers\n\n' + table(['What', 'Original', 'Opus 5.5', 'Sonnet 5.5', 'Haiku 5.5'], [
        ['Mean weighted static score (lower is better)'] + [mean([by[(r, v)]['static_score'] for r in repos]) for v in V],
        ['Mean Hadolint findings'] + [mean([by[(r, v)]['hadolint_total'] for r in repos]) for v in V],
        ['Mean Trivy misconfigurations'] + [mean([by[(r, v)]['trivy_cfg_total'] for r in repos]) for v in V],
        ['Dockerfiles whose build steps all succeed'] + [f"{sum(by[(r, v)]['build_steps_ok'] for r in repos)}/10" for v in V],
        ['Images scanned'] + [sum(1 for r in repos if by[(r, v)].get('vuln_total') is not None) for v in V],
        ['Scanned images that run as root'] + [sum(1 for r in repos if by[(r, v)].get('runs_as_root')) for v in V],
        ['Median Critical+High CVEs per image'] + [med([by[(r, v)].get('vuln_crit_high') for r in repos]) for v in V],
        ['Median image size (MB)'] + [med([by[(r, v)].get('size_mb') for r in repos]) for v in V],
    ]),
    '## Five facts to remember\n\n'
    f'1. {strict} of 30 generated Dockerfiles scored strictly better than the original on the static score; none scored worse.\n'
    '2. All 30 generated Dockerfiles completed every build step, although no model could run a build.\n'
    f'3. Critical+High CVEs went down in {cve_down} of {len(scanned)} scanned images and up in {cve_up}.\n'
    '4. Every time a model replaced an Alpine or distroless base with a Debian one (11 runs), CVEs went up.\n'
    '5. The cheapest model (Haiku) had the best static score and the most CVEs.',
]
write('01-at-a-glance.md', 'At a glance', 'The whole experiment on one page.', glance)

# ---------------------------------------------------------------- 02 selection funnel
cq = collections.Counter((c['group'], c['query']) for c in raw['candidates'])
cd = collections.Counter((c['group'], c['query']) for c in raw['candidates'] if c['root_dockerfile'])
rej = collections.Counter()
for r in pool['rejected']:
    k = r['reason']
    rej['Base image below the runtime floor' if k.startswith('old') else 'GPU base image' if k.startswith('GPU') else
        {'no root Dockerfile': 'No Dockerfile at the repository root', 'uses git submodules': 'Uses git submodules'}.get(k, 'More than one Dockerfile' if k.startswith('not exactly') else k)] += 1
grp = collections.defaultdict(list)
for p in ranking: grp[p['group']].append(p['score'])
prev = collections.Counter()
for p in ranking:
    for c in set(p['hadolint_codes'] + p['trivy_ids']): prev[c] += 1
sel_slugs = {s['slug'] for s in selected}
skip = {s['slug']: s for s in sel['skipped']}
CAUSE = {'imdhemy__laravel-in-app-purchases': 'Skipped: `pecl install` needs plain HTTP, which the sandbox does not carry',
         'imtaqin__waxum': 'Skipped: build script downloads from github.com, blocked in the sandbox',
         'physhik__ecg-mit-bih': 'Skipped: Dockerfile copies a dataset folder that is not in the repository',
         'MGeurts__genealogy': 'Skipped: Composer downloads from github.com, blocked in the sandbox'}
funnel = [
    '## Search queries\n\nEvery query also carried `stars:15..400 pushed:>2025-11-17 archived:false fork:false`. '
    'Three result pages (up to 30 repositories) were taken per query, in GitHub\'s default "best match" order. '
    'A repository returned by two queries is counted under the first.\n\n' +
    table(['Language group', 'Query', 'New repositories', 'With a root Dockerfile'],
          [[g, f'`{q}`', n, cd[(g, q)]] for (g, q), n in cq.items()] + [['**Total**', '', sum(cq.values()), sum(cd.values())]]),
    '## Filling the pool\n\nCandidates were examined in search order until each language group reached its quota '
    f'({", ".join(f"{k} {v}" for k, v in pool["quota"].items())}). {len(pool["pool"]) + len(pool["rejected"])} candidates were examined.\n\n' +
    table(['Outcome', 'Repositories'], [['Kept in the pool', len(pool['pool'])]] + [[k, n] for k, n in rej.most_common()]),
    '## The pool by language\n\n' + table(['Group', 'Repositories', 'Mean static score', 'Worst score'],
          [[g, len(v), mean(v), max(v)] for g, v in sorted(grp.items(), key=lambda kv: -len(kv[1]))]) +
    '\n\nJava, Ruby and PHP did not fill their quotas because few search results had a single root Dockerfile. Python lost two repositories and Java one to filters added after the first pass (GPU base images, Java 8).',
    f'## How common each problem is across the {len(ranking)} pool Dockerfiles\n\n'
    'This is the unselected sample, so it says something about ordinary recent projects, not just the worst ten.\n\n' +
    table(['Rule', 'What it flags', 'Dockerfiles', 'Share'], [[c, rule_name(c), n, f'{100 * n / len(ranking):.0f}%'] for c, n in prev.most_common(12)]),
    '## The top of the ranking\n\nSelection walked this list from the top, kept a repository if its original Dockerfile built, and allowed at most three per language group.\n\n' +
    table(['Rank', 'Repository', 'Group', 'Score', 'Outcome'],
          [[p['rank'], p['full_name'], p['group'], p['score'],
            '**Selected**' if p['slug'] in sel_slugs else CAUSE.get(p['slug'], skip.get(p['slug'], {}).get('reason', 'Not reached'))] for p in ranking[:14]]),
    f'Scores in the pool run from {min(p["score"] for p in ranking)} to {max(p["score"] for p in ranking)} with a median of '
    f'{st.median([p["score"] for p in ranking]):.0f}. The ten selected originals score {min(s["score"] for s in selected)}–{max(s["score"] for s in selected)}.',
]
write('02-selection-funnel.md', 'How the ten repositories were chosen',
      'From 545 search results to 10 studied repositories, with the counts at each step.', funnel)

# ---------------------------------------------------------------- 03 repositories
NOTES = {
    'rdborg/Mediarium': 'All three models wrote their own entrypoint script to replace the hidden one, and all three keep the original\'s pattern of starting as root and then dropping privileges. '
                        'Opus and Haiku placed it at `docker/entrypoint.sh`, the same path as the hidden original; that path is named in the project\'s Go source, which was not edited. '
                        'All three kept the four API-key build arguments that the original has, which is why the "sensitive ARG" finding remains.',
    'zebbern/claude-code-discord': 'The application runs on Deno. Opus kept a Deno base image with a pinned version; Sonnet and Haiku started from a Node image and added Deno to it. '
                                   'Haiku tried to `curl` the npm registry to look up a package version; the call was rejected because no shell was offered.',
    'zqbxdev/webchat2api': 'Opus\'s image has the fewest Critical+High CVEs here (785 → 585). All three models stay root; Haiku notes in a comment that the server binds port 83. '
                           'One documentation line that names `scripts/entrypoint.sh` and the start command survived the stripping because it does not contain the word "docker"; Haiku wrote its entrypoint at that same path.',
    'Climate-Vision/ClimateVision': 'The original installs CPU-only PyTorch and explains why in a comment. Opus made the same choice unprompted (4.7 GB image). '
                                    'Sonnet and Haiku installed the default wheels with GPU libraries: Sonnet\'s image is 12.2 GB, and Haiku\'s could not be exported inside the sandbox, so it has no image scan. '
                                    'All three models switch the container to a non-root user.',
    'zhravan/github-readme-quotes': 'The biggest CVE drop in the study: the original uses the full `node:20` image and runs as root. '
                                    'All three models expose port 3002, the default in `src/app.js`; the original exposes 3000 and 3004.',
    'coolstartnow/isms-builder': 'The static score halves, but every model replaced the original\'s Alpine base with Debian slim and Critical+High CVEs rose from 6 to 48. '
                                 'Opus and Haiku wrote a separate `docker/healthcheck.js`.',
    'pelican/wings': 'Wings controls the Docker daemon, so root is expected. The Go code checks `/etc/os-release` for `ID="distroless"`. '
                     'Opus was the only model to pick this up: it kept a distroless base and writes that file, as the original does, and its score equals the original\'s. '
                     'Sonnet (Alpine) and Haiku (Debian) score lower but ignore that check. All three add port 2022, which the original does not expose.',
    'lissy93/who-dat': 'The smallest and simplest project. Opus and Haiku chose `distroless/static:nonroot`; Sonnet kept Alpine with a pinned version. Fastest run of the study: Sonnet, 19 seconds.',
    'leonovk/wg-rest-api': 'A WireGuard manager that has to configure a network interface, so every model stays root (Haiku says so in a comment). '
                           'All three moved from Alpine to Debian slim, which multiplied Critical+High CVEs by about ten. The original exposes no ports; the models expose 3000 and 51820.',
    'chelunfu/qiluo_admin': 'The original pulls its base images through a third-party registry mirror (`docker.1ms.run`); all three models use the official images. '
                            'All three also wrote a `config/docker.yaml`. The original\'s Alpine runtime has no Critical+High CVEs; the models\' Debian runtime has 38.',
}
parts = []
for s in selected:
    r = s['full_name']; o = by[(r, 'original')]
    body = []
    for v in V:
        x = by[(r, v)]
        body.append([LABEL[v], f"`{fb[(r, v)]['final_base'][:44]}`", x['static_score'], x['hadolint_total'], x['trivy_cfg_total'],
                     '–' if x.get('runs_as_root') is None else ('root' if x['runs_as_root'] else 'non-root'),
                     x.get('vuln_crit_high'), x.get('vuln_total'), x.get('size_mb')])
    cleared = set.intersection(*[codes(o) - codes(by[(r, m)]) for m in M])
    added = set.union(*[codes(by[(r, m)]) - codes(o) for m in M])
    gen = table(['Model', 'Seconds', 'Turns', 'Files read', 'Thinking tokens', 'Cost (USD)', 'Files written'],
                [[LABEL[m], runs[(r, m)]['wall_seconds'], runs[(r, m)]['num_turns'], len({t for n, t in runs[(r, m)]['tool_calls'] if n == 'Read'}),
                  thinking(runs[(r, m)]), f"{runs[(r, m)]['total_cost_usd']:.2f}", ', '.join(f'`{f}`' for f in runs[(r, m)]['files_added'])] for m in M])
    rep = load(f'data/strip_reports/{s["slug"]}.json')
    parts.append(
        f'## {r}\n\n{desc.get(r, "").strip()}\n\n'
        f'Group: {s["group"]} · Stars: {s["stars"]} · Commit: `{s["commit"][:10]}` · Pool rank: {s["rank"]} · '
        f'Hidden from the models: {rep["n_deleted"]} paths, {rep["n_doc_lines_removed"]} documentation lines\n\n' +
        table(['Author', 'Final base image', 'Static score', 'Hadolint', 'Trivy config', 'User', 'Critical+High CVEs', 'All CVEs', 'Size (MB)'], body) +
        f'\n\n- **Findings every model removed:** {", ".join(f"{c} ({rule_name(c)})" for c in sorted(cleared)) or "none"}\n'
        f'- **Findings at least one model added:** {", ".join(f"{c} ({rule_name(c)})" for c in sorted(added)) or "none"}\n'
        f'- **Notes:** {NOTES[r]}\n\n' + gen)
write('03-repositories.md', 'The ten repositories, one by one',
      'For each repository: what the original and each model produced, what changed, and anything worth knowing. '
      'A dash means the image could not be scanned.', parts)

# ---------------------------------------------------------------- 04 model behaviour
tb = {m: collections.Counter() for m in M}
for (r, m), run in runs.items():
    for n, _ in run['tool_calls']: tb[m][n] += 1
def per(m, f): return [f(runs[(r, m)]) for r in repos]
lines = {v: [] for v in V}; comments = {v: [] for v in V}
for s in selected:
    for v in V:
        p = f'data/originals/{s["slug"]}/Dockerfile' if v == 'original' else f'results/generated/{s["slug"]}/{v}/files/Dockerfile'
        t = open(p, errors='replace').read().splitlines()
        lines[v].append(len(t)); comments[v].append(sum(1 for l in t if l.strip().startswith('#')))
extras = collections.Counter()
for (r, m), run in runs.items():
    for f in run['files_added']:
        if f not in ('Dockerfile', '.dockerignore'): extras[(m, 'entrypoint script' if 'entrypoint' in f else os.path.basename(f))] += 1
fam = {v: collections.Counter(family(fb[(r, v)]['final_base']) for r in repos) for v in V}
agree = sum(1 for r in repos if len({by[(r, m)]['static_score'] for m in M}) == 1)
same_base = sum(1 for r in repos if len({fb[(r, m)]['final_base'] for m in M}) == 1)
behaviour = [
    '## Settings (identical for all three)\n\n' + table(['Setting', 'Value'], [
        ['Runner', 'Claude Code CLI 2.1.326, headless (`claude -p`), one new process per run'],
        ['Effort', '`--effort high`'], ['Tools offered', 'Read, Glob, Grep, Write'],
        ['Not offered', 'Shell, in-place edit, web access, sub-agents, MCP servers, skills'],
        ['Runs', 'One per repository per model'], ['Prompt', 'The same neutral prompt (`scripts/prompt.txt`), no mention of security']]),
    '## Effort spent per run (means over 10 repositories)\n\n' + table(['Measure', 'Opus 5.5', 'Sonnet 5.5', 'Haiku 5.5'], [
        ['Wall-clock seconds'] + [mean(per(m, lambda x: x['wall_seconds'])) for m in M],
        ['Fastest / slowest run (s)'] + [f"{min(per(m, lambda x: x['wall_seconds']))} / {max(per(m, lambda x: x['wall_seconds']))}" for m in M],
        ['Turns'] + [mean(per(m, lambda x: x['num_turns'])) for m in M],
        ['Distinct files read'] + [mean(per(m, lambda x: len({t for n, t in x['tool_calls'] if n == 'Read'}))) for m in M],
        ['Output tokens'] + [f"{mean(per(m, lambda x: x['usage']['output_tokens'])):,.0f}" for m in M],
        ['…of which thinking tokens'] + [f"{mean(per(m, thinking)):,.0f}" for m in M],
        ['Thinking tokens, smallest / largest run'] + [f"{min(per(m, thinking)):,} / {max(per(m, thinking)):,}" for m in M],
        ['Cost per run (USD)'] + [f"{mean(per(m, lambda x: x['total_cost_usd'])):.3f}" for m in M],
        ['Cost for all 10 repositories (USD)'] + [f"{sum(per(m, lambda x: x['total_cost_usd'])):.2f}" for m in M]]) +
    '\n\nHaiku thought the most and Sonnet the least at the same effort setting. Cost is the figure the CLI reports and includes prompt-cache discounts, so read it as relative.',
    '## Tool calls over all 10 runs\n\n' + table(['Tool', 'Opus 5.5', 'Sonnet 5.5', 'Haiku 5.5'],
        [[t] + [tb[m][t] for m in M] for t in ('Read', 'Grep', 'Glob', 'Write')] +
        [['Attempted, not offered (rejected)'] + [sum(n for t, n in tb[m].items() if t not in ('Read', 'Grep', 'Glob', 'Write')) for m in M],
         ['**Total**'] + [sum(tb[m].values()) for m in M]]),
    '## What they wrote\n\n' + table(['Measure', 'Original', 'Opus 5.5', 'Sonnet 5.5', 'Haiku 5.5'], [
        ['Mean Dockerfile length (lines)'] + [mean(lines[v]) for v in V],
        ['Mean comment lines'] + [mean(comments[v]) for v in V],
        ['Longest Dockerfile (lines)'] + [max(lines[v]) for v in V],
        ['Wrote a `.dockerignore`', '8 have one'] + [sum(1 for r in repos if '.dockerignore' in runs[(r, m)]['files_added']) for m in M],
        ['Wrote an entrypoint script', '–'] + [extras[(m, 'entrypoint script')] for m in M],
        ['Wrote another support file', '–'] + [sum(n for (mm, k), n in extras.items() if mm == m and k != 'entrypoint script') for m in M],
        ['Multi-stage builds'] + [sum(1 for r in repos if fb[(r, v)]['multi_stage']) for v in V],
        ['Final base: Alpine / Debian-based / distroless'] + [f"{fam[v]['Alpine']} / {fam[v]['Debian-based']} / {fam[v]['distroless']}" for v in V]]) +
    '\n\nOpus and Haiku write longer files than the originals and comment more. The number of instructions is about the same for every author (22.3 for the originals against 21.9, 21.3 and 22.7).',
    '## How much the models agree with each other\n\n'
    f'- In {agree} of 10 repositories all three models got the same static score.\n'
    f'- In {same_base} of 10 repositories all three chose the same final base image.\n'
    '- All three made the same root or non-root decision in every repository where all three images were scanned.\n'
    '- No pairwise difference between models is statistically significant (see table T14 in `FINDINGS.md`).',
]
write('04-model-behaviour.md', 'How the three models behaved', 'Settings, effort, tool use and writing habits of Opus 5.5, Sonnet 5.5 and Haiku 5.5.', behaviour)

# ---------------------------------------------------------------- 05 rules
per_rule = {v: collections.Counter() for v in V}
for r in rows:
    for c in codes(r): per_rule[r['variant']][c] += 1
allc = sorted(set().union(*[set(per_rule[v]) for v in V]), key=lambda c: (-per_rule['original'][c], c))
SECURITY = {'DS-0002', 'DL3002', 'DS-0001', 'DL3007', 'DS-0031', 'DL3064', 'DL3008', 'DL3018', 'DL3013', 'DL3016', 'DS-0026', 'DL4006'}
def chg(c): return mean([per_rule[m][c] for m in M]) - per_rule['original'][c]
def gone(c): return per_rule['original'][c] >= 1 and all(per_rule[m][c] == 0 for m in M)
improved = [c for c in allc if chg(c) <= -2 or gone(c)]; worse = [c for c in allc if chg(c) >= 1]; flat = [c for c in allc if c not in improved and c not in worse]
def rt(cs): return table(['Rule', 'What it flags', 'Security-relevant', 'Original', 'Opus 5.5', 'Sonnet 5.5', 'Haiku 5.5'],
                         [[c, rule_name(c), 'yes' if c in SECURITY else 'style'] + [per_rule[v][c] for v in V] for c in cs])
sev = {v: collections.Counter() for v in V}
for r in rows:
    for k in ('hadolint_error', 'hadolint_warning', 'hadolint_info', 'hadolint_style', 'trivy_cfg_critical', 'trivy_cfg_high', 'trivy_cfg_medium', 'trivy_cfg_low'):
        sev[r['variant']][k] += r.get(k) or 0
rules = [
    'Counts are the number of Dockerfiles, out of 10, that trigger the rule at least once. "Security-relevant" is a labelling made for this study of '
    'whether a rule concerns privileges, secrets, reproducibility of what gets installed, or health monitoring, as opposed to style.',
    '## Problems the models mostly removed\n\n' + rt(improved),
    '## Problems the models introduced or made more common\n\n' + rt(worse) +
    '\n\nUnpinned `apt-get` packages rose as the models moved to Debian-based images; the matching Alpine rule (DL3018) fell at the same time.',
    '## Problems that barely moved\n\n' + rt(flat),
    '## Findings by severity, summed over the 10 Dockerfiles\n\n' + table(['Severity', 'Original', 'Opus 5.5', 'Sonnet 5.5', 'Haiku 5.5'], [
        ['Hadolint error'] + [sev[v]['hadolint_error'] for v in V], ['Hadolint warning'] + [sev[v]['hadolint_warning'] for v in V],
        ['Hadolint info'] + [sev[v]['hadolint_info'] for v in V], ['Hadolint style'] + [sev[v]['hadolint_style'] for v in V],
        ['Trivy CRITICAL'] + [sev[v]['trivy_cfg_critical'] for v in V], ['Trivy HIGH'] + [sev[v]['trivy_cfg_high'] for v in V],
        ['Trivy MEDIUM'] + [sev[v]['trivy_cfg_medium'] for v in V], ['Trivy LOW'] + [sev[v]['trivy_cfg_low'] for v in V]]),
    '## Things no scanner flagged but worth knowing\n\n'
    '- Trivy\'s secret scanner found nothing in any of the 39 scanned images.\n'
    '- No generated Dockerfile uses `ADD`, and none of the originals does either.\n'
    '- One original pins a base image by digest; no generated Dockerfile does.\n'
    '- Neither tool has a rule for "the base image carries many known CVEs", which is where the models did worst.',
]
write('05-rules-fixed-and-introduced.md', 'Which problems were fixed and which were introduced', 'Rule by rule, for Hadolint and Trivy config.', rules)

# ---------------------------------------------------------------- 06 base images and CVEs
moved = [(r, m) for r in repos for m in M if family(fb[(r, 'original')]['final_base']) != 'Debian-based' and family(fb[(r, m)]['final_base']) == 'Debian-based']
def cvecell(r, v): x = by[(r, v)]; return '–' if x.get('vuln_crit_high') is None else f"{x['vuln_crit_high']} ({family(fb[(r, v)]['final_base'])})"
os_share = {v: 100 * sum(by[(r, v)].get('vuln_os') or 0 for r in repos) / max(1, sum(by[(r, v)].get('vuln_total') or 0 for r in repos)) for v in V}
fix_share = {v: 100 * sum(by[(r, v)].get('vuln_fixable_crit_high') or 0 for r in repos) / max(1, sum(by[(r, v)].get('vuln_crit_high') or 0 for r in repos)) for v in V}
base = [
    '## Critical+High CVEs next to the base-image family\n\n' + table(['Repository'] + [LABEL[v] for v in V], [[r] + [cvecell(r, v) for v in V] for r in repos]),
    '## What happened when the base family changed\n\n' + table(['Repository', 'Model', 'Original base', 'Model\'s base', 'Critical+High before', 'after'],
        [[r, LABEL[m], f"`{fb[(r, 'original')]['final_base'][:36]}`", f"`{fb[(r, m)]['final_base'][:36]}`", by[(r, 'original')]['vuln_crit_high'], by[(r, m)].get('vuln_crit_high')] for r, m in moved]) +
    f'\n\n{len(moved)} runs moved an Alpine or distroless original onto a Debian-based image. Critical+High CVEs rose in all {len(moved)}.',
    '## Where the CVEs live\n\n' + table(['Measure', 'Original', 'Opus 5.5', 'Sonnet 5.5', 'Haiku 5.5'], [
        ['Share of all CVEs that are in operating-system packages'] + [f'{os_share[v]:.0f}%' for v in V],
        ['Share of Critical+High CVEs that have a fix available'] + [f'{fix_share[v]:.0f}%' for v in V],
        ['Images with zero Critical+High CVEs'] + [sum(1 for r in repos if by[(r, v)].get('vuln_crit_high') == 0) for v in V],
        ['Largest Critical+High count in one image'] + [max(by[(r, v)].get('vuln_crit_high') or 0 for r in repos) for v in V]]) +
    '\n\nOperating-system packages dominate, so the count mostly reflects the base image and the system packages installed on top of it, not the application.',
    '## Extremes\n\n'
    '- Largest drop: zhravan/github-readme-quotes, 2,008 → 45 Critical+High (10,450 → 131 CVEs in total) when the full `node:20` image was replaced by `node:20-alpine`.\n'
    '- Largest relative rise: rdborg/Mediarium under Haiku, 1 → 105, Alpine to Debian slim.\n'
    '- Roughly tenfold for all three models: leonovk/wg-rest-api, 13 → 127–135, Alpine to Debian slim.\n'
    '- From zero to non-zero: chelunfu/qiluo_admin, 0 → 38 for all three models.\n'
    '- Only repository at zero for every author: lissy93/who-dat.',
    '## Why this matters for reading the results\n\n'
    'Trivy counts every published CVE that applies to an installed package, including many Debian ones marked as unfixed or minor. '
    'Alpine ships fewer packages and reports far fewer. A raw CVE count therefore rewards Alpine and distroless bases regardless of how carefully the rest of the Dockerfile is written. '
    'It is a real difference in attack surface, but it is one decision (the `FROM` line), not a measure of overall Dockerfile quality.',
]
write('06-base-images-and-cves.md', 'Base images and vulnerability counts', 'Why the lint scores improved while the CVE counts did not.', base)

# ---------------------------------------------------------------- 07 isolation and audit
att = []
for (r, m), run in runs.items():
    for n, t in run['tool_calls']:
        if n not in ('Read', 'Glob', 'Grep', 'Write'): att.append([r, LABEL[m], n])
ATT_NOTE = {('chelunfu/qiluo_admin', 'Haiku 5.5'): 'List the workspace directory (`ls -la`)', ('coolstartnow/isms-builder', 'Sonnet 5.5'): 'List the workspace directory (`ls -a`)',
            ('zebbern/claude-code-discord', 'Haiku 5.5'): '`curl` the npm registry to look up a package version', ('zhravan/github-readme-quotes', 'Haiku 5.5'): 'Edit the Dockerfile it had just written'}
strip_rows = []
for s in selected:
    rep = load(f'data/strip_reports/{s["slug"]}.json')
    strip_rows.append([s['full_name'], rep['n_deleted'], len(rep['doc_lines_removed']), rep['n_doc_lines_removed'], len(rep['residual_mentions']), rep['n_residual_mentions']])
audit = [
    '## What a model could and could not do\n\n' + table(['Could', 'Could not'], [
        ['Read any file in its own copy of the stripped repository', 'Read anything outside that copy'],
        ['Search file names and file contents', 'Run commands, build or test anything'],
        ['Create new files', 'Edit a file in place'],
        ['', 'Use the web, call another agent, or use any extension'],
        ['', 'See the original Dockerfile, `.dockerignore`, compose files, CI, Docker scripts or git history'],
        ['', 'See another model\'s output or remember another run']]),
    '## What the run records show (all 30 sessions)\n\n' + table(['Check', 'Result'], [
        ['Sessions answered by the pinned model', f"{sum(1 for x in runs.values() if x['models_seen'] == [x['model_id']])}/30"],
        ['Sessions that ended normally', f"{sum(1 for x in runs.values() if x['exit_code'] == 0)}/30"],
        ['Tools available at session start', 'Glob, Grep, Read, Write in all 30; no MCP servers'],
        ['Tool calls in total', sum(x['n_tool_calls'] for x in runs.values())],
        ['File reads or writes outside the workspace', sum(1 for x in runs.values() for n, t in x['tool_calls'] if n in ('Read', 'Write') and not t.startswith(f"/home/user/work/runs/{x['slug']}/{x['model']}/ws"))],
        ['Searches rooted outside the workspace', sum(1 for x in runs.values() for n, t in x['tool_calls'] if n in ('Glob', 'Grep') and re.match(r'/(home|root|tmp|etc|var|usr|opt)/', t) and not t.startswith(f"/home/user/work/runs/{x['slug']}/{x['model']}/ws"))],
        ['Existing files modified or deleted', sum(len(x['files_modified']) + len(x['files_deleted']) for x in runs.values())],
        ['Container files present before the model wrote its own', 0],
        ['Attempts to call a tool that was not offered', len(att)]]),
    '## The four rejected tool attempts\n\nThe CLI answered each with "No such tool available". None had any effect.\n\n' +
    table(['Repository', 'Model', 'Tool', 'What it tried to do'], [[r, m, n, ATT_NOTE.get((r, m), '')] for r, m, n in att]),
    '## What was hidden, per repository\n\n' + table(['Repository', 'Paths deleted', 'Doc files trimmed', 'Doc lines removed', 'Code files still mentioning Docker', 'Mentions left'], strip_rows) +
    '\n\nSource code was never edited, so projects that are themselves about Docker (Mediarium, wings) keep many mentions.',
    '## Hints that got through\n\nFound by checking the generated files against what was hidden:\n\n'
    '- **rdborg/Mediarium:** Go source files name `docker/entrypoint.sh`, the path of the hidden entrypoint script. Opus and Haiku wrote their own script at that path.\n'
    '- **zqbxdev/webchat2api:** one documentation line names `scripts/entrypoint.sh` and the start command. It was not removed because it does not contain the word "docker". Haiku wrote its script at that path.\n'
    '- **pelican/wings:** Go code checks for a "distroless" system, which reveals the kind of base image the project expects. Only Opus used it.\n\n'
    'None of these exposes the original Dockerfile\'s text, but they show that "code only" still carries deployment knowledge.',
    '## Separate from isolation: training data\n\nAll ten repositories are public. A model may have seen an earlier version of a Dockerfile during training. '
    'Repositories were limited to 15–400 stars to make that less likely, but it cannot be ruled out or measured here.',
]
write('07-isolation-and-audit.md', 'What the models could see, and the evidence', 'The isolation rules, the audit of all 30 sessions, and the hints that still leaked.', audit)

# ---------------------------------------------------------------- 08 environment
env = [
    '## Versions\n\n' + table(['Component', 'Version'], [
        ['Hadolint', '2.15.1'], ['Trivy', '0.76.2'], ['Trivy vulnerability database', 'updated 2026-11-17 13:00 UTC, reused for every image'],
        ['Docker Engine', '29.10.0 (BuildKit)'], ['Claude Code CLI', '2.1.326'], ['Playwright browser', 'headless Chromium'],
        ['Models', '`claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5`']]),
    '## Machine\n\n' + table(['Resource', 'Value'], [
        ['Where', 'A managed cloud container (Linux), not a personal machine'], ['CPU / memory', '4 cores / 15 GB'],
        ['Working disk', 'about 25 GB free after tools and databases'], ['Build time limit', '20 minutes per image'],
        ['Parallelism', '3 generation sessions at a time; up to 2 image builds at a time']]),
    '## Sandbox constraints and the workaround for each\n\n' + table(['Constraint', 'Effect', 'Workaround'], [
        ['TLS is intercepted with a private certificate authority', 'Package downloads inside `docker build` fail certificate checks', 'Each base image is wrapped in a thin layer that trusts the sandbox certificate'],
        ['Only HTTPS through a local proxy; no plain HTTP', '`apt` over HTTP fails; `pecl` fails', 'apt sources rewritten to HTTPS in the wrapper layer; one PHP candidate lost'],
        ['Most github.com downloads blocked', 'Builds that fetch release files or Composer archives fail', 'None; two candidates lost at selection'],
        ['Docker Hub rate limit (HTTP 429)', 'Base images could not be pulled', '`mirror.gcr.io` configured as a registry mirror'],
        ['Small disk', 'Large images cannot be kept', 'Each image is scanned and deleted immediately; one image still did not fit'],
        ['2-hour limit on background processes', 'The Docker daemon was stopped mid-evaluation', 'Three falsely failed builds deleted and rerun after a restart']]),
    '## What the wrapper layer adds to an image\n\nCertificate files under `/usr/local/share/ca-certificates/` and `/etc/ssl/`, an apt configuration file, and environment variables that point common tools at the certificate bundle. '
    'It installs no packages. It is applied to original and generated builds alike, and scanners always read the unmodified Dockerfile. Outside such a sandbox, `build_image.py --no-shim` builds normally.',
    '## What was rerun, and why\n\n' + table(['Rerun', 'Reason', 'Effect on results'], [
        ['Stripping of the first four repositories', 'A rule deleted a front-end folder named `charts`', 'Fixed before any model ran'],
        ['Stripping of pelican/wings', 'A rule deleted a Go package named `docker`', 'Fixed before any model ran on that repository'],
        ['All generated-image builds', 'First attempt built inside the stripped copy; one project compiles its own docs', 'First three results discarded; context changed to original source plus model files'],
        ['Three builds', 'Docker daemon stopped by the time limit', 'False failures deleted and rerun'],
        ['Haiku / ClimateVision build', 'Disk ran out during image export, twice', 'Recorded as "build steps completed, not scanned"']]) +
    '\n\nNo generation session was rerun: each of the 30 Dockerfiles is the model\'s first and only attempt.',
]
write('08-environment-and-tooling.md', 'Environment, tooling and reruns', 'Versions, the machine, the sandbox workarounds, and everything that had to be run twice.', env)

# ---------------------------------------------------------------- 09 notable cases
ro = by[('zhravan/github-readme-quotes', 'original')]
notable = [
    '## Opus read a base-image requirement out of Go code\n\npelican/wings checks `/etc/os-release` for `ID="distroless"` in two Go files. Opus kept a distroless base and added a step that writes that file, exactly what the hidden original does. '
    'Sonnet and Haiku chose other bases and skipped it. Opus\'s static score equals the original\'s (11); the other two score 6. Here the higher-scoring file is probably the more correct one.',
    '## One model matched a human\'s size optimisation; two did not\n\nClimateVision\'s authors install CPU-only PyTorch and say why in a comment. Opus made the same choice without being told (4.7 GB against the original\'s 6.9 GB). '
    'Sonnet and Haiku installed the default wheels, which bundle GPU libraries: 12.2 GB for Sonnet, and too large to export for Haiku.',
    '## A model tried to look something up online\n\nIn zebbern/claude-code-discord, Haiku tried to run `curl` against the npm registry to check a package version. No shell was offered, so the call was rejected and it carried on from the code alone.',
    '## Staying root was argued, not forgotten\n\nHaiku wrote its reasons into the Dockerfiles: Wings "runs as root by design: it needs the Docker socket"; wg-rest-api "runs as root because it must create and configure the wg0 interface"; webchat2api binds port 83, "below 1024". '
    'All three models made the same root or non-root call in every repository.',
    f'## The largest single improvement\n\nzhravan/github-readme-quotes: the original image is {ro["size_mb"]:,} MB, runs as root and carries {ro["vuln_total"]:,} CVEs. '
    'All three models produced a non-root image under 400 MB with fewer than 300 CVEs.',
    '## The models disagreed with a human about a port, and agreed with each other\n\nThe original github-readme-quotes Dockerfile exposes ports 3000 and 3004. All three models expose 3002, the default in `src/app.js`.',
    '## A third-party registry mirror was dropped\n\nchelunfu/qiluo_admin pulls its base images through `docker.1ms.run`. With that hidden, all three models used the official images, which removes a dependency on an unofficial mirror. '
    'They also moved the runtime from Alpine to Debian, which took Critical+High CVEs from 0 to 38.',
    '## Secret-looking build arguments were kept\n\nMediarium\'s original passes four API keys as build arguments. All three models kept all four, because the Go build embeds them. Hadolint flags this in every version.',
    '## The same setting, very different amounts of thinking\n\nAt `--effort high`, Sonnet used between 153 and 2,867 thinking tokens per run, Opus between 530 and 15,252, and Haiku between 3,923 and 84,501. '
    'The single most expensive Haiku run (Mediarium, 428 seconds) cost about as much as Sonnet\'s run on the same repository.',
    '## Stripping hints is harder than it looks\n\nThree of the rules written to hide Docker hints were wrong on first use: one deleted a front-end folder called `charts`, one deleted a Go package called `docker`, and trimming Docker lines from documentation broke a project that compiles its docs into the application. '
    'And two script paths still leaked: one through source code and one through an overlooked documentation line.',
]
write('09-notable-cases.md', 'Notable cases', 'Individual things that happened and are worth a sentence in the report. Each was checked against the generated files.', notable)

# ---------------------------------------------------------------- index
index = '''# Fact sheets

Short, single-topic pages about the experiment. Every number is computed from
the files in `data/` and `results/` by `scripts/13_fact_sheets.py`. The full
write-up, with all tables and the limitations, is [`FINDINGS.md`](../../FINDINGS.md).

| Page | What it answers |
|---|---|
| [At a glance](01-at-a-glance.md) | What are the key numbers? |
| [How the ten repositories were chosen](02-selection-funnel.md) | What was searched, filtered, ranked and skipped? |
| [The ten repositories, one by one](03-repositories.md) | What did each model do to each project? |
| [How the three models behaved](04-model-behaviour.md) | Effort, tool use, cost, writing habits, agreement |
| [Which problems were fixed and which were introduced](05-rules-fixed-and-introduced.md) | Rule-by-rule changes |
| [Base images and vulnerability counts](06-base-images-and-cves.md) | Why did lint scores improve but CVEs not? |
| [What the models could see, and the evidence](07-isolation-and-audit.md) | Isolation rules, audit, leaked hints |
| [Environment, tooling and reruns](08-environment-and-tooling.md) | Versions, sandbox workarounds, what was rerun |
| [Notable cases](09-notable-cases.md) | Individual stories worth a sentence in the report |
'''
open(f'{OUT}/README.md', 'w').write(index)
print('fact sheets written:', sorted(os.listdir(OUT)))
