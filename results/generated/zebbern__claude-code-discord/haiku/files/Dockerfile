# syntax=docker/dockerfile:1

# Node.js is required at runtime: the Claude Agent SDK launches its bundled
# Claude Code CLI with `node`. Deno is installed on top of this image.
FROM node:22-bookworm-slim

# Deno version to install. Empty = latest stable.
# Pin for reproducible builds, e.g. --build-arg DENO_VERSION=2.5.0
ARG DENO_VERSION=
# Commit identity for the update check (util/version-check.ts reads GIT_COMMIT).
# Pass with: --build-arg GIT_COMMIT=$(git rev-parse HEAD)
ARG GIT_COMMIT=

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl unzip git tini \
 && curl -fsSL -o /tmp/install-deno.sh https://deno.land/install.sh \
 && DENO_INSTALL=/usr/local sh /tmp/install-deno.sh ${DENO_VERSION:+v${DENO_VERSION}} \
 && rm /tmp/install-deno.sh \
 && apt-get purge -y --auto-remove curl unzip \
 && rm -rf /var/lib/apt/lists/* \
 && deno --version

ENV DOCKER_CONTAINER=true \
    DENO_NO_UPDATE_CHECK=1 \
    GIT_COMMIT=${GIT_COMMIT} \
    WORK_DIR=/app/workspace

WORKDIR /app
COPY --chown=node:node . .

# Writable runtime dirs: the bot persists data in .bot-data, /mcp writes .claude/mcp.json,
# and the Claude workspace is mounted at WORK_DIR.
RUN mkdir -p /app/workspace /app/.bot-data \
 && chown node:node /app /app/workspace /app/.bot-data

USER node

# Pre-fetch the Deno module and npm graph so the first start doesn't download it.
RUN deno cache index.ts

# tini reaps child processes spawned by /shell and the SDK, and forwards signals.
ENTRYPOINT ["/usr/bin/tini", "--", "sh", "/app/docker-entrypoint.sh"]
