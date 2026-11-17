# ISMS Builder – Docker-Image (Node.js/Express-API + statische Oberfläche)
#
# Bauen:
#   docker build -t isms-builder .
#
# Starten (JWT_SECRET muss gesetzt sein, sonst bricht der Start ab):
#   cp .env.docker .env          # dann JWT_SECRET ersetzen: openssl rand -hex 32
#   docker run -d --name isms-builder -p 3000:3000 \
#     --env-file .env -v isms-data:/data isms-builder
#
# Der Container läuft immer mit NODE_ENV=production. Nutzerdaten liegen in /data (Volume).

# ── Stage 1: Produktionsabhängigkeiten ───────────────────────────────────────────
# Dev-Abhängigkeiten (jest, puppeteer, supertest) werden bewusst nicht installiert:
# puppeteer würde sonst ein Chromium herunterladen, das die Anwendung nicht braucht
# (der PDF-Export läuft ohne Browser).
FROM node:22-bookworm-slim AS deps
WORKDIR /app

# Falls better-sqlite3 kein vorkompiliertes Binary laden kann, baut npm es aus dem Quelltext.
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 make g++ \
 && rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund

# ── Stage 2: Laufzeit-Image ──────────────────────────────────────────────────────
FROM node:22-bookworm-slim AS runtime

# tini als PID 1: Der Server behandelt SIGTERM nicht selbst. Ohne Init würde `docker stop`
# zehn Sekunden warten und den Prozess dann hart beenden. tini reicht Signale weiter.
RUN apt-get update \
 && apt-get install -y --no-install-recommends tini \
 && rm -rf /var/lib/apt/lists/*

ENV NODE_ENV=production \
    PORT=3000 \
    DATA_DIR=/data

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY package.json ./
COPY server ./server
COPY ui ./ui
COPY docs ./docs
COPY scripts ./scripts
COPY docker/healthcheck.js ./docker/healthcheck.js
COPY LICENSE ./

# Mitgelieferte Demo-Bundles gehören zum Programmstand. Die übrigen Dateien unter data/
# sind Entwicklungs- bzw. Seed-Daten und werden nicht ins Image kopiert (siehe .dockerignore);
# die Anwendung legt ihre Daten beim ersten Start unter DATA_DIR selbst an.
COPY data/demo-bundles ./data/demo-bundles

# Nutzerdaten (JSON-Dateien, Sitzungen, Uploads, ggf. SQLite) liegen im Volume /data.
RUN mkdir -p /data && chown node:node /data
VOLUME ["/data"]

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["node", "docker/healthcheck.js"]

USER node

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["node", "server/index.js"]
