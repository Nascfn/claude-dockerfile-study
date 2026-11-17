# syntax=docker/dockerfile:1

# ---- Build stage ----
FROM golang:1.26-alpine AS build
WORKDIR /src

# Download modules first so this layer is cached unless go.mod/go.sum change
COPY go.mod go.sum ./
RUN go mod download

# Frontend assets in internal/web/static are embedded into the binary at build time
COPY cmd ./cmd
COPY internal ./internal

ARG VERSION=dev
RUN CGO_ENABLED=0 go build -trimpath \
      -ldflags="-w -s -X main.version=${VERSION}" \
      -o /out/who-dat ./cmd/server

# ---- Runtime stage ----
FROM alpine:3.21
# CA certs for HTTPS (RDAP), tzdata for time handling
RUN apk add --no-cache ca-certificates tzdata \
 && adduser -D -H -u 10001 whodat

COPY --from=build /out/who-dat /usr/local/bin/who-dat

USER whodat

# Configurable via env: PORT, AUTH_KEY, API_KEYS, ENABLE_CACHE, CACHE_TTL_SECONDS,
# LOOKUP_TIMEOUT_SECONDS, MAX_DOMAINS, RATE_PER_MINUTE, RATE_BURST
ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null "http://127.0.0.1:${PORT}/health" || exit 1

ENTRYPOINT ["/usr/local/bin/who-dat"]
