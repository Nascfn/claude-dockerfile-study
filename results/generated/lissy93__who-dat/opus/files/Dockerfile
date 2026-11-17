# syntax=docker/dockerfile:1

# ---- Build stage ------------------------------------------------------------
FROM golang:1.26-alpine AS build

WORKDIR /src

# Use the toolchain in the image; go.mod only requires go >= 1.26.0
ENV CGO_ENABLED=0 \
    GOTOOLCHAIN=local

# Cache module downloads
COPY go.mod go.sum ./
RUN go mod download

# Copy sources (static frontend is embedded into the binary via go:embed)
COPY cmd ./cmd
COPY internal ./internal

ARG VERSION=docker
RUN go build -trimpath -ldflags="-w -s -X main.version=${VERSION}" -o /out/who-dat ./cmd/server

# ---- Runtime stage ----------------------------------------------------------
# distroless/static ships CA certificates (needed for RDAP over HTTPS) and tzdata
FROM gcr.io/distroless/static-debian12:nonroot

COPY --from=build /out/who-dat /usr/local/bin/who-dat

ENV PORT=8080
EXPOSE 8080

USER nonroot:nonroot

ENTRYPOINT ["/usr/local/bin/who-dat"]
