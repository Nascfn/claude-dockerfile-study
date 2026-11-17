# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1: build the React frontend (frontend/build)
# ---------------------------------------------------------------------------
FROM node:20-bookworm-slim AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
ENV GENERATE_SOURCEMAP=false
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: install production dependencies for the Express server
# ---------------------------------------------------------------------------
FROM node:20-alpine AS server-deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund

# ---------------------------------------------------------------------------
# Stage 3: runtime image
# ---------------------------------------------------------------------------
FROM node:20-alpine

WORKDIR /app

# NOTE on NODE_ENV:
# src/app.js only serves the React UI when NODE_ENV is exactly "PRODUCTION",
# and in that mode its catch-all `GET /*` route is registered before the API
# routes, so /quote, /image and /api-docs would all return index.html.
# The default here ("production", lowercase) keeps the API working, which is
# what the GitHub README cards use. To serve the bundled UI instead, run the
# container with `-e NODE_ENV=PRODUCTION`.
ENV NODE_ENV=production \
    PORT=3002 \
    SERVICE_URL=https://gist.githubusercontent.com/zhravan/6b70e3f8d8c560919f445defc9786972/raw/ce4af1e372d2b312ae66335a82238d8ecdbcd80c/random-quotes.json
# Optional: pass UNSPLASH_ACCESS_KEY at runtime to enable bgSource=unsplash.

COPY --from=server-deps --chown=node:node /app/node_modules ./node_modules
COPY --chown=node:node package.json server.js ./
COPY --chown=node:node src ./src
COPY --chown=node:node customQuotes ./customQuotes
COPY --from=frontend-build --chown=node:node /app/frontend/build ./frontend/build

USER node

EXPOSE 3002

# Same as `npm run prod`, minus the hard-coded NODE_ENV (see note above).
# `-r dotenv/config` still allows a mounted /app/.env file to supply settings.
CMD ["node", "-r", "dotenv/config", "server.js"]
