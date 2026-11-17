# syntax=docker/dockerfile:1

# Mediarium container image.
#
#   docker build -t mediarium .
#   docker run -d --name mediarium --restart unless-stopped -p 8264:8264 \
#     -e TZ=Europe/London -v ./config:/config -v ./data:/data ... mediarium
#
# Stages:
#   web      builds the web interface (web/dist), with the docs it reads for the in-app guide
#   build    builds the one Mediarium program with that interface embedded; the program
#            is left at /out/app (tools/push-update.sh copies it from this stage)
#   runtime  the small image the program runs in (the last stage, built by default)
#
# Build arguments (all optional):
#   VERSION                     the version to stamp; defaults to the VERSION file
#   TMDB_API_KEY                app-wide keys built into the program, so that
#   OPENSUBTITLES_API_KEY       the setup wizard does not ask for your own
#   TRAKT_CLIENT_ID
#   SIMKL_CLIENT_ID

ARG GO_IMAGE=golang:1.26
ARG NODE_IMAGE=node:24-slim
ARG RUNTIME_IMAGE=debian:bookworm-slim

# ---------------------------------------------------------------------------
# Web interface
# ---------------------------------------------------------------------------
FROM --platform=$BUILDPLATFORM ${NODE_IMAGE} AS web
WORKDIR /src
# The in-app guide is built from ../docs (web/tools/build-guide.mjs), so docs/ is needed here.
COPY docs ./docs
COPY web ./web
WORKDIR /src/web
RUN --mount=type=cache,target=/root/.npm npm ci
RUN npm run build

# ---------------------------------------------------------------------------
# The Mediarium program
# ---------------------------------------------------------------------------
FROM --platform=$BUILDPLATFORM ${GO_IMAGE} AS build
ARG VERSION=""
ARG TMDB_API_KEY=""
ARG OPENSUBTITLES_API_KEY=""
ARG TRAKT_CLIENT_ID=""
ARG SIMKL_CLIENT_ID=""
ARG TARGETARCH
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
# The interface built above replaces the placeholder web/dist (see web/embed.go).
COPY --from=web /src/web/dist ./web/dist
RUN --mount=type=cache,target=/go/pkg/mod --mount=type=cache,target=/root/.cache/go-build <<'EOF'
set -eu
version="${VERSION:-}"
if [ -z "$version" ]; then
  version=$(tr -d ' \r\n' < VERSION)
fi
arch="${TARGETARCH:-$(go env GOARCH)}"
ldflags="-s -w"
ldflags="$ldflags -X main.version=$version"
ldflags="$ldflags -X main.defaultTMDBAPIKey=$TMDB_API_KEY"
ldflags="$ldflags -X main.defaultOpenSubtitlesAPIKey=$OPENSUBTITLES_API_KEY"
ldflags="$ldflags -X main.defaultTraktClientID=$TRAKT_CLIENT_ID"
ldflags="$ldflags -X main.defaultSimklClientID=$SIMKL_CLIENT_ID"
mkdir -p /out
CGO_ENABLED=0 GOOS=linux GOARCH="$arch" \
  go build -trimpath -buildvcs=false -ldflags "$ldflags" -o /out/app ./cmd/app
EOF

# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------
FROM ${RUNTIME_IMAGE} AS runtime

ENV DEBIAN_FRONTEND=noninteractive
# ca-certificates: HTTPS to the metadata services and indexers
# tzdata:          the TZ setting (times in logs and schedules)
# p7zip-full:      the 7z program, for .7z downloads
# par2:            par2cmdline, for PAR2 repair of Usenet downloads
# tini:            the init process (signals, zombie processes)
# curl:            the health check
# util-linux:      setpriv, which runs Mediarium as PUID:PGID
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl par2 p7zip-full tini tzdata util-linux \
 && rm -rf /var/lib/apt/lists/*

COPY --chmod=0755 --from=build /out/app /app/app
COPY --chmod=0755 docker/entrypoint.sh /usr/local/bin/entrypoint.sh

# The config folder: settings, database and encryption key. The entrypoint
# makes it writable for PUID:PGID when the container starts as root.
RUN mkdir -p /config && chown 1000:1000 /config

ENV MEDIARIUM_IMAGE_BIN=/app/app \
    CONFIG_DIR=/config \
    DOWNLOADS_DIR=/downloads \
    MOVIES_DIR=/movies \
    TV_DIR=/tv \
    PUID=1000 \
    PGID=1000 \
    TZ=Etc/UTC

LABEL org.opencontainers.image.source="https://github.com/rdborg/Mediarium" \
      org.opencontainers.image.licenses="AGPL-3.0" \
      org.opencontainers.image.title="Mediarium" \
      org.opencontainers.image.description="A self-hosted media manager: find, download and organise movies, shows, music and books."

# 8264: the web interface and API. 58264: torrent peers (optional, TCP and UDP).
EXPOSE 8264
EXPOSE 58264/tcp
EXPOSE 58264/udp

HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${APP_PORT:-8264}${URL_BASE:-}/api/version" > /dev/null || exit 1

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["IMAGE"]
