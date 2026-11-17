# At a glance

The whole experiment on one page.

## The experiment in numbers

| What | Number |
|---|---|
| Repositories returned by the GitHub search | 545 |
| …with a Dockerfile at the root | 152 |
| Repositories in the ranked pool | 43 |
| Repositories studied | 10 |
| Models | 3 (Opus 5.5, Sonnet 5.5, Haiku 5.5) |
| Generation sessions | 30 |
| Dockerfiles evaluated (10 original + 30 generated) | 40 |
| Images built and scanned | 39 |
| Tool calls made by the models | 784 |
| Total generation time, all 30 sessions | 47 minutes |
| Total generation cost reported by the CLI | USD 8.75 |
| Date of every run and scan | 2026-11-17 |

## The result in numbers

| What | Original | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| Mean weighted static score (lower is better) | 13.3 | 7.4 | 7.3 | 6.3 |
| Mean Hadolint findings | 5.1 | 3 | 3.1 | 2.5 |
| Mean Trivy misconfigurations | 2.1 | 1.1 | 1 | 1 |
| Dockerfiles whose build steps all succeed | 10/10 | 10/10 | 10/10 | 10/10 |
| Images scanned | 10 | 10 | 10 | 9 |
| Scanned images that run as root | 7 | 4 | 4 | 4 |
| Median Critical+High CVEs per image | 9.5 | 46.5 | 46.5 | 64 |
| Median image size (MB) | 617 | 293 | 261.5 | 334 |

## Five facts to remember

1. 27 of 30 generated Dockerfiles scored strictly better than the original on the static score; none scored worse.
2. All 30 generated Dockerfiles completed every build step, although no model could run a build.
3. Critical+High CVEs went down in 10 of 29 scanned images and up in 14.
4. Every time a model replaced an Alpine or distroless base with a Debian one (11 runs), CVEs went up.
5. The cheapest model (Haiku) had the best static score and the most CVEs.

[Back to the index](README.md)
