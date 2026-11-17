#!/usr/bin/env python3
"""Stage 9: figures for the report (PDF for LaTeX, PNG for previews) from results/summary.json."""
import json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.ticker
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

VARIANTS = ['original', 'opus', 'sonnet', 'haiku']
LABEL = {'original': 'Original (human)', 'opus': 'Opus 5.5', 'sonnet': 'Sonnet 5.5', 'haiku': 'Haiku 5.5'}
# Baseline in neutral gray; the three models in a colour-blind-validated categorical order.
COLOR = {'original': '#8a8984', 'opus': '#2a78d6', 'sonnet': '#eb6834', 'haiku': '#1baf7a'}
MARK = {'original': 's', 'opus': 'o', 'sonnet': '^', 'haiku': 'D'}
INK, MUTED, GRID, SURFACE = '#0b0b0b', '#52514e', '#e4e3df', '#ffffff'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.edgecolor': GRID, 'axes.labelcolor': MUTED,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'text.color': INK, 'axes.spines.top': False,
                     'axes.spines.right': False, 'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'pdf.fonttype': 42})
rows = json.load(open('results/summary.json'))
repos = []
for r in rows:
    if r['repo'] not in repos: repos.append(r['repo'])
by = {(r['repo'], r['variant']): r for r in rows}
short = [r.split('/')[1][:20] for r in repos]
os.makedirs('results/figures', exist_ok=True)

def save(fig, name):
    fig.savefig(f'results/figures/{name}.pdf', bbox_inches='tight'); fig.savefig(f'results/figures/{name}.png', dpi=200, bbox_inches='tight'); plt.close(fig)

# Figure: static insecurity score per repository (grouped bars, zero baseline)
fig, ax = plt.subplots(figsize=(7.1, 2.7))
w = 0.2
for i, v in enumerate(VARIANTS):
    xs = [j + (i - 1.5) * w for j in range(len(repos))]
    ys = [by[(r, v)].get('static_score') or 0 for r in repos]
    ax.bar(xs, ys, width=w * 0.88, color=COLOR[v], label=LABEL[v], linewidth=0)
ax.set_xticks(range(len(repos))); ax.set_xticklabels(short, rotation=28, ha='right')
ax.set_ylabel('Weighted static score (lower is better)'); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5)); ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
ax.legend(frameon=False, ncol=4, loc='upper right', bbox_to_anchor=(1, 1.16), handlelength=1, columnspacing=1.2)
save(fig, 'fig_static_score')

# Figure: Critical+High CVEs per image (dot plot on a log axis; bars would need a zero baseline)
fig, ax = plt.subplots(figsize=(7.1, 4.3))
DODGE = {'original': -0.27, 'opus': -0.09, 'sonnet': 0.09, 'haiku': 0.27}
for j, r in enumerate(repos):
    if j % 2 == 0: ax.axhspan(j - 0.5, j + 0.5, color='#f6f5f2', zorder=0)
    vals = [by[(r, v)].get('vuln_crit_high') for v in VARIANTS]
    present = [x for x in vals if x is not None]
    for v, x in zip(VARIANTS, vals):
        if x is None: continue
        ax.scatter(max(x, 0.5), j + DODGE[v], s=22, marker=MARK[v], color=COLOR[v], edgecolor=SURFACE, linewidth=0.6, zorder=3)
ax.set_xscale('log'); ax.set_xlim(0.35, 4000); ax.set_ylim(-0.5, len(repos) - 0.5); ax.set_yticks(range(len(repos))); ax.set_yticklabels(short); ax.invert_yaxis(); ax.tick_params(axis='y', length=0)
ax.set_xlabel('Critical + High CVEs in the built image (log scale; 0 plotted at 0.5)'); ax.xaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
handles = [plt.Line2D([], [], marker=MARK[v], color=COLOR[v], linestyle='', markersize=5.5, label=LABEL[v]) for v in VARIANTS]
ax.legend(handles=handles, frameon=False, ncol=4, loc='upper right', bbox_to_anchor=(1, 1.09), handletextpad=0.3, columnspacing=1.2)
save(fig, 'fig_cves')

# Figure: build outcome and runtime user per author (counts)
fig, axes = plt.subplots(1, 2, figsize=(7.1, 1.9))
n = len(repos)
for ax, key, title in ((axes[0], 'build_ok', 'Dockerfiles whose build steps all succeed'), (axes[1], 'nonroot', 'Built images that run as non-root')):
    for i, v in enumerate(VARIANTS):
        rs = [by[(r, v)] for r in repos]
        val = sum(1 for a in rs if a['build_steps_ok']) if key == 'build_ok' else sum(1 for a in rs if a.get('runs_as_root') is False)
        tot = n if key == 'build_ok' else sum(1 for a in rs if a.get('runs_as_root') is not None)
        ax.barh(i, val, height=0.55, color=COLOR[v], linewidth=0)
        ax.text(val + 0.15, i, f'{val}/{tot}', va='center', color=INK)
    ax.set_yticks(range(4)); ax.set_yticklabels([LABEL[v] for v in VARIANTS]); ax.invert_yaxis(); ax.set_xlim(0, n + 1.2)
    ax.set_title(title, loc='left', fontsize=8.5, color=INK); ax.xaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
fig.tight_layout()
save(fig, 'fig_build_and_user')

# Figure: pipeline
counts = json.load(open('results/pipeline_counts.json')) if os.path.exists('results/pipeline_counts.json') else {}
fig, ax = plt.subplots(figsize=(7.1, 3.5)); ax.axis('off'); ax.set_xlim(0, 100); ax.set_ylim(0, 50)
def box(x, y, w, h, title, body, fc='#f4f3ef'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.2,rounding_size=1.0', fc=fc, ec='#bdbcb6', lw=0.8))
    ax.text(x + w / 2, y + h - 2.2, title, ha='center', va='top', fontsize=7.2, fontweight='bold', color=INK)
    ax.text(x + w / 2, y + h - 6.4, body, ha='center', va='top', fontsize=5.9, color=MUTED, linespacing=1.4)
def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=8, lw=0.9, color=MUTED, shrinkA=0, shrinkB=0))
c = lambda k, d: counts.get(k, d)
ax.text(0.5, 49, 'INPUT AND SELECTION', fontsize=6, color=MUTED, va='top'); ax.text(99.5, 24.6, 'TREATMENT AND EVALUATION', fontsize=6, color=MUTED, va='top', ha='right')
top = [('1. Discover', f"GitHub repo search\nvia Playwright,\n19 fixed queries\n{c('found', '?')} repos"),
       ('2. Filter pool', f"one root Dockerfile,\nno submodules,\ncurrent runtime\n{c('pool', '?')} repos"),
       ('3. Rank', "Hadolint + Trivy\nconfig on each\noriginal; weighted\nscore, worst first"),
       ('4. Select', f"keep if original\nstill builds;\nmax 3 per language\n{c('selected', 10)} repos"),
       ('5. Strip hints', "delete Dockerfile,\n.dockerignore,\ncompose, CI, .git;\ntrim Docker docs")]
for i, (t, b_) in enumerate(top):
    box(0.5 + i * 20, 27, 18.4, 18.5, t, b_)
    if i < 4: arrow(0.5 + i * 20 + 18.8, 36.2, 0.5 + (i + 1) * 20 - 0.4, 36.2)
box(0.5, 2, 33, 18.5, '6. Generate', "3 models x 10 repos = 30 separate\nheadless Claude Code sessions;\ntools: Read, Glob, Grep, Write (no shell);\nsame neutral prompt, effort high", fc='#eaf1fb')
box(37, 2, 31, 18.5, '7. Evaluate 40 Dockerfiles', "Hadolint 2.15.1: lint findings\nTrivy 0.76.2 config: misconfigurations\ndocker build: does it build?\nTrivy image: CVEs, secrets, user, size", fc='#eaf1fb')
box(71.5, 2, 28, 18.5, '8. Compare', "per repository: original vs\neach model; per model: score\nreduction, build rate, non-root\nrate, CVE counts", fc='#eaf1fb')
ax.plot([89.7, 89.7, 15.5], [26.6, 22.6, 22.6], color=MUTED, lw=0.9); arrow(15.5, 22.6, 15.5, 20.9)
arrow(33.9, 11.2, 36.6, 11.2); arrow(68.4, 11.2, 71.1, 11.2)
save(fig, 'fig_pipeline')
print('figures written')
