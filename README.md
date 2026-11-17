# Can Claude Code Improve Insecure Dockerfiles?

Code, data and results for a CAP5150 course project that asks: given only an
application's source code, does Claude Code write a more secure Dockerfile than
the project's human authors did, and how do Opus 5.5, Sonnet 5.5 and Haiku 5.5
compare?

**Start with [`FINDINGS.md`](FINDINGS.md).** It has the setup as it was actually
run, every results table, the caveats, and how to reproduce.

## Layout

| Path | What it is |
|---|---|
| `FINDINGS.md` | All findings, tables, limitations |
| `docs/facts/` | Nine short single-topic fact sheets (start at `docs/facts/README.md`) |
| `docs/FINDINGS.template.md` | Source of `FINDINGS.md` before the tables are inserted |
| `scripts/` | The pipeline, one script per stage (`01_` … `10_`) plus helpers |
| `scripts/prompt.txt` | The exact prompt every model received |
| `data/candidates_raw.json` | All 545 repositories returned by the GitHub search |
| `data/pool.json` | The 43-repository pool and why each other candidate was rejected |
| `data/pool_ranking.json` | Static scan score and rank of every pool Dockerfile |
| `data/selection.json` | The 10 selected repositories (with pinned commits) and the skipped ones |
| `data/originals/<repo>/Dockerfile` | Original Dockerfile of every pool repository |
| `data/strip_reports/` | What was hidden from the models in each selected repository |
| `results/generated/<repo>/<model>/files/` | Everything a model wrote (Dockerfile, .dockerignore, scripts) |
| `results/generated/<repo>/<model>/run.json` | Session record: model, tool calls, tokens, cost, files added |
| `results/static/` | Raw Hadolint and Trivy-config JSON for every Dockerfile |
| `results/image/<repo>/<variant>/` | Build result, build log, Trivy image scan and image summary |
| `results/summary.csv`, `summary.json` | One row per (repository, Dockerfile author) with every metric |
| `results/tables.md`, `tables_features.md`, `tables_stats.md` | The tables used in `FINDINGS.md` |
| `results/selection_build_failures/` | Build logs of ranked candidates whose original did not build |
| `results/pipeline_counts.json` | Counts at each pipeline stage |
| `results/figures/` | Figures as PDF (for LaTeX) and PNG |

Full session transcripts are not published because they contain account
details; `run.json` keeps the audit-relevant part (every tool call and path).

Third-party source code is not copied here. Each selected repository is
identified by its GitHub name and commit hash in `data/selection.json`.

## Pipeline

```
01_discover.js      GitHub repository search driven by Playwright (fixed queries)
02_fetch_pool.py    shallow clone + mechanical filters -> candidate pool
03_rank_pool.py     Hadolint + Trivy config on every original, weighted score, rank
04_select.py        walk the ranking, keep the first 10 whose original builds
05_prepare.py       make the "code only" copy the models see (strip_hints.py)
06_generate_all.py  30 isolated headless Claude Code sessions (generate.py)
07_evaluate.py      scan + build + image-scan every generated Dockerfile
08_aggregate.py     summary.csv / summary.json / tables.md
09_figures.py       figures
10_features.py      structural features of each Dockerfile
11_stats.py         paired sign and Wilcoxon tests
12_render_findings.py  FINDINGS.md from docs/FINDINGS.template.md + tables
13_fact_sheets.py    the fact sheets in docs/facts/
```

Helpers: `scan_static.py` (Hadolint + Trivy config, weighted score),
`build_image.py` (one `docker build`), `image_eval.py` (build, Trivy image
scan, summary, cleanup).

## Tool versions

Hadolint 2.15.1, Trivy 0.76.2 (vulnerability database updated
2026-11-17 13:00 UTC, used for every image), Docker Engine 29.10.0,
Claude Code CLI 2.1.326. All runs happened on 2026-11-17.

## Reproducing

Requirements: Docker, Hadolint, Trivy, Node.js with Playwright, Python 3.10+,
and the Claude Code CLI signed in to an account with access to the three models.

`build_image.py` contains a workaround for the cloud sandbox the study ran in
(a TLS-intercepting proxy): it wraps each base image in a thin layer that
trusts the sandbox certificate. On a normal machine pass `--no-shim` (or set it
in `image_eval.py`) and the Dockerfiles are built unmodified.

The scripts read working copies from `/home/user/work` by default; override
with the `STUDY_WORK` and `STUDY_WORK_ROOT` environment variables.
