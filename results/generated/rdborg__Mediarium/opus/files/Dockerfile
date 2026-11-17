# syntax=docker/dockerfile:1
#
# Mediarium: one Go program that serves the web UI (React, embedded with
# go:embed from web/dist) and runs every background job.
#
#   docker build -t mediarium .
#   docker run -d --name mediarium -p 8264:8264 \
#     -e PUID=1000 -e PGID=1000 -e TZ=Etc/UTC \
#     -v ./config:/config -v ./data:/data \
#     -e DOWNLOADS_DIR=/data/downloads -e MOVIES_DIR=/data/movies -e TV_DIR=/data/tv \
#     --restart unless-stopped mediarium
#
# Optional build arguments (all empty by default):
#   VERSION                 version to stamp (default: the VERSION file)
#   TMDB_API_KEY, OPENSUBTITLES_API_KEY, TRAKT_CLIENT_ID, SIMKL_CLIENT_ID
#                           app-wide keys built into the program; without them
#                           the setup wizard asks for your own
#
# tools/push-update.sh builds the "build" stage on its own and copies the
# program out of /out/app, so keep that stage name and path.

ARG GO_VERSION=1.26
ARG NODE_VERSION=24
ARG ALPINE_VERSION=3.21

# ---------------------------------------------------------------------------
# 1. The web app (web/dist). Its output is the same on every platform, so it
#    is built once on the build machine's own platform.
# ---------------------------------------------------------------------------
FROM --platform=$BUILDPLATFORM node:${NODE_VERSION}-bookworm-slim AS web
WORKDIR /src/web
COPY web/package.json web/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --no-audit --no-fund
COPY web/ ./
# "npm run build" first builds the in-app guide from ../docs (prebuild).
COPY docs/ /src/docs/
RUN npm run build

# ---------------------------------------------------------------------------
# 2. The program. Pure Go (CGO off), cross-compiled for the target platform.
# ---------------------------------------------------------------------------
FROM --platform=$BUILDPLATFORM golang:${GO_VERSION}-alpine AS build
WORKDIR /src
ENV CGO_ENABLED=0 GOTOOLCHAIN=auto
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
COPY . .
COPY --from=web /src/web/dist ./web/dist

ARG TARGETOS=linux
ARG TARGETARCH
ARG VERSION=""
ARG TMDB_API_KEY=""
ARG OPENSUBTITLES_API_KEY=""
ARG TRAKT_CLIENT_ID=""
ARG SIMKL_CLIENT_ID=""
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    set -eu; \
    version="${VERSION:-$(tr -d ' \r\n' < VERSION)}"; \
    mkdir -p /out; \
    GOOS="${TARGETOS}" GOARCH="${TARGETARCH:-$(go env GOARCH)}" \
    go build -trimpath -o /out/app \
      -ldflags "-s -w \
        -X main.version=${version} \
        -X main.defaultTMDBAPIKey=${TMDB_API_KEY} \
        -X main.defaultOpenSubtitlesAPIKey=${OPENSUBTITLES_API_KEY} \
        -X main.defaultTraktClientID=${TRAKT_CLIENT_ID} \
        -X main.defaultSimklClientID=${SIMKL_CLIENT_ID}" \
      ./cmd/app

# ---------------------------------------------------------------------------
# 3. The image that runs it.
# ---------------------------------------------------------------------------
FROM alpine:${ALPINE_VERSION}

# tini: process 1; su-exec: drop to PUID/PGID; par2cmdline and 7z: repair and
# unpack Usenet downloads; ca-certificates and tzdata: https and time zones.
RUN set -eu; \
    apk add --no-cache tini su-exec par2cmdline ca-certificates tzdata; \
    apk add --no-cache p7zip || apk add --no-cache 7zip; \
    if ! command -v 7z >/dev/null 2>&1 && command -v 7zz >/dev/null 2>&1; then \
      ln -s "$(command -v 7zz)" /usr/local/bin/7z; \
    fi; \
    command -v 7z >/dev/null; command -v par2 >/dev/null

COPY --from=build /out/app /app/app
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod 0755 /app/app /usr/local/bin/entrypoint.sh \
    && mkdir -p /config

ENV PUID=1000 \
    PGID=1000 \
    TZ=Etc/UTC \
    CONFIG_DIR=/config \
    APP_PORT=8264 \
    MEDIARIUM_IMAGE_BIN=/app/app

WORKDIR /app
VOLUME ["/config"]
# Web page; torrent peers (TCP and UDP).
EXPOSE 8264 58264/tcp 58264/udp

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget -q -Y off -O /dev/null "http://127.0.0.1:${APP_PORT:-8264}/api/version" || exit 1

ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["/app/app"]
