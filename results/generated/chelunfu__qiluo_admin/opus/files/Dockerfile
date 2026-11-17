# syntax=docker/dockerfile:1

############################
# Build stage
############################
FROM rust:1-bookworm AS builder

# Native build deps: aws-lc-sys (jsonwebtoken/rustls) uses cmake/clang,
# libsqlite3-sys is compiled from source, openssl-sys may be pulled in.
RUN apt-get update \
 && apt-get install -y --no-install-recommends cmake clang pkg-config libssl-dev \
 && rm -rf /var/lib/apt/lists/*

# Must match the runtime WORKDIR: the code generator reads its templates from
# env!("CARGO_MANIFEST_DIR")/src/common/codegen/tera_templates at runtime.
WORKDIR /app

COPY Cargo.toml Cargo.lock ./
COPY migration ./migration
COPY src ./src

RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    --mount=type=cache,target=/app/target \
    cargo build --release --bin qiluo \
 && cp /app/target/release/qiluo /usr/local/bin/qiluo

############################
# Runtime stage
############################
FROM debian:bookworm-slim AS runtime

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates tzdata libssl3 \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --system --create-home --home-dir /home/qiluo --uid 10001 qiluo

# The application resolves config/, data/ and src/ relative to the working dir.
WORKDIR /app

COPY --from=builder /usr/local/bin/qiluo /app/qiluo
COPY config ./config
COPY data ./data
# Needed at runtime by the code generator (templates + model sources).
COPY src ./src

RUN mkdir -p data/log data/web data/static data/upload data/ssl \
 && chown -R qiluo:qiluo /app

USER qiluo

# Selects config/docker.yaml (override with -e environment=development, etc.).
ENV environment=docker \
    TZ=Asia/Shanghai \
    RUST_LOG=info

EXPOSE 5001

VOLUME ["/app/data/upload", "/app/data/log"]

CMD ["/app/qiluo"]
