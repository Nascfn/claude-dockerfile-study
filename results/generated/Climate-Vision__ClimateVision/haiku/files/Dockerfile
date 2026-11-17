# syntax=docker/dockerfile:1
#
# ClimateVision: FastAPI backend + pre-built React dashboard in one image.
#
# Build:  docker build -t climatevision .
# Run:    docker run --rm -p 8000:8000 --env-file .env -v cv-outputs:/app/outputs climatevision
#         API docs at http://localhost:8000/docs, dashboard at http://localhost:8000/

# ---------------------------------------------------------------------------
# Stage 1: build the React dashboard (Vite) into static files
# ---------------------------------------------------------------------------
FROM node:22-slim AS frontend-build
WORKDIR /build/frontend

# Install dependencies first so this layer stays cached across source edits.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
# Leave empty: the dashboard then calls /api on the origin it is served from.
ARG VITE_API_BASE_URL=
RUN npm run build


# ---------------------------------------------------------------------------
# Stage 2: install Python dependencies into a virtualenv
# ---------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS python-build

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build
COPY requirements.txt ./
RUN pip install --upgrade pip \
 && pip install -r requirements.txt


# ---------------------------------------------------------------------------
# Stage 3: runtime image
# ---------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS runtime

# opencv-python links against these shared libraries at import time.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
 && rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OMP_NUM_THREADS=1 \
    MPLCONFIGDIR=/tmp/matplotlib \
    DATABASE_URL=sqlite:////app/outputs/climatevision.sqlite3

# Non-root user. The app creates its outputs/data/logs directories at import
# time (see climatevision/config.py), so those must be writable by this user.
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin app \
 && mkdir -p /app/outputs /app/data /app/logs /app/models_pretrained \
 && chown -R app:app /app

COPY --from=python-build /opt/venv /opt/venv

WORKDIR /app
# Application code and configuration. Code stays root-owned (read-only to the app user).
COPY src ./src
COPY config ./config
COPY config.yaml ./
COPY models ./models
COPY --from=frontend-build /build/frontend/dist ./frontend/dist

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)" || exit 1

# Same command as run_api.sh, without the local .venv check.
CMD ["uvicorn", "climatevision.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
