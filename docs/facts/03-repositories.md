# The ten repositories, one by one

For each repository: what the original and each model produced, what changed, and anything worth knowing. A dash means the image could not be scanned.

## rdborg/Mediarium

Self-hosted media manager for movies, TV, music, ebooks and audiobooks: search, download and organise, all in one Docker container.

Group: go · Stars: 328 · Commit: `7a1a0730d0` · Pool rank: 1 · Hidden from the models: 11 paths, 717 documentation lines

| Author | Final base image | Static score | Hadolint | Trivy config | User | Critical+High CVEs | All CVEs | Size (MB) |
|---|---|---|---|---|---|---|---|---|
| Original | `alpine:3.24` | 19 | 9 | 1 | root | 1 | 3 | 125 |
| Opus 5.5 | `alpine:3.21` | 11 | 4 | 1 | root | 0 | 1 | 124 |
| Sonnet 5.5 | `alpine:3.22` | 11 | 4 | 1 | root | 0 | 1 | 125 |
| Haiku 5.5 | `debian:bookworm-slim` | 11 | 4 | 1 | root | 105 | 432 | 248 |

- **Findings every model removed:** DL3002 (Last USER is root), DL3059 (Consecutive RUN instructions), DL3066 (Non-numeric user id)
- **Findings at least one model added:** none
- **Notes:** All three models wrote their own entrypoint script to replace the hidden one, and all three keep the original's pattern of starting as root and then dropping privileges. Opus and Haiku placed it at `docker/entrypoint.sh`, the same path as the hidden original; that path is named in the project's Go source, which was not edited. All three kept the four API-key build arguments that the original has, which is why the "sensitive ARG" finding remains.

| Model | Seconds | Turns | Files read | Thinking tokens | Cost (USD) | Files written |
|---|---|---|---|---|---|---|
| Opus 5.5 | 298.4 | 52 | 29 | 15252 | 1.93 | `.dockerignore`, `Dockerfile`, `docker/entrypoint.sh` |
| Sonnet 5.5 | 75.6 | 36 | 18 | 2867 | 0.43 | `.dockerignore`, `Dockerfile`, `docker-entrypoint.sh` |
| Haiku 5.5 | 427.8 | 52 | 26 | 84501 | 0.42 | `.dockerignore`, `Dockerfile`, `docker/entrypoint.sh` |

## zebbern/claude-code-discord

A Discord bot that brings Claude Code to your channels so you can chat, run shell/git, and manage branches. Access from any local, VM, or…

Group: node · Stars: 234 · Commit: `5058290987` · Pool rank: 2 · Hidden from the models: 5 paths, 93 documentation lines

| Author | Final base image | Static score | Hadolint | Trivy config | User | Critical+High CVEs | All CVEs | Size (MB) |
|---|---|---|---|---|---|---|---|---|
| Original | `denoland/deno:latest` | 17 | 8 | 2 | non-root | 132 | 501 | 638 |
| Opus 5.5 | `denoland/deno:debian-2.5.6` | 4 | 2 | 1 | non-root | 232 | 675 | 817 |
| Sonnet 5.5 | `node:22-bookworm-slim` | 8 | 5 | 1 | non-root | 150 | 567 | 1393 |
| Haiku 5.5 | `node:22-bookworm-slim` | 4 | 2 | 1 | non-root | 140 | 491 | 821 |

- **Findings every model removed:** DL3003 (`cd` instead of WORKDIR), DL3007 (`latest` tag used), DL3025 (CMD/ENTRYPOINT not in JSON form), DL3046 (`useradd` without `-l`), DL3059 (Consecutive RUN instructions), DS-0001 (`latest` tag used), DS-0013 (`RUN cd …` instead of WORKDIR)
- **Findings at least one model added:** DL3016 (Unpinned `npm install` packages), DS-0026 (No HEALTHCHECK)
- **Notes:** The application runs on Deno. Opus kept a Deno base image with a pinned version; Sonnet and Haiku started from a Node image and added Deno to it. Haiku tried to `curl` the npm registry to look up a package version; the call was rejected because no shell was offered.

| Model | Seconds | Turns | Files read | Thinking tokens | Cost (USD) | Files written |
|---|---|---|---|---|---|---|
| Opus 5.5 | 135.2 | 28 | 13 | 7582 | 0.92 | `.dockerignore`, `Dockerfile` |
| Sonnet 5.5 | 46.1 | 20 | 7 | 1288 | 0.26 | `.dockerignore`, `Dockerfile`, `docker-entrypoint.sh` |
| Haiku 5.5 | 125.1 | 24 | 13 | 21732 | 0.03 | `.dockerignore`, `Dockerfile`, `docker-entrypoint.sh` |

## zqbxdev/webchat2api

OpenAI-compatible Web Chat API proxy with GPT, Grok, Gemini account management and Docker self-hosting

Group: python · Stars: 399 · Commit: `25752b97cb` · Pool rank: 3 · Hidden from the models: 8 paths, 216 documentation lines

| Author | Final base image | Static score | Hadolint | Trivy config | User | Critical+High CVEs | All CVEs | Size (MB) |
|---|---|---|---|---|---|---|---|---|
| Original | `python:3.13-slim` | 16 | 5 | 3 | root | 785 | 2550 | 2351 |
| Opus 5.5 | `python:3.13-slim-bookworm` | 11 | 3 | 2 | root | 585 | 1469 | 1625 |
| Sonnet 5.5 | `python:3.13-slim` | 10 | 2 | 3 | root | 781 | 1822 | 2153 |
| Haiku 5.5 | `python:3.13-slim` | 11 | 3 | 2 | root | 709 | 1790 | 1936 |

- **Findings every model removed:** DL3013 (Unpinned `pip install` packages), DL3065 (Redundant `--platform`), SC2164 (`cd` without failure check)
- **Findings at least one model added:** DL3025 (CMD/ENTRYPOINT not in JSON form)
- **Notes:** Opus's image has the fewest Critical+High CVEs here (785 → 585). All three models stay root; Haiku notes in a comment that the server binds port 83. One documentation line that names `scripts/entrypoint.sh` and the start command survived the stripping because it does not contain the word "docker"; Haiku wrote its entrypoint at that same path.

| Model | Seconds | Turns | Files read | Thinking tokens | Cost (USD) | Files written |
|---|---|---|---|---|---|---|
| Opus 5.5 | 104.1 | 30 | 13 | 3653 | 0.64 | `.dockerignore`, `Dockerfile`, `docker-entrypoint.sh` |
| Sonnet 5.5 | 45.1 | 27 | 12 | 1177 | 0.16 | `.dockerignore`, `Dockerfile`, `docker-entrypoint.sh` |
| Haiku 5.5 | 137.2 | 35 | 17 | 22332 | 0.04 | `.dockerignore`, `Dockerfile`, `scripts/entrypoint.sh` |

## Climate-Vision/ClimateVision

Open-source ML platform for detecting deforestation, ice melt, and flooding from Sentinel-2 / Landsat imagery.

Group: python · Stars: 378 · Commit: `aab970869e` · Pool rank: 4 · Hidden from the models: 7 paths, 14 documentation lines

| Author | Final base image | Static score | Hadolint | Trivy config | User | Critical+High CVEs | All CVEs | Size (MB) |
|---|---|---|---|---|---|---|---|---|
| Original | `python:3.11-slim` | 14 | 6 | 2 | root | 364 | 2895 | 6852 |
| Opus 5.5 | `python:3.11-slim` | 11 | 6 | 0 | non-root | 64 | 290 | 4693 |
| Sonnet 5.5 | `python:3.11-slim` | 9 | 5 | 0 | non-root | 65 | 297 | 12150 |
| Haiku 5.5 | `python:3.12-slim-bookworm` | 7 | 4 | 0 | – | – | – | – |

- **Findings every model removed:** DL3059 (Consecutive RUN instructions), DS-0002 (Image runs as root), DS-0026 (No HEALTHCHECK)
- **Findings at least one model added:** DL3025 (CMD/ENTRYPOINT not in JSON form), DL3066 (Non-numeric user id)
- **Notes:** The original installs CPU-only PyTorch and explains why in a comment. Opus made the same choice unprompted (4.7 GB image). Sonnet and Haiku installed the default wheels with GPU libraries: Sonnet's image is 12.2 GB, and Haiku's could not be exported inside the sandbox, so it has no image scan. All three models switch the container to a non-root user.

| Model | Seconds | Turns | Files read | Thinking tokens | Cost (USD) | Files written |
|---|---|---|---|---|---|---|
| Opus 5.5 | 85.1 | 28 | 14 | 3096 | 0.51 | `.dockerignore`, `Dockerfile` |
| Sonnet 5.5 | 40.1 | 21 | 9 | 989 | 0.16 | `.dockerignore`, `Dockerfile` |
| Haiku 5.5 | 104.3 | 34 | 14 | 15607 | 0.03 | `.dockerignore`, `Dockerfile` |

## zhravan/github-readme-quotes

Dynamic quote generator for your GitHub readmes | Give a poetic touch to readmes

Group: node · Stars: 307 · Commit: `26980947ad` · Pool rank: 7 · Hidden from the models: 6 paths, 10 documentation lines

| Author | Final base image | Static score | Hadolint | Trivy config | User | Critical+High CVEs | All CVEs | Size (MB) |
|---|---|---|---|---|---|---|---|---|
| Original | `node:20` | 12 | 3 | 3 | root | 2008 | 10450 | 2487 |
| Opus 5.5 | `node:20-alpine` | 2 | 1 | 1 | non-root | 45 | 131 | 225 |
| Sonnet 5.5 | `node:20-alpine` | 2 | 1 | 1 | non-root | 45 | 131 | 229 |
| Haiku 5.5 | `node:22-bookworm-slim` | 2 | 1 | 1 | non-root | 64 | 287 | 362 |

- **Findings every model removed:** DL3003 (`cd` instead of WORKDIR), DL3016 (Unpinned `npm install` packages), DL3025 (CMD/ENTRYPOINT not in JSON form), DS-0002 (Image runs as root), DS-0013 (`RUN cd …` instead of WORKDIR)
- **Findings at least one model added:** DL3066 (Non-numeric user id)
- **Notes:** The biggest CVE drop in the study: the original uses the full `node:20` image and runs as root. All three models expose port 3002, the default in `src/app.js`; the original exposes 3000 and 3004.

| Model | Seconds | Turns | Files read | Thinking tokens | Cost (USD) | Files written |
|---|---|---|---|---|---|---|
| Opus 5.5 | 57.9 | 23 | 17 | 2200 | 0.29 | `.dockerignore`, `Dockerfile` |
| Sonnet 5.5 | 19.4 | 13 | 7 | 292 | 0.06 | `.dockerignore`, `Dockerfile` |
| Haiku 5.5 | 54 | 23 | 12 | 6589 | 0.01 | `.dockerignore`, `Dockerfile` |

## coolstartnow/isms-builder

Self-hosted Information Security Management System — ISO 27001, NIS2, GDPR/DSGVO, BSI IT-Grundschutz

Group: node · Stars: 266 · Commit: `801d5456f2` · Pool rank: 9 · Hidden from the models: 7 paths, 303 documentation lines

| Author | Final base image | Static score | Hadolint | Trivy config | User | Critical+High CVEs | All CVEs | Size (MB) |
|---|---|---|---|---|---|---|---|---|
| Original | `node:lts-alpine` | 11 | 2 | 2 | root | 6 | 20 | 598 |
| Opus 5.5 | `node:22-bookworm-slim` | 5 | 3 | 0 | non-root | 48 | 249 | 525 |
| Sonnet 5.5 | `node:22-bookworm-slim` | 5 | 3 | 0 | non-root | 48 | 249 | 723 |
| Haiku 5.5 | `node:22-bookworm-slim` | 5 | 3 | 0 | non-root | 48 | 249 | 521 |

- **Findings every model removed:** DL3018 (Unpinned `apk add` packages), DS-0002 (Image runs as root), DS-0031 (Secret passed as build argument or env)
- **Findings at least one model added:** DL3008 (Unpinned `apt-get install` packages), DL3066 (Non-numeric user id)
- **Notes:** The static score halves, but every model replaced the original's Alpine base with Debian slim and Critical+High CVEs rose from 6 to 48. Opus and Haiku wrote a separate `docker/healthcheck.js`.

| Model | Seconds | Turns | Files read | Thinking tokens | Cost (USD) | Files written |
|---|---|---|---|---|---|---|
| Opus 5.5 | 126.6 | 39 | 10 | 4032 | 0.78 | `.dockerignore`, `Dockerfile`, `docker/entrypoint.sh`, `docker/healthcheck.js` |
| Sonnet 5.5 | 43.5 | 26 | 7 | 1070 | 0.17 | `.dockerignore`, `Dockerfile` |
| Haiku 5.5 | 146.2 | 41 | 15 | 22471 | 0.04 | `.dockerignore`, `Dockerfile`, `docker/healthcheck.js` |

## pelican/wings

Pelican's server control daemon: runs each game server in its own Docker container.

Group: go · Stars: 331 · Commit: `82bf39e07a` · Pool rank: 10 · Hidden from the models: 5 paths, 66 documentation lines

| Author | Final base image | Static score | Hadolint | Trivy config | User | Critical+High CVEs | All CVEs | Size (MB) |
|---|---|---|---|---|---|---|---|---|
| Original | `gcr.io/distroless/static:latest` | 11 | 3 | 3 | root | 2 | 9 | 63 |
| Opus 5.5 | `gcr.io/distroless/static-debian12:latest` | 11 | 3 | 3 | root | 2 | 13 | 63 |
| Sonnet 5.5 | `alpine:3` | 6 | 1 | 2 | root | 2 | 10 | 81 |
| Haiku 5.5 | `debian:bookworm-slim` | 6 | 1 | 2 | root | 40 | 247 | 184 |

- **Findings every model removed:** none
- **Findings at least one model added:** DL3008 (Unpinned `apt-get install` packages)
- **Notes:** Wings controls the Docker daemon, so root is expected. The Go code checks `/etc/os-release` for `ID="distroless"`. Opus was the only model to pick this up: it kept a distroless base and writes that file, as the original does, and its score equals the original's. Sonnet (Alpine) and Haiku (Debian) score lower but ignore that check. All three add port 2022, which the original does not expose.

| Model | Seconds | Turns | Files read | Thinking tokens | Cost (USD) | Files written |
|---|---|---|---|---|---|---|
| Opus 5.5 | 52.7 | 21 | 8 | 1251 | 0.35 | `.dockerignore`, `Dockerfile` |
| Sonnet 5.5 | 23.8 | 13 | 2 | 369 | 0.07 | `.dockerignore`, `Dockerfile` |
| Haiku 5.5 | 70.5 | 29 | 9 | 8304 | 0.02 | `.dockerignore`, `Dockerfile` |

## lissy93/who-dat

🔎 A really complete domain lookup (RDAP + WHOIS) API for maximum TLD support

Group: go · Stars: 330 · Commit: `23288a4dd7` · Pool rank: 11 · Hidden from the models: 3 paths, 0 documentation lines

| Author | Final base image | Static score | Hadolint | Trivy config | User | Critical+High CVEs | All CVEs | Size (MB) |
|---|---|---|---|---|---|---|---|---|
| Original | `alpine:latest` | 11 | 5 | 1 | non-root | 0 | 1 | 27 |
| Opus 5.5 | `gcr.io/distroless/static-debian12:nonroot` | 2 | 1 | 1 | non-root | 0 | 4 | 18 |
| Sonnet 5.5 | `alpine:3.21` | 5 | 3 | 0 | non-root | 0 | 1 | 28 |
| Haiku 5.5 | `gcr.io/distroless/static-debian12:nonroot` | 2 | 1 | 1 | non-root | 0 | 4 | 18 |

- **Findings every model removed:** DL3007 (`latest` tag used), DL4006 (Pipe without `pipefail`), DS-0001 (`latest` tag used)
- **Findings at least one model added:** DS-0026 (No HEALTHCHECK)
- **Notes:** The smallest and simplest project. Opus and Haiku chose `distroless/static:nonroot`; Sonnet kept Alpine with a pinned version. Fastest run of the study: Sonnet, 19 seconds.

| Model | Seconds | Turns | Files read | Thinking tokens | Cost (USD) | Files written |
|---|---|---|---|---|---|---|
| Opus 5.5 | 28.5 | 12 | 7 | 530 | 0.13 | `.dockerignore`, `Dockerfile` |
| Sonnet 5.5 | 19 | 13 | 6 | 153 | 0.06 | `.dockerignore`, `Dockerfile` |
| Haiku 5.5 | 33.2 | 17 | 9 | 3923 | 0.01 | `.dockerignore`, `Dockerfile` |

## leonovk/wg-rest-api

WireGuard VPN + Easy REST API in one package

Group: ruby · Stars: 76 · Commit: `0bc3aa07a1` · Pool rank: 12 · Hidden from the models: 4 paths, 38 documentation lines

| Author | Final base image | Static score | Hadolint | Trivy config | User | Critical+High CVEs | All CVEs | Size (MB) |
|---|---|---|---|---|---|---|---|---|
| Original | `ruby:4.0.6-alpine` | 11 | 5 | 2 | root | 13 | 58 | 636 |
| Opus 5.5 | `ruby:4.0.6-slim` | 11 | 4 | 1 | root | 135 | 457 | 326 |
| Sonnet 5.5 | `ruby:4.0.6-slim` | 11 | 4 | 1 | root | 127 | 424 | 294 |
| Haiku 5.5 | `ruby:4.0.6-slim` | 9 | 3 | 1 | root | 135 | 456 | 334 |

- **Findings every model removed:** DL3018 (Unpinned `apk add` packages), DL3059 (Consecutive RUN instructions), DS-0026 (No HEALTHCHECK)
- **Findings at least one model added:** DL3008 (Unpinned `apt-get install` packages), DL3025 (CMD/ENTRYPOINT not in JSON form), DL4005 (Shell changed with `ln` instead of SHELL)
- **Notes:** A WireGuard manager that has to configure a network interface, so every model stays root (Haiku says so in a comment). All three moved from Alpine to Debian slim, which multiplied Critical+High CVEs by about ten. The original exposes no ports; the models expose 3000 and 51820.

| Model | Seconds | Turns | Files read | Thinking tokens | Cost (USD) | Files written |
|---|---|---|---|---|---|---|
| Opus 5.5 | 74 | 30 | 23 | 2428 | 0.41 | `.dockerignore`, `Dockerfile`, `docker-entrypoint.sh` |
| Sonnet 5.5 | 43.3 | 22 | 14 | 1564 | 0.14 | `.dockerignore`, `Dockerfile` |
| Haiku 5.5 | 140.1 | 30 | 23 | 26285 | 0.03 | `.dockerignore`, `Dockerfile` |

## chelunfu/qiluo_admin

QiLuo is an enterprise-grade rapid development platform built on the Rust technology stack. It adopts modern architectural design and pro…

Group: rust · Stars: 247 · Commit: `cf389ed47e` · Pool rank: 14 · Hidden from the models: 4 paths, 2 documentation lines

| Author | Final base image | Static score | Hadolint | Trivy config | User | Critical+High CVEs | All CVEs | Size (MB) |
|---|---|---|---|---|---|---|---|---|
| Original | `docker.1ms.run/alpine:latest` | 11 | 5 | 2 | non-root | 0 | 1 | 67 |
| Opus 5.5 | `debian:bookworm-slim` | 6 | 3 | 1 | non-root | 38 | 238 | 260 |
| Sonnet 5.5 | `debian:bookworm-slim` | 6 | 3 | 1 | non-root | 38 | 238 | 193 |
| Haiku 5.5 | `debian:bookworm-slim` | 6 | 3 | 1 | non-root | 38 | 238 | 192 |

- **Findings every model removed:** DL3007 (`latest` tag used), DL3018 (Unpinned `apk add` packages), DL3059 (Consecutive RUN instructions), DS-0001 (`latest` tag used)
- **Findings at least one model added:** DL3008 (Unpinned `apt-get install` packages)
- **Notes:** The original pulls its base images through a third-party registry mirror (`docker.1ms.run`); all three models use the official images. All three also wrote a `config/docker.yaml`. The original's Alpine runtime has no Critical+High CVEs; the models' Debian runtime has 38.

| Model | Seconds | Turns | Files read | Thinking tokens | Cost (USD) | Files written |
|---|---|---|---|---|---|---|
| Opus 5.5 | 86.1 | 25 | 13 | 2704 | 0.48 | `.dockerignore`, `Dockerfile`, `config/docker.yaml` |
| Sonnet 5.5 | 45.8 | 21 | 11 | 1461 | 0.16 | `.dockerignore`, `Dockerfile`, `config/docker.yaml` |
| Haiku 5.5 | 107.6 | 29 | 16 | 15932 | 0.02 | `.dockerignore`, `Dockerfile`, `config/docker.yaml` |

[Back to the index](README.md)
