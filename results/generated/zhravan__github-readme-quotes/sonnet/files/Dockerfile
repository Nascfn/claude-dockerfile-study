# syntax=docker/dockerfile:1

# ---- Stage 1: build the React frontend ----
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/public ./public
COPY frontend/src ./src
RUN npm run build

# ---- Stage 2: install production backend dependencies ----
FROM node:20-alpine AS backend-deps
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# ---- Stage 3: runtime image ----
FROM node:20-alpine
WORKDIR /app

ENV NODE_ENV=PRODUCTION \
    PORT=3002

COPY --from=backend-deps /app/node_modules ./node_modules
COPY package.json server.js ./
COPY src ./src
COPY customQuotes ./customQuotes
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Run as the unprivileged user shipped with the node image
USER node

EXPOSE 3002

# Configuration (PORT, SERVICE_URL, UNSPLASH_ACCESS_KEY) is supplied at runtime,
# e.g. `docker run --env-file .env -p 3002:3002 <image>`.
# NODE_ENV=PRODUCTION makes the server also serve the built frontend.
CMD ["node", "-r", "dotenv/config", "server.js"]
