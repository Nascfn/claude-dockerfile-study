# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Build stage
# ---------------------------------------------------------------------------
FROM rust:1-bookworm AS builder

# Native build tools for crates with C build scripts (e.g. aws-lc-sys used by jsonwebtoken).
RUN apt-get update \
    && apt-get install -y --no-install-recommends cmake pkg-config clang \
    && rm -rf /var/lib/apt/lists/*

# Keep the source at /app in both stages. The codegen templates are located via
# CARGO_MANIFEST_DIR, which is fixed at compile time, so the path must match at runtime.
WORKDIR /app
COPY . .

# Build with the committed Cargo.lock. The binary is copied out of the cached target
# directory in the same step because cache mounts are not part of the image layers.
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/app/target \
    cargo build --release --locked \
    && cp target/release/qiluo /usr/local/bin/qiluo

# ---------------------------------------------------------------------------
# Runtime stage
# ---------------------------------------------------------------------------
FROM debian:bookworm-slim AS runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 10001 qiluo \
    && useradd --system --uid 10001 --gid qiluo --home-dir /app --shell /usr/sbin/nologin qiluo

WORKDIR /app

COPY --from=builder /usr/local/bin/qiluo /usr/local/bin/qiluo

# Runtime configuration. The app loads config/${environment}.yaml and
# config/regexes.yaml relative to the working directory.
COPY --from=builder --chown=qiluo:qiluo /app/config ./config

# Codegen templates, read from /app/src/common/codegen/tera_templates at runtime.
COPY --from=builder --chown=qiluo:qiluo /app/src/common/codegen/tera_templates ./src/common/codegen/tera_templates

# Static/web/upload/log directories. Mount volumes over data/upload, data/static, data/web
# to persist uploads or serve your own assets.
COPY --from=builder --chown=qiluo:qiluo /app/data ./data
RUN mkdir -p data/log data/upload data/static data/web \
    && chown -R qiluo:qiluo data

# Select config/docker.yaml (reads DATABASE_URL, JWT_SECRET, SMTP_USER, SMTP_PASSWORD).
ENV environment=docker

USER qiluo

EXPOSE 5001

ENTRYPOINT ["/usr/local/bin/qiluo"]
