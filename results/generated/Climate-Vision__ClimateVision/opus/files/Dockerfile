# syntax=docker/dockerfile:1
#
# ClimateVision: FastAPI backend + Vite/React dashboard in a single image.
#
#   docker build -t climatevision .
#   docker run --rm -p 8000:8000 --env-file .env -v climatevision_outputs:/app/outputs climatevision
#
# Dashboard: http://localhost:8000/   API docs: http://localhost:8000/docs

############################
# Stage 1: build frontend  #
############################
FROM node:22-slim AS frontend

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./

# An empty value makes the dashboard call the API on the same origin, which is
# what you want when FastAPI serves frontend/dist (the same as scripts/deploy.sh).
ARG VITE_API_BASE_URL=""
ARG VITE_GOOGLE_MAPS_API_KEY=""
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL} \
    VITE_GOOGLE_MAPS_API_KEY=${VITE_GOOGLE_MAPS_API_KEY}

RUN npm run build


############################
# Stage 2: Python runtime  #
############################
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    OMP_NUM_THREADS=1 \
    PYTHONPATH=/app/src \
    MPLCONFIGDIR=/tmp/matplotlib \
    PORT=8000

# Runtime libraries used by OpenCV (libGL, glib) and by torch/sklearn (OpenMP).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first so this layer is cached between builds.
# Leave out the dev/test-only tools (pytest, black, jupyter, ...) and pull
# CPU-only PyTorch wheels so the image doesn't include CUDA.
COPY requirements.txt /tmp/requirements.txt
RUN grep -Ev '^[[:space:]]*(pytest|pytest-cov|black|flake8|mypy|jupyter|ipython)([[:space:]<>=!~;\[]|$)' \
        /tmp/requirements.txt > /tmp/requirements-runtime.txt \
    && pip install --upgrade pip setuptools wheel \
    && pip install \
        --extra-index-url https://download.pytorch.org/whl/cpu \
        -r /tmp/requirements-runtime.txt \
    && rm -f /tmp/requirements.txt /tmp/requirements-runtime.txt

# Application source, config.yaml, models/, scripts/, etc.
COPY . .

# Install the package without letting setup.py's looser pins (numpy<2)
# override the resolved requirements. Use an editable install so the code
# stays in /app/src: the app finds config.yaml, models/, outputs/ and
# frontend/dist by walking up from its own source files.
RUN pip install --no-deps -e .

# Built dashboard. FastAPI serves it when /app/frontend/dist/index.html exists.
COPY --from=frontend /frontend/dist /app/frontend/dist

# Run as a non-root user that owns the writable runtime directories
# (SQLite DB + outputs, logs, data, secrets written by the entrypoint).
RUN useradd --create-home --uid 1000 --shell /usr/sbin/nologin climatevision \
    && mkdir -p /app/outputs /app/data /app/logs /app/secrets /app/models_pretrained \
    && chown -R climatevision:climatevision /app

USER climatevision

EXPOSE 8000

VOLUME ["/app/outputs"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/api/health' % os.environ.get('PORT', '8000'), timeout=5)" || exit 1

# The existing entrypoint writes GEE_SERVICE_ACCOUNT_KEY_JSON (if set) to
# /app/secrets/gee-key.json, creates the runtime dirs, then runs uvicorn on $PORT.
CMD ["bash", "/app/scripts/render_entrypoint.sh"]
