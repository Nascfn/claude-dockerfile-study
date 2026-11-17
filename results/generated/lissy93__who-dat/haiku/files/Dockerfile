# syntax=docker/dockerfile:1

# ---------- Build stage ----------
# go.mod pins toolchain go1.26.10; GOTOOLCHAIN=auto (the default) fetches it if the
# base image ships an older patch release.
FROM golang:1.26 AS build

WORKDIR /src

# Download modules in their own layer so it stays cached until go.mod/go.sum change.
COPY go.mod go.sum ./
RUN go mod download

COPY . .

# The frontend is embedded via go:embed, so the binary is self-contained.
ARG VERSION=dev
RUN CGO_ENABLED=0 GOOS=linux go build \
      -trimpath -buildvcs=false \
      -ldflags="-s -w -X main.version=${VERSION}" \
      -o /out/who-dat ./cmd/server

# ---------- Runtime stage ----------
# Distroless "static" has no shell or package manager, but it includes CA certificates
# (required for HTTPS to RDAP registries and IANA bootstrap) and runs as non-root.
FROM gcr.io/distroless/static-debian12:nonroot

COPY --from=build /out/who-dat /usr/local/bin/who-dat

# The server reads PORT (default 8080). Other settings (AUTH_KEY, API_KEYS, cache and
# rate-limit variables) are supplied at runtime with `docker run -e ...`, never baked in.
ENV PORT=8080
EXPOSE 8080

USER nonroot:nonroot
ENTRYPOINT ["/usr/local/bin/who-dat"]
