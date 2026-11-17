# syntax=docker/dockerfile:1

# ============================================================================
# webchat2api image
#
#   web-build     Next.js admin UI, static export to web/out
#   python-build  Python dependencies from uv.lock into /app/.venv
#   runtime       Python 3.13 + Chromium/Node for the Grok Browser Bridge
#
# Build:  docker build -t webchat2api .
# Run:    docker run -d -p 83:83 -e LOGIN_SECRET=<strong-secret> \
#           -v webchat2api-data:/app/data webchat2api
# ============================================================================

# ---- 1. Frontend static export ----------------------------------------------
FROM node:22-alpine AS web-build
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app
# web/next.config.ts reads ../VERSION, so VERSION must sit one level above web/.
COPY VERSION ./VERSION
WORKDIR /app/web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# ---- 2. Python dependencies --------------------------------------------------
FROM python:3.13-slim AS python-build
COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /usr/local/bin/uv
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=.python-version,target=.python-version \
    uv sync --frozen --no-dev --no-install-project

# ---- 3. Runtime --------------------------------------------------------------
FROM python:3.13-slim AS runtime

# chromium + nodejs/npm: Grok Browser Bridge (launched by scripts/entrypoint.sh)
# git: git storage backend (gitpython shells out to git)
# openssl: R2 backup encryption (openssl CLI)
# tini: PID 1 init, reaps Chromium child processes and forwards signals
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates curl tini chromium nodejs npm git openssl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:${PATH}" \
    HOST=0.0.0.0 \
    PORT=83 \
    BRIDGE_PORT=3080 \
    CHROMIUM_PATH=/usr/bin/chromium \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

WORKDIR /app

# Virtualenv from stage 2. The base image is the same, so the interpreter path matches.
COPY --from=python-build /app/.venv /app/.venv

# Browser Bridge Node dependencies, installed in this image (not copied from the host).
COPY services/browser_bridge/package.json services/browser_bridge/package-lock.json ./services/browser_bridge/
RUN cd services/browser_bridge \
    && npm ci --omit=dev \
    && npm cache clean --force

# Application code and the built frontend.
COPY main.py VERSION ./
COPY api ./api
COPY services ./services
COPY utils ./utils
COPY scripts/entrypoint.sh ./scripts/entrypoint.sh
COPY --from=web-build /app/web/out ./web_dist

RUN chmod 0755 /app/scripts/entrypoint.sh \
    && mkdir -p /app/data

# Port 83 is below 1024, so the process runs as root. Chromium runs with --no-sandbox
# (set in services/browser_bridge/server.js), which Chromium needs when run as root.
EXPOSE 83

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/health" || exit 1

ENTRYPOINT ["/usr/bin/tini", "-g", "--", "/app/scripts/entrypoint.sh"]
CMD ["python", "main.py"]
