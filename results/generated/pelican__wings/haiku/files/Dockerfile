# syntax=docker/dockerfile:1

# Pelican Wings image.
#
# Wings is a single static Go binary (CGO is not required; the SQLite driver is
# pure Go). It manages game server containers through the Docker daemon of the
# host it runs on, so the image contains only the wings binary and the minimal
# OS pieces it needs. The Docker daemon itself is NOT inside the image.
#
# Build:
#   docker build -t pelican/wings .
#
# Run (see the notes at the bottom of this file for why the paths matter):
#   docker run -d --name wings \
#     -p 8080:8080 -p 2022:2022 \
#     -v /etc/pelican:/etc/pelican \
#     -v /var/run/docker.sock:/var/run/docker.sock \
#     -v /var/lib/pelican:/var/lib/pelican \
#     -v /var/log/pelican:/var/log/pelican \
#     -v /tmp/pelican:/tmp/pelican \
#     pelican/wings

ARG GO_VERSION=1.27
ARG DEBIAN_VERSION=bookworm

# ---------------------------------------------------------------------------
# Build stage
# ---------------------------------------------------------------------------
FROM golang:${GO_VERSION}-${DEBIAN_VERSION} AS build

WORKDIR /src

# Fetch modules first so this layer stays cached until go.mod/go.sum change.
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

COPY . .

# Same flags as the Makefile's build target, plus the version injected into
# system.Version. VERSION defaults to the value in system/const.go.
ARG VERSION=develop
ARG TARGETOS
ARG TARGETARCH
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 \
    GOOS=${TARGETOS:-linux} \
    GOARCH=${TARGETARCH:-amd64} \
    go build \
      -trimpath \
      -ldflags="-s -w -X github.com/pelican/wings/system.Version=${VERSION}" \
      -o /out/wings .

# ---------------------------------------------------------------------------
# Runtime stage
# ---------------------------------------------------------------------------
FROM debian:${DEBIAN_VERSION}-slim AS runtime

# ca-certificates: the Panel API and remote backup/transfer endpoints are
#                  reached over HTTPS, and auto-TLS (Let's Encrypt) needs them.
# tzdata:          Wings reads the host timezone for scheduling and logs.
# passwd (already in the base image) provides useradd, which Wings uses to
# create its system user on first start.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates tzdata \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /out/wings /usr/local/bin/wings

# Default directories from config/config.go. They are created by Wings on
# startup if missing; creating them here just makes the image self-describing.
RUN mkdir -p /etc/pelican /var/lib/pelican /var/log/pelican /tmp/pelican

# API (HTTP/HTTPS) and SFTP ports from config/config.go defaults.
EXPOSE 8080 2022

# Wings runs as root by design: it needs the Docker socket and must manage
# files owned by arbitrary container users. The config file is not baked in
# because it holds secrets (node token, etc.); mount it at
# /etc/pelican/config.yml, which is Wings' default --config location.
ENTRYPOINT ["/usr/local/bin/wings"]

# Notes on runtime requirements:
#
# 1. Config file: /etc/pelican/config.yml must exist at startup, otherwise
#    Wings exits with "Configuration File Not Found". Generate it from the
#    Panel (or with `wings configure`) and bind-mount it in.
#
# 2. Docker daemon: Wings reads DOCKER_HOST, defaulting to
#    unix:///var/run/docker.sock. Mount the host socket as shown above.
#
# 3. Matching paths: Wings passes its data directories (e.g.
#    /var/lib/pelican/volumes) to the host Docker daemon as bind-mount sources
#    for game containers. Those paths are resolved on the HOST, so the host
#    directories must be mounted at the same paths inside the container, as in
#    the example above.
#
# 4. Snap-packaged Docker is not supported by Wings and will cause it to exit.
