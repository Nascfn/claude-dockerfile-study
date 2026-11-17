
### T12. Practices adopted (number of Dockerfiles out of 10)

| Practice | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| Multi-stage build | 7 | 9 | 10 | 9 |
| Final USER is non-root | 3 | 6 | 6 | 6 |
| Defines a HEALTHCHECK | 4 | 5 | 5 | 5 |
| Slim/Alpine/distroless final base | 8 | 9 | 10 | 10 |
| Final base is `latest` or untagged | 4 | 1 | 0 | 0 |
| Pins an image by digest | 1 | 0 | 0 | 0 |
| Has a .dockerignore | 8 | 10 | 10 | 10 |
| Uses tini/dumb-init | 2 | 4 | 1 | 4 |
| Uses BuildKit cache mounts | 0 | 2 | 1 | 4 |
| Uses ADD | 0 | 0 | 0 | 0 |
| Mean instructions per Dockerfile | 22.3 | 21.9 | 21.3 | 22.7 |
| Dockerfiles with secret-named ARG/ENV | 2 | 2 | 2 | 1 |
| Runs that wrote extra files (entrypoint scripts etc.) | 0 | 5 | 4 | 5 |

### T13. Final-stage base image chosen

| Repository | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | `alpine:3.24` | `alpine:3.21` | `alpine:3.22` | `debian:bookworm-slim` |
| zebbern/claude-code-discord | `denoland/deno:latest` | `denoland/deno:debian-2.5.6` | `node:22-bookworm-slim` | `node:22-bookworm-slim` |
| zqbxdev/webchat2api | `python:3.13-slim` | `python:3.13-slim-bookworm` | `python:3.13-slim` | `python:3.13-slim` |
| Climate-Vision/ClimateVision | `python:3.11-slim` | `python:3.11-slim` | `python:3.11-slim` | `python:3.12-slim-bookworm` |
| zhravan/github-readme-quotes | `node:20` | `node:20-alpine` | `node:20-alpine` | `node:22-bookworm-slim` |
| coolstartnow/isms-builder | `node:lts-alpine` | `node:22-bookworm-slim` | `node:22-bookworm-slim` | `node:22-bookworm-slim` |
| pelican/wings | `gcr.io/distroless/static:latest` | `gcr.io/distroless/static-debian12:latest` | `alpine:3` | `debian:bookworm-slim` |
| lissy93/who-dat | `alpine:latest` | `gcr.io/distroless/static-debian12:nonroot` | `alpine:3.21` | `gcr.io/distroless/static-debian12:nonroot` |
| leonovk/wg-rest-api | `ruby:4.0.6-alpine` | `ruby:4.0.6-slim` | `ruby:4.0.6-slim` | `ruby:4.0.6-slim` |
| chelunfu/qiluo_admin | `docker.1ms.run/alpine:latest` | `debian:bookworm-slim` | `debian:bookworm-slim` | `debian:bookworm-slim` |
