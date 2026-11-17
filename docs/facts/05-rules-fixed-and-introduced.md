# Which problems were fixed and which were introduced

Rule by rule, for Hadolint and Trivy config.

Counts are the number of Dockerfiles, out of 10, that trigger the rule at least once. "Security-relevant" is a labelling made for this study of whether a rule concerns privileges, secrets, reproducibility of what gets installed, or health monitoring, as opposed to style.

## Problems the models mostly removed

| Rule | What it flags | Security-relevant | Original | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|---|---|
| DS-0002 | Image runs as root | yes | 7 | 4 | 4 | 4 |
| DL3018 | Unpinned `apk add` packages | yes | 6 | 2 | 3 | 0 |
| DL3059 | Consecutive RUN instructions | style | 6 | 1 | 0 | 0 |
| DL3007 | `latest` tag used | yes | 4 | 1 | 0 | 0 |
| DS-0001 | `latest` tag used | yes | 4 | 1 | 0 | 0 |
| DL3003 | `cd` instead of WORKDIR | style | 3 | 1 | 1 | 1 |
| DS-0013 | `RUN cd …` instead of WORKDIR | style | 3 | 1 | 1 | 1 |
| DL3002 | Last USER is root | yes | 1 | 0 | 0 | 0 |
| DL3046 | `useradd` without `-l` | style | 1 | 0 | 0 | 0 |
| DL3065 | Redundant `--platform` | style | 1 | 0 | 0 | 0 |
| DL4006 | Pipe without `pipefail` | yes | 1 | 0 | 0 | 0 |
| DS-0031 | Secret passed as build argument or env | yes | 1 | 0 | 0 | 0 |
| SC2164 | `cd` without failure check | style | 1 | 0 | 0 | 0 |

## Problems the models introduced or made more common

| Rule | What it flags | Security-relevant | Original | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|---|---|
| DL3008 | Unpinned `apt-get install` packages | yes | 4 | 6 | 6 | 8 |
| DL3066 | Non-numeric user id | style | 4 | 6 | 6 | 6 |
| DL4005 | Shell changed with `ln` instead of SHELL | style | 0 | 1 | 1 | 1 |

Unpinned `apt-get` packages rose as the models moved to Debian-based images; the matching Alpine rule (DL3018) fell at the same time.

## Problems that barely moved

| Rule | What it flags | Security-relevant | Original | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|---|---|
| DS-0026 | No HEALTHCHECK | yes | 6 | 5 | 5 | 5 |
| DL3025 | CMD/ENTRYPOINT not in JSON form | style | 5 | 4 | 5 | 4 |
| DL3013 | Unpinned `pip install` packages | yes | 2 | 1 | 0 | 1 |
| DL3064 | Sensitive-looking name in ARG/ENV | yes | 2 | 2 | 2 | 1 |
| DL3016 | Unpinned `npm install` packages | yes | 1 | 0 | 1 | 0 |

## Findings by severity, summed over the 10 Dockerfiles

| Severity | Original | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| Hadolint error | 0 | 0 | 0 | 0 |
| Hadolint warning | 37 | 23 | 23 | 19 |
| Hadolint info | 14 | 7 | 8 | 6 |
| Hadolint style | 0 | 0 | 0 | 0 |
| Trivy CRITICAL | 1 | 0 | 0 | 0 |
| Trivy HIGH | 7 | 4 | 4 | 4 |
| Trivy MEDIUM | 7 | 2 | 1 | 1 |
| Trivy LOW | 6 | 5 | 5 | 5 |

## Things no scanner flagged but worth knowing

- Trivy's secret scanner found nothing in any of the 39 scanned images.
- No generated Dockerfile uses `ADD`, and none of the originals does either.
- One original pins a base image by digest; no generated Dockerfile does.
- Neither tool has a rule for "the base image carries many known CVEs", which is where the models did worst.

[Back to the index](README.md)
