# claude-code-discord — container image
#
# Build:
#   docker build --build-arg GIT_COMMIT=$(git rev-parse HEAD) -t claude-code-discord .
#
# Run (ANTHROPIC_API_KEY is required in a container — `claude /login` is not possible):
#   docker run -d --name claude-code-discord --env-file .env \
#     -v /path/to/your/project:/app/workspace \
#     -v claude-bot-data:/app/.bot-data \
#     -v claude-home:/home/deno/.claude \
#     claude-code-discord
#
# Extra CLI flags are appended to the entrypoint, e.g.:
#   docker run ... claude-code-discord --category myproject --user-id 123456789

# deno.lock is format v5 → Deno 2.3+ required.
ARG DENO_VERSION=2.5.6
FROM denoland/deno:debian-${DENO_VERSION}

# git      — required at startup (getGitInfo) and for /git, /worktree
# nodejs   — runtime for the Claude Code CLI bundled with @anthropic-ai/claude-agent-sdk
# procps / iproute2 — ps, free, ip, ss used by the /system-* commands
# tini     — reaps subprocesses (Claude CLI, shell commands) and forwards signals
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates git nodejs procps iproute2 tini \
  && rm -rf /var/lib/apt/lists/* \
  # Mounted workspaces are usually owned by a different uid than the bot user.
  && git config --system --add safe.directory '*' \
  # The base image's `deno` user (uid 1993) has no home directory; Claude Code
  # needs one for ~/.claude and ~/.claude.json. Pre-create volume mount points
  # so named volumes inherit deno ownership instead of root.
  && mkdir -p /home/deno/.claude /app/workspace /app/.bot-data \
  && chown -R deno:deno /home/deno /app

ENV HOME=/home/deno \
    DOCKER_CONTAINER=true \
    WORK_DIR=/app/workspace

# Commit identity for the update checker (util/version-check.ts); optional.
ARG GIT_COMMIT=""
ENV GIT_COMMIT=${GIT_COMMIT}

WORKDIR /app
USER deno

# Cache npm dependencies declared in deno.json first (better layer reuse).
COPY --chown=deno:deno deno.json deno.lock ./
RUN deno install

# App source, then cache the full module graph (incl. deno.land/std remotes).
COPY --chown=deno:deno . .
RUN deno install --entrypoint index.ts \
  # index.ts resolves repo/branch from git in the process cwd at startup and
  # refuses to start outside a git repository.
  && git init -q -b main /app

ENTRYPOINT ["/usr/bin/tini", "--", "deno", "run", "--allow-all", "index.ts"]
