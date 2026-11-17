# Environment, tooling and reruns

Versions, the machine, the sandbox workarounds, and everything that had to be run twice.

## Versions

| Component | Version |
|---|---|
| Hadolint | 2.15.1 |
| Trivy | 0.76.2 |
| Trivy vulnerability database | updated 2026-11-17 13:00 UTC, reused for every image |
| Docker Engine | 29.10.0 (BuildKit) |
| Claude Code CLI | 2.1.326 |
| Playwright browser | headless Chromium |
| Models | `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5` |

## Machine

| Resource | Value |
|---|---|
| Where | A managed cloud container (Linux), not a personal machine |
| CPU / memory | 4 cores / 15 GB |
| Working disk | about 25 GB free after tools and databases |
| Build time limit | 20 minutes per image |
| Parallelism | 3 generation sessions at a time; up to 2 image builds at a time |

## Sandbox constraints and the workaround for each

| Constraint | Effect | Workaround |
|---|---|---|
| TLS is intercepted with a private certificate authority | Package downloads inside `docker build` fail certificate checks | Each base image is wrapped in a thin layer that trusts the sandbox certificate |
| Only HTTPS through a local proxy; no plain HTTP | `apt` over HTTP fails; `pecl` fails | apt sources rewritten to HTTPS in the wrapper layer; one PHP candidate lost |
| Most github.com downloads blocked | Builds that fetch release files or Composer archives fail | None; two candidates lost at selection |
| Docker Hub rate limit (HTTP 429) | Base images could not be pulled | `mirror.gcr.io` configured as a registry mirror |
| Small disk | Large images cannot be kept | Each image is scanned and deleted immediately; one image still did not fit |
| 2-hour limit on background processes | The Docker daemon was stopped mid-evaluation | Three falsely failed builds deleted and rerun after a restart |

## What the wrapper layer adds to an image

Certificate files under `/usr/local/share/ca-certificates/` and `/etc/ssl/`, an apt configuration file, and environment variables that point common tools at the certificate bundle. It installs no packages. It is applied to original and generated builds alike, and scanners always read the unmodified Dockerfile. Outside such a sandbox, `build_image.py --no-shim` builds normally.

## What was rerun, and why

| Rerun | Reason | Effect on results |
|---|---|---|
| Stripping of the first four repositories | A rule deleted a front-end folder named `charts` | Fixed before any model ran |
| Stripping of pelican/wings | A rule deleted a Go package named `docker` | Fixed before any model ran on that repository |
| All generated-image builds | First attempt built inside the stripped copy; one project compiles its own docs | First three results discarded; context changed to original source plus model files |
| Three builds | Docker daemon stopped by the time limit | False failures deleted and rerun |
| Haiku / ClimateVision build | Disk ran out during image export, twice | Recorded as "build steps completed, not scanned" |

No generation session was rerun: each of the 30 Dockerfiles is the model's first and only attempt.

[Back to the index](README.md)
