# syntax=docker/dockerfile:1

# ---- Build stage ----
# Recent stable Rust is required (dependencies such as rand 0.10 / sha2 0.11).
FROM rust:1-bookworm AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends cmake clang pkg-config libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# `migration` is a path dependency of the main crate.
COPY Cargo.toml Cargo.lock ./
COPY migration ./migration
COPY src ./src

RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/app/target \
    cargo build --release --locked \
    && cp target/release/qiluo /usr/local/bin/qiluo

# ---- Runtime stage ----
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --create-home --home-dir /app --shell /usr/sbin/nologin qiluo

WORKDIR /app

COPY --from=builder /usr/local/bin/qiluo /usr/local/bin/qiluo
# The app reads config/<environment>.yaml and config/regexes.yaml relative to the
# working directory, and serves/stores files under data/.
COPY config ./config
COPY data ./data

RUN mkdir -p data/log data/static data/web data/upload \
    && chown -R qiluo:qiluo /app

USER qiluo

# Uses config/docker.yaml (environment-variable driven).
ENV environment=docker \
    DATABASE_URL=mysql://qiluo:Qiluo123@mysql:3306/qiluoopen \
    CACHE_TYPE=memory \
    LOG_LEVEL=info

EXPOSE 5001
VOLUME ["/app/data/upload", "/app/data/log"]

# Requires a reachable MySQL database already loaded with the schema (qiluo.sql).
CMD ["qiluo"]
