# syntax=docker/dockerfile:1

# ---- Build stage -----------------------------------------------------------
FROM golang:1.27-alpine AS builder

# go.mod pins a specific Go patch release; allow the go command to fetch it if
# the base image ships an older 1.27.x toolchain.
ENV GOTOOLCHAIN=auto \
    CGO_ENABLED=0 \
    GOOS=linux

ARG VERSION=develop

RUN apk add --no-cache git ca-certificates tzdata

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN go build \
      -trimpath \
      -ldflags="-s -w -X github.com/pelican/wings/system.Version=${VERSION}" \
      -o /out/wings \
      wings.go

# Wings detects that it is running inside a container by checking for
# ID="distroless" in /etc/os-release. In that mode it skips system user
# creation and reads WINGS_USERNAME / WINGS_UID / WINGS_GID instead.
RUN echo 'ID="distroless"' > /out/os-release

# ---- Runtime stage ---------------------------------------------------------
FROM gcr.io/distroless/static-debian12:latest

COPY --from=builder /out/os-release /etc/os-release
COPY --from=builder /out/wings /usr/bin/wings

# HTTP API (api.port) and built-in SFTP server (system.sftp.bind_port).
EXPOSE 8080 2022

# Wings must be able to talk to the host Docker daemon and needs access to its
# configuration and data directories. Typical run:
#
#   docker run -d \
#     -v /var/run/docker.sock:/var/run/docker.sock \
#     -v /etc/pelican:/etc/pelican \
#     -v /var/lib/pelican:/var/lib/pelican \
#     -v /var/log/pelican:/var/log/pelican \
#     -v /tmp/pelican:/tmp/pelican \
#     -p 8080:8080 -p 2022:2022 \
#     <image>
ENTRYPOINT ["/usr/bin/wings"]
CMD ["--config", "/etc/pelican/config.yml"]
