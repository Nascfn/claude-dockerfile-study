# ISMS Builder – Node.js / Express server (serves the UI from ./ui, data from ./data)
#
# Build:  docker build -t isms-builder .
# Run:    docker run -d -p 3000:3000 \
#           -e JWT_SECRET="$(openssl rand -hex 32)" \
#           -v isms-data:/app/data \
#           isms-builder
#
# NODE_ENV=production is set below: the server refuses to start without a
# JWT_SECRET of at least 32 random characters (placeholders are rejected) and
# refuses DEV_HEADER_AUTH=true. See .env.docker for all supported variables.

# ---- Stage 1: install production dependencies --------------------------------
FROM node:22-bookworm-slim AS deps

# Toolchain only as a fallback in case no prebuilt better-sqlite3 binary
# matches; it does not end up in the final image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 make g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package.json package-lock.json ./
# devDependencies (jest, puppeteer, supertest) are not needed at runtime
RUN npm ci --omit=dev && npm cache clean --force

# ---- Stage 2: runtime image --------------------------------------------------
FROM node:22-bookworm-slim

ENV NODE_ENV=production \
    PORT=3000 \
    STORAGE_BACKEND=json

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# All mutable data (JSON stores, uploads, SQLite file) lives in /app/data.
# A named volume mounted here is seeded from the image content on first use.
RUN chown -R node:node /app
USER node

VOLUME ["/app/data"]
EXPOSE 3000

# TCP-level check: works for both HTTP and HTTPS (SSL_CERT_FILE/SSL_KEY_FILE)
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD node -e "const s=require('net').connect(process.env.PORT||3000,'127.0.0.1');s.on('connect',()=>process.exit(0));s.on('error',()=>process.exit(1))"

CMD ["node", "server/index.js"]
