# syntax=docker/dockerfile:1

ARG GO_VERSION=1.27

# ---- Build stage ----
FROM golang:${GO_VERSION}-alpine AS builder

WORKDIR /src

# Cache module downloads separately from source changes.
COPY go.mod go.sum ./
RUN go mod download

COPY . .

# The SQLite driver (glebarez/sqlite) is pure Go, so CGO is not needed and the
# resulting binary is fully static.
ARG VERSION=develop
ARG TARGETOS=linux
ARG TARGETARCH
RUN CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${TARGETARCH} \
    go build \
      -ldflags="-s -w -X github.com/pelican/wings/system.Version=${VERSION}" \
      -trimpath \
      -o /out/wings \
      wings.go

# ---- Runtime stage ----
FROM alpine:3

RUN apk add --no-cache ca-certificates tzdata curl \
    && mkdir -p /etc/pelican /var/lib/pelican /var/log/pelican /tmp/pelican

COPY --from=builder /out/wings /usr/local/bin/wings

# Wings talks to the host's Docker daemon to manage game server containers, so
# mount the Docker socket, e.g.:
#   docker run -d --name wings \
#     -p 8080:8080 -p 2022:2022 \
#     -v /var/run/docker.sock:/var/run/docker.sock \
#     -v /etc/pelican:/etc/pelican \
#     -v /var/lib/pelican:/var/lib/pelican \
#     -v /var/log/pelican:/var/log/pelican \
#     -v /tmp/pelican:/tmp/pelican \
#     <image>
# The config file is expected at /etc/pelican/config.yml. Data directories
# should be mounted at the same path on the host and in the container, since
# game server containers bind-mount paths as seen by the host daemon.
VOLUME ["/etc/pelican", "/var/lib/pelican", "/var/log/pelican"]

# 8080: API / websocket, 2022: SFTP
EXPOSE 8080 2022

ENTRYPOINT ["wings"]
CMD ["--config", "/etc/pelican/config.yml"]
