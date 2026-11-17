# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1: build the React/Vite frontend (served by the API from frontend/dist)
# ---------------------------------------------------------------------------
FROM node:22-slim AS frontend-build
WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
# VITE_API_BASE_URL is empty by default so the browser calls the API on the
# same origin. Override at build time if the API lives elsewhere:
#   docker build --build-arg VITE_API_BASE_URL=https://example.com .
ARG VITE_API_BASE_URL=""
ARG VITE_GOOGLE_MAPS_API_KEY=""
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL} \
    VITE_GOOGLE_MAPS_API_KEY=${VITE_GOOGLE_MAPS_API_KEY}
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: Python API runtime
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    OMP_NUM_THREADS=1 \
    PORT=8000

# Runtime libraries needed by opencv / rasterio / fiona wheels.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching). The testing and
# development tools at the end of requirements.txt (pytest, black, jupyter, ...)
# are not needed to run the API, so that section is stripped.
COPY requirements.txt ./
RUN sed '/^# Testing and Development/,$d' requirements.txt > requirements-runtime.txt \
    && pip install -r requirements-runtime.txt

# Application code, configs, and bundled model definitions/weights.
COPY setup.py README.md ./
COPY src/ ./src/
COPY config.yaml ./config.yaml
COPY config/ ./config/
COPY models/ ./models/
COPY scripts/ ./scripts/

# Editable install keeps the package at /app/src so the code's repo-root
# lookups (frontend/dist, models/, outputs/) resolve to /app. --no-deps because
# dependencies were installed above (setup.py pins numpy<2, which would clash).
RUN pip install --no-deps -e .

# Built frontend, picked up automatically by the API when present.
COPY --from=frontend-build /frontend/dist ./frontend/dist

# Run as an unprivileged user; outputs/ holds the SQLite DB, uploads, audit logs.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/outputs \
    && chown -R appuser:appuser /app/outputs
USER appuser

VOLUME ["/app/outputs"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/api/health' % os.environ.get('PORT','8000'), timeout=4)" || exit 1

# Secrets/config (GEE keys, API_SECRET_KEY, CORS origins, SMTP, ...) are passed at
# runtime, e.g.: docker run --env-file .env -v $PWD/secrets:/app/secrets:ro ...
CMD ["sh", "-c", "exec uvicorn climatevision.api.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
