# Base images and vulnerability counts

Why the lint scores improved while the CVE counts did not.

## Critical+High CVEs next to the base-image family

| Repository | Original | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | 1 (Alpine) | 0 (Alpine) | 0 (Alpine) | 105 (Debian-based) |
| zebbern/claude-code-discord | 132 (Debian-based) | 232 (Debian-based) | 150 (Debian-based) | 140 (Debian-based) |
| zqbxdev/webchat2api | 785 (Debian-based) | 585 (Debian-based) | 781 (Debian-based) | 709 (Debian-based) |
| Climate-Vision/ClimateVision | 364 (Debian-based) | 64 (Debian-based) | 65 (Debian-based) | – |
| zhravan/github-readme-quotes | 2008 (Debian-based) | 45 (Alpine) | 45 (Alpine) | 64 (Debian-based) |
| coolstartnow/isms-builder | 6 (Alpine) | 48 (Debian-based) | 48 (Debian-based) | 48 (Debian-based) |
| pelican/wings | 2 (distroless) | 2 (distroless) | 2 (Alpine) | 40 (Debian-based) |
| lissy93/who-dat | 0 (Alpine) | 0 (distroless) | 0 (Alpine) | 0 (distroless) |
| leonovk/wg-rest-api | 13 (Alpine) | 135 (Debian-based) | 127 (Debian-based) | 135 (Debian-based) |
| chelunfu/qiluo_admin | 0 (Alpine) | 38 (Debian-based) | 38 (Debian-based) | 38 (Debian-based) |

## What happened when the base family changed

| Repository | Model | Original base | Model's base | Critical+High before | after |
|---|---|---|---|---|---|
| rdborg/Mediarium | Haiku 5.5 | `alpine:3.24` | `debian:bookworm-slim` | 1 | 105 |
| coolstartnow/isms-builder | Opus 5.5 | `node:lts-alpine` | `node:22-bookworm-slim` | 6 | 48 |
| coolstartnow/isms-builder | Sonnet 5.5 | `node:lts-alpine` | `node:22-bookworm-slim` | 6 | 48 |
| coolstartnow/isms-builder | Haiku 5.5 | `node:lts-alpine` | `node:22-bookworm-slim` | 6 | 48 |
| pelican/wings | Haiku 5.5 | `gcr.io/distroless/static:latest` | `debian:bookworm-slim` | 2 | 40 |
| leonovk/wg-rest-api | Opus 5.5 | `ruby:4.0.6-alpine` | `ruby:4.0.6-slim` | 13 | 135 |
| leonovk/wg-rest-api | Sonnet 5.5 | `ruby:4.0.6-alpine` | `ruby:4.0.6-slim` | 13 | 127 |
| leonovk/wg-rest-api | Haiku 5.5 | `ruby:4.0.6-alpine` | `ruby:4.0.6-slim` | 13 | 135 |
| chelunfu/qiluo_admin | Opus 5.5 | `docker.1ms.run/alpine:latest` | `debian:bookworm-slim` | 0 | 38 |
| chelunfu/qiluo_admin | Sonnet 5.5 | `docker.1ms.run/alpine:latest` | `debian:bookworm-slim` | 0 | 38 |
| chelunfu/qiluo_admin | Haiku 5.5 | `docker.1ms.run/alpine:latest` | `debian:bookworm-slim` | 0 | 38 |

11 runs moved an Alpine or distroless original onto a Debian-based image. Critical+High CVEs rose in all 11.

## Where the CVEs live

| Measure | Original | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| Share of all CVEs that are in operating-system packages | 97% | 91% | 89% | 92% |
| Share of Critical+High CVEs that have a fix available | 51% | 20% | 21% | 14% |
| Images with zero Critical+High CVEs | 2 | 2 | 2 | 1 |
| Largest Critical+High count in one image | 2008 | 585 | 781 | 709 |

Operating-system packages dominate, so the count mostly reflects the base image and the system packages installed on top of it, not the application.

## Extremes

- Largest drop: zhravan/github-readme-quotes, 2,008 → 45 Critical+High (10,450 → 131 CVEs in total) when the full `node:20` image was replaced by `node:20-alpine`.
- Largest relative rise: rdborg/Mediarium under Haiku, 1 → 105, Alpine to Debian slim.
- Roughly tenfold for all three models: leonovk/wg-rest-api, 13 → 127–135, Alpine to Debian slim.
- From zero to non-zero: chelunfu/qiluo_admin, 0 → 38 for all three models.
- Only repository at zero for every author: lissy93/who-dat.

## Why this matters for reading the results

Trivy counts every published CVE that applies to an installed package, including many Debian ones marked as unfixed or minor. Alpine ships fewer packages and reports far fewer. A raw CVE count therefore rewards Alpine and distroless bases regardless of how carefully the rest of the Dockerfile is written. It is a real difference in attack surface, but it is one decision (the `FROM` line), not a measure of overall Dockerfile quality.

[Back to the index](README.md)
