# syntax=docker/dockerfile:1

# Mediarium: one Go program with the React web app embedded in it
# (web/embed.go embeds web/dist). Three stages:
#   web    builds the frontend (npm run build -> web/dist)
#   build  builds the Go program with the frontend embedded (-> /out/app)
#   final  small Alpine image that runs it as PUID/PGID
#
# Build:  docker build -t mediarium .
# Run:    docker run -d --name mediarium -p 8264:8264 \
#           -e PUID=1000 -e PGID=1000 -e TZ=Etc/UTC \
#           -v /path/to/config:/config -v /path/to/data:/data \
#           -e DOWNLOADS_DIR=/data/downloads -e MOVIES_DIR=/data/movies -e TV_DIR=/data/tv \
#           --restart unless-stopped mediarium
#
# Optional build arguments (app-wide service keys; without them the setup
# wizard asks for the user's own): VERSION, TMDB_API_KEY,
# OPENSUBTITLES_API_KEY, TRAKT_CLIENT_ID, SIMKL_CLIENT_ID.

# ---------------------------------------------------------------- frontend
FROM node:24-alpine AS web
WORKDIR /src/web

# Dependencies first, so they are cached until package*.json changes.
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund

# `npm run build` first builds the in-app guide from ../docs (prebuild step),
# then runs tsc and vite. The output goes to web/dist.
COPY web/ ./
COPY docs/ /src/docs/
RUN npm run build

# ---------------------------------------------------------------- program
FROM golang:1.26-alpine AS build
WORKDIR /src

ARG VERSION=
ARG TMDB_API_KEY=
ARG OPENSUBTITLES_API_KEY=
ARG TRAKT_CLIENT_ID=
ARG SIMKL_CLIENT_ID=

ENV CGO_ENABLED=0 GOFLAGS=-trimpath

COPY go.mod go.sum ./
RUN go mod download

COPY . .
# The freshly built frontend replaces whatever web/dist the context had.
RUN rm -rf web/dist
COPY --from=web /src/web/dist ./web/dist

# Stamp the version (default: the VERSION file) and the optional app-wide keys.
RUN set -eu; \
    v="${VERSION:-$(tr -d ' \r\n' < VERSION)}"; \
    flags="-s -w -X main.version=${v}"; \
    [ -z "$TMDB_API_KEY" ]            || flags="$flags -X main.defaultTMDBAPIKey=${TMDB_API_KEY}"; \
    [ -z "$OPENSUBTITLES_API_KEY" ]   || flags="$flags -X main.defaultOpenSubtitlesAPIKey=${OPENSUBTITLES_API_KEY}"; \
    [ -z "$TRAKT_CLIENT_ID" ]         || flags="$flags -X main.defaultTraktClientID=${TRAKT_CLIENT_ID}"; \
    [ -z "$SIMKL_CLIENT_ID" ]         || flags="$flags -X main.defaultSimklClientID=${SIMKL_CLIENT_ID}"; \
    mkdir -p /out; \
    go build -ldflags "$flags" -o /out/app ./cmd/app

# ---------------------------------------------------------------- runtime
FROM alpine:3.22

# par2: repairs Usenet downloads. p7zip: unpacks .7z archives (RAR and ZIP are
# native). su-exec: drops to PUID/PGID. ca-certificates, tzdata: https and TZ.
RUN apk add --no-cache ca-certificates tzdata par2cmdline p7zip su-exec

COPY --from=build /out/app /opt/mediarium/app
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod 0755 /usr/local/bin/docker-entrypoint.sh /opt/mediarium/app \
 && mkdir -p /config /data

ENV APP_PORT=8264 \
    CONFIG_DIR=/config \
    PUID=1000 \
    PGID=1000 \
    TZ=Etc/UTC

VOLUME ["/config"]
# 8264: web page. 58264 (TCP and UDP): torrent peers.
EXPOSE 8264 58264/tcp 58264/udp

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD wget -q -O /dev/null "http://127.0.0.1:${APP_PORT:-8264}${URL_BASE:-}/api/version" || exit 1

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["/opt/mediarium/app"]
