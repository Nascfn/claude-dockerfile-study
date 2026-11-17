# syntax=docker/dockerfile:1

# Multi-stage build that mirrors the project's own `npm start` flow:
#   1. build the React frontend (frontend/ -> frontend/build)
#   2. install the Express backend's production dependencies
#   3. run `node -r dotenv/config server.js` with NODE_ENV=PRODUCTION, which
#      makes the server serve frontend/build alongside the API.

ARG NODE_VERSION=22-bookworm-slim

# ---------------------------------------------------------------------------
# Stage 1: build the frontend (Create React App, react-scripts 5)
# ---------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS frontend-build
WORKDIR /app/frontend

# Install dependencies first so this layer is cached until the lockfile changes.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: install backend production dependencies
# ---------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS backend-deps
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund

# ---------------------------------------------------------------------------
# Stage 3: runtime image
# ---------------------------------------------------------------------------
FROM node:${NODE_VERSION} AS runtime
WORKDIR /app

ENV NODE_ENV=PRODUCTION \
    PORT=3002

COPY --from=backend-deps /app/node_modules ./node_modules

# Backend source. The server resolves paths relative to its own location
# (src/app.js uses ../frontend/build), so keep the directory layout intact.
COPY package.json server.js ./
COPY src ./src
COPY customQuotes ./customQuotes

# Compiled frontend served by Express in production mode.
COPY --from=frontend-build /app/frontend/build ./frontend/build

# The official Node images include a non-root `node` user. The app writes no
# files, so it does not need a writable directory.
USER node

EXPOSE 3002

# Runtime configuration is read from the environment. See .env.example:
#   SERVICE_URL          - endpoint that returns the default quotes JSON
#   UNSPLASH_ACCESS_KEY  - optional, only needed for bgSource=unsplash
# Pass them with `docker run -e KEY=value`, or with an env file that uses
# KEY=value lines (no spaces around `=`).
CMD ["node", "-r", "dotenv/config", "server.js"]
