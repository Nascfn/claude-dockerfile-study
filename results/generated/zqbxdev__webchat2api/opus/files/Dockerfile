# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1: build the Next.js admin UI as a static export (web/out)
# ---------------------------------------------------------------------------
FROM node:22-bookworm-slim AS web-builder

ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /src/web

COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund

# next.config.ts reads ../VERSION to embed the app version
COPY VERSION /src/VERSION
COPY web/ ./
RUN npm run build


# ---------------------------------------------------------------------------
# Stage 2: install the Browser Bridge node dependencies (playwright only;
# the system Chromium from Debian is used at runtime)
# ---------------------------------------------------------------------------
FROM node:22-bookworm-slim AS bridge-builder

ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
WORKDIR /src/bridge

COPY services/browser_bridge/package.json services/browser_bridge/package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund


# ---------------------------------------------------------------------------
# Stage 3: resolve Python dependencies from uv.lock into a virtualenv
# ---------------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS py-builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# uv.lock points at a regional mirror; install the same pinned versions from
# this index instead (override with --build-arg PYPI_INDEX_URL=...).
ARG PYPI_INDEX_URL=https://pypi.org/simple

WORKDIR /src
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --no-hashes --no-emit-project -o /tmp/requirements.txt \
 && uv venv /opt/venv \
 && cd /tmp \
 && uv pip install --no-config --no-cache \
        --python /opt/venv/bin/python \
        --default-index "${PYPI_INDEX_URL}" \
        -r /tmp/requirements.txt


# ---------------------------------------------------------------------------
# Stage 4: runtime image
# ---------------------------------------------------------------------------
FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:${PATH}" \
    HOST=0.0.0.0 \
    PORT=83 \
    BRIDGE_PORT=3080 \
    CHROMIUM_PATH=/usr/bin/chromium \
    ENABLE_BROWSER_BRIDGE=1 \
    STORAGE_BACKEND=json

# chromium: used by the Browser Bridge
# git:      required by GitPython for STORAGE_BACKEND=git
# tini:     PID 1 / zombie reaping for Chromium child processes
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        ca-certificates \
        chromium \
        fonts-liberation \
        git \
        libstdc++6 \
        tini \
 && rm -rf /var/lib/apt/lists/*

# Node runtime for the Browser Bridge (same Debian base as the node image)
COPY --from=bridge-builder /usr/local/bin/node /usr/local/bin/node

COPY --from=py-builder /opt/venv /opt/venv

WORKDIR /app
COPY . .
COPY --from=bridge-builder /src/bridge/node_modules /app/services/browser_bridge/node_modules
COPY --from=web-builder /src/web/out /app/web_dist

RUN sed -i 's/\r$//' /app/docker-entrypoint.sh \
 && chmod +x /app/docker-entrypoint.sh \
 && mkdir -p /app/data

VOLUME ["/app/data"]
EXPOSE 83

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"83\")}/health', timeout=4)" || exit 1

ENTRYPOINT ["/usr/bin/tini", "--", "/app/docker-entrypoint.sh"]
