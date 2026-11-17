#!/bin/sh
# Container entrypoint: prepare the folders and run Mediarium as PUID:PGID.
#
# Started as root (the default), it makes the config folder and any default
# media folder that does not exist yet, gives them to PUID:PGID, and then drops
# to that user. Started as an ordinary user (docker run --user / compose
# "user:"), it just runs the program as that user.
set -eu

PUID="${PUID:-1000}"
PGID="${PGID:-1000}"
CONFIG_DIR="${CONFIG_DIR:-/config}"

# Time zone, if the image has the zone file.
if [ -n "${TZ:-}" ] && [ -e "/usr/share/zoneinfo/$TZ" ]; then
  ln -sf "/usr/share/zoneinfo/$TZ" /etc/localtime 2>/dev/null || true
  echo "$TZ" > /etc/timezone 2>/dev/null || true
fi

if [ "$(id -u)" != "0" ]; then
  exec "$@"
fi

case "$PUID$PGID" in
  *[!0-9]*) echo "PUID and PGID must be numbers (got PUID=$PUID PGID=$PGID)." >&2; exit 1 ;;
esac

# Make a folder that is missing and give it to the user. Existing folders are
# left alone: they belong to the person who mapped them.
ensure_dir() {
  [ -n "$1" ] || return 0
  if [ ! -d "$1" ]; then
    mkdir -p "$1" 2>/dev/null && chown "$PUID:$PGID" "$1" 2>/dev/null || true
  fi
}

ensure_dir "$CONFIG_DIR"
# The config folder must be writable by the user (database, key, backups).
chown "$PUID:$PGID" "$CONFIG_DIR" 2>/dev/null || true
for d in "${DOWNLOADS_DIR:-}" "${MOVIES_DIR:-}" "${TV_DIR:-}"; do
  ensure_dir "$d"
done

export HOME="$CONFIG_DIR"
exec su-exec "$PUID:$PGID" "$@"
