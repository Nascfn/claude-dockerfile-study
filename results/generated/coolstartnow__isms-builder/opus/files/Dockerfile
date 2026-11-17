# syntax=docker/dockerfile:1
# ISMS Builder – container image
#
# Build:  docker build -t isms-builder .
# Run:    docker run -d -p 3000:3000 -v isms-data:/data \
#           -e JWT_SECRET="$(openssl rand -hex 32)" isms-builder
#     or: docker run -d -p 3000:3000 -v isms-data:/data --env-file .env.docker isms-builder
#         (replace the JWT_SECRET placeholder in .env.docker first – the server
#          refuses to start in production with the placeholder)
#
# If JWT_SECRET is not set at all, the entrypoint generates one and keeps it in
# the data volume (/data/.jwt_secret) so sessions survive restarts.

# ── Stage 1: install production dependencies (native build of better-sqlite3) ──
FROM node:22-bookworm-slim AS deps

WORKDIR /app

# Toolchain only needed if no prebuilt better-sqlite3 binary is available
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 make g++ \
 && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_SKIP_DOWNLOAD=true \
    npm_config_update_notifier=false

COPY package.json package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund \
 && npm cache clean --force

# ── Stage 2: runtime image ──
FROM node:22-bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends tini \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV NODE_ENV=production \
    PORT=3000 \
    DATA_DIR=/data \
    STORAGE_BACKEND=json \
    npm_config_update_notifier=false

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Application code stays root-owned (read-only for the app); all mutable state
# lives in DATA_DIR, which is owned by the unprivileged "node" user.
RUN chmod 0755 /app/docker/entrypoint.sh \
 && mkdir -p /data \
 && chown node:node /data

USER node

VOLUME ["/data"]
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["node", "/app/docker/healthcheck.js"]

ENTRYPOINT ["/usr/bin/tini", "--", "/app/docker/entrypoint.sh"]
CMD ["node", "server/index.js"]
