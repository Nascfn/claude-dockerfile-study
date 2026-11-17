# syntax=docker/dockerfile:1

# Deno binary stage. Deno 2.x matches the v5 deno.lock format.
ARG DENO_VERSION=2.5.6
FROM denoland/deno:bin-${DENO_VERSION} AS deno-bin

# Runtime: Node is required because @anthropic-ai/claude-agent-sdk launches the
# Claude Code CLI (a Node program). Git is required because the bot refuses to
# start outside a git repository and /git, /worktree shell out to it.
FROM node:22-bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates curl tini \
    && rm -rf /var/lib/apt/lists/*

COPY --from=deno-bin /deno /usr/local/bin/deno

# Claude Code CLI (same as setup.sh installs) for `claude` on PATH.
RUN npm install -g @anthropic-ai/claude-code && npm cache clean --force

# The bot's cwd must contain deno.json (read at startup) and .bot-data is
# written relative to cwd, so run from /app as a non-root user.
# (Claude Code refuses bypassPermissions when run as root.)
ENV DENO_DIR=/home/bot/.deno \
    DOCKER_CONTAINER=true \
    WORK_DIR=/app/workspace

RUN useradd --create-home --shell /bin/bash bot \
    && mkdir -p /app/workspace /app/.bot-data /home/bot/.claude \
    && chown -R bot:bot /app /home/bot

WORKDIR /app
USER bot

# Dependencies first for better layer caching: deno.json + lockfile only.
COPY --chown=bot:bot deno.json deno.lock ./
COPY --chown=bot:bot . .

# Pre-fetch and cache all dependencies (npm + remote std imports) against the lockfile.
RUN deno cache --lock=deno.lock index.ts

# Optional: pass the commit so the update checker works without a .git dir.
ARG BOT_GIT_COMMIT=""
ENV BOT_GIT_COMMIT=${BOT_GIT_COMMIT}

# Persist bot state and Claude sessions/credentials across container restarts.
VOLUME ["/app/.bot-data", "/app/workspace", "/home/bot/.claude"]

COPY --chown=bot:bot docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
USER root
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
USER bot

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/docker-entrypoint.sh"]
CMD ["deno", "task", "start"]
