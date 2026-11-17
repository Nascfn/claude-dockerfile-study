#!/bin/sh
# ISMS Builder – container entrypoint
#  1. Seeds the data volume (DATA_DIR) with the shipped demo data on first start.
#  2. Provides a persistent JWT_SECRET if none was passed in.
#  3. Execs the server (CMD).
set -eu

DATA_DIR="${DATA_DIR:-/data}"
SEED_DIR="/app/data"
export DATA_DIR

mkdir -p "$DATA_DIR"

if [ ! -w "$DATA_DIR" ]; then
  echo "[entrypoint] FEHLER/ERROR: $DATA_DIR is not writable by uid $(id -u). Fix the volume permissions (e.g. chown $(id -u):$(id -g))." >&2
  exit 1
fi

# ── 1. First start: copy seed data into an empty data directory ────────────────
# Only if DATA_DIR contains no JSON data yet, so existing installations are never
# touched. demo-bundles stay in the image (read via staticDataPath).
if [ "$DATA_DIR" != "$SEED_DIR" ] && [ -d "$SEED_DIR" ]; then
  if ! find "$DATA_DIR" -maxdepth 2 -name '*.json' -print 2>/dev/null | grep -q .; then
    echo "[entrypoint] Empty data directory – seeding $DATA_DIR from $SEED_DIR"
    for entry in "$SEED_DIR"/* "$SEED_DIR"/.[!.]*; do
      [ -e "$entry" ] || continue
      name="$(basename "$entry")"
      [ "$name" = "demo-bundles" ] && continue
      cp -Rn "$entry" "$DATA_DIR/"
    done
  fi
fi

# ── 2. JWT secret ──────────────────────────────────────────────────────────────
if [ -z "${JWT_SECRET:-}" ]; then
  SECRET_FILE="$DATA_DIR/.jwt_secret"
  if [ ! -s "$SECRET_FILE" ]; then
    echo "[entrypoint] JWT_SECRET not set – generating one and storing it in $SECRET_FILE"
    ( umask 077; node -e "process.stdout.write(require('crypto').randomBytes(32).toString('hex'))" > "$SECRET_FILE" )
  fi
  JWT_SECRET="$(cat "$SECRET_FILE")"
  export JWT_SECRET
fi

exec "$@"
