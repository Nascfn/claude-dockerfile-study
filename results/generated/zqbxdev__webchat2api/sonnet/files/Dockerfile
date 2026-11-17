# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1: build the static web UI (Next.js `output: 'export'` -> web/out)
# ---------------------------------------------------------------------------
FROM node:22-slim AS web-builder

WORKDIR /app/web

# next.config.ts reads ../VERSION, so it must exist next to the web/ directory.
COPY VERSION /app/VERSION
COPY web/package.json web/package-lock.json ./
RUN npm ci

COPY web/ ./
RUN npm run build


# ---------------------------------------------------------------------------
# Stage 2: runtime (FastAPI backend + Grok browser bridge + static web UI)
# ---------------------------------------------------------------------------
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    HOST=0.0.0.0 \
    PORT=83 \
    BRIDGE_PORT=3080 \
    CHROMIUM_PATH=/usr/bin/chromium \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# - chromium + nodejs/npm: Grok browser bridge (services/browser_bridge, Playwright)
# - openssl: used by the encrypted backup feature
# - git: used by the git storage backend (GitPython)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        chromium \
        fonts-liberation \
        git \
        nodejs \
        npm \
        openssl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Python dependencies (cached unless pyproject.toml / uv.lock change)
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

# Browser bridge dependencies (Playwright driver only; system Chromium is used)
COPY services/browser_bridge/package.json services/browser_bridge/package-lock.json services/browser_bridge/
RUN cd services/browser_bridge && npm ci --omit=dev

# Application source
COPY . .

# Static web UI produced by stage 1 (served by the backend from web_dist/)
COPY --from=web-builder /app/web/out ./web_dist

RUN chmod +x /app/docker-entrypoint.sh && mkdir -p /app/data

VOLUME ["/app/data"]
EXPOSE 83

ENTRYPOINT ["/app/docker-entrypoint.sh"]
