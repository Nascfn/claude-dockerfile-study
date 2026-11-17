#!/bin/sh
# Starts Mediarium inside the container image.
#
# The image's own program is MEDIARIUM_IMAGE_BIN (/app/app). A newer program
# that was installed from the settings or pushed through the API lives in
# <CONFIG_DIR>/update. When it is there, can be run, matches its checksum, is a
# Mediarium program for this system, is not older than the image's program and
# has not failed to start three times in a row, it is started instead.
# Otherwise the image's program is started. The file names and the rules are
# the ones in internal/selfupdate; keep the two in step.
#
# Arguments are the command to run. The word IMAGE is replaced by the program
# that was chosen, so the image runs "IMAGE" and any extra arguments follow it.
#
# Environment:
#   PUID, PGID                  user and group to run as (1000 and 1000 by
#                               default). Used only when the container starts as
#                               root; a container started with "user:" runs as
#                               that user, as given.
#   UMASK                       optional octal file-creation mask, such as 022.
#   MEDIARIUM_SKIP_INSTALLED_UPDATE=1
#                               start the image's program even if an update is
#                               installed.
#
# Each note written by this script is a single line on standard error.

MAX_BOOT_ATTEMPTS=3
CONFIG_DIR="${CONFIG_DIR:-/config}"
UPDATE_DIR="$CONFIG_DIR/update"
IMAGE_BIN="${MEDIARIUM_IMAGE_BIN:-/app/app}"

note() {
  printf 'mediarium: %s\n' "$*" >&2
}

# is_true VALUE is true for 1, true, yes or on, in any case.
is_true() {
  case "$(printf '%s' "$1" | tr 'A-Z' 'a-z')" in
    1 | true | yes | on) return 0 ;;
  esac
  return 1
}

use_image() {
  printf '%s' "$IMAGE_BIN"
}

# image_identity sets IMAGE_VERSION and IMAGE_PLATFORM from the image's program
# and reports whether it answered as a Mediarium program.
image_identity() {
  IMAGE_VERSION=""
  IMAGE_PLATFORM=""
  out=$("$IMAGE_BIN" --version-check 2>/dev/null) || return 1
  set -f
  set -- $out
  set +f
  if [ $# -eq 3 ] && [ "$1" = mediarium ]; then
    IMAGE_VERSION=$2
    IMAGE_PLATFORM=$3
    return 0
  fi
  return 1
}

# choose_program prints the path of the program to start. Every reason to fall
# back to the image's program is a single note on standard error.
choose_program() {
  app="$UPDATE_DIR/app"
  if [ ! -e "$app" ]; then
    use_image
    return 0
  fi
  if is_true "${MEDIARIUM_SKIP_INSTALLED_UPDATE:-}"; then
    note "MEDIARIUM_SKIP_INSTALLED_UPDATE is set, so the program in the image is started."
    use_image
    return 0
  fi
  if [ ! -w "$UPDATE_DIR" ]; then
    note "The update folder $UPDATE_DIR can't be written, so the installed update is not used (its starts cannot be counted)."
    use_image
    return 0
  fi
  if [ ! -f "$app" ] || [ ! -x "$app" ]; then
    note "The installed update is not an executable file, so it is not used."
    use_image
    return 0
  fi
  if [ -f "$UPDATE_DIR/app.sha256" ]; then
    set -f
    set -- $(head -n 1 "$UPDATE_DIR/app.sha256" 2>/dev/null)
    set +f
    want=$(printf '%s' "${1:-}" | tr 'A-F' 'a-f')
    have=$(sha256sum "$app" 2>/dev/null | cut -d ' ' -f 1)
    if [ -n "$want" ] && [ "$have" != "$want" ]; then
      note "The installed update does not match its checksum (app.sha256), so it is not used."
      use_image
      return 0
    fi
  fi

  # Ask the installed program who it is, with a time limit.
  probe=$(timeout 10 "$app" --version-check 2>/dev/null)
  probe_status=$?
  set -f
  set -- $probe
  set +f
  if [ "$probe_status" -ne 0 ] || [ $# -ne 3 ] || [ "$1" != mediarium ] || [ "$3" != "$IMAGE_PLATFORM" ]; then
    note "The installed update does not answer as a Mediarium program for this system, so it is not used."
    use_image
    return 0
  fi
  candidate=$2

  # The image's program decides whether the version is new enough: 0 means yes,
  # 1 means it is older than the image, anything else means it is not a version.
  "$IMAGE_BIN" --accepts-update "$candidate" >/dev/null 2>&1
  case $? in
    0) ;;
    1)
      note "The installed update $candidate is older than the version in the image (${IMAGE_VERSION:-unknown}), so it is not used."
      use_image
      return 0
      ;;
    *)
      note "The installed update's version \"$candidate\" is not a version number, so it is not used."
      use_image
      return 0
      ;;
  esac

  # Count this start. A program that keeps stopping before it proves itself
  # (the app clears the count after it has run for a while) is set aside.
  count_file="$UPDATE_DIR/boot-count"
  count=$(head -n 1 "$count_file" 2>/dev/null)
  case "$count" in
    '' | *[!0-9]*) count=0 ;;
  esac
  count=$(printf '%s' "$count" | sed 's/^0*//')
  count=${count:-0}
  if [ "$count" -ge "$MAX_BOOT_ATTEMPTS" ]; then
    mv -f "$app" "$UPDATE_DIR/app.failed"
    if [ -f "$UPDATE_DIR/VERSION" ]; then
      mv -f "$UPDATE_DIR/VERSION" "$UPDATE_DIR/VERSION.failed"
    else
      rm -f "$UPDATE_DIR/VERSION.failed"
    fi
    rm -f "$UPDATE_DIR/app.sha256" "$count_file"
    note "The installed update $candidate stopped $MAX_BOOT_ATTEMPTS times in a row, so it is set aside and the program in the image is started."
    use_image
    return 0
  fi
  if ! printf '%s\n' "$((count + 1))" > "$count_file"; then
    note "The installed update is not used because its starts cannot be counted in $count_file."
    use_image
    return 0
  fi
  note "starting the installed update $candidate"
  printf '%s' "$app"
}

[ $# -gt 0 ] || set -- IMAGE

PUID="${PUID:-1000}"
PGID="${PGID:-1000}"

# As root: prepare the config folder and start again as PUID:PGID.
if [ "$(id -u)" = 0 ] && [ "$PUID" != 0 ]; then
  case "$PUID" in
    '' | *[!0-9]*) note "PUID must be a number, not \"$PUID\"."; exit 1 ;;
  esac
  case "$PGID" in
    '' | *[!0-9]*) note "PGID must be a number, not \"$PGID\"."; exit 1 ;;
  esac
  mkdir -p "$CONFIG_DIR" 2>/dev/null
  if [ "$(stat -c '%u:%g' "$CONFIG_DIR" 2>/dev/null)" != "$PUID:$PGID" ]; then
    chown -R "$PUID:$PGID" "$CONFIG_DIR" 2>/dev/null ||
      note "could not give $CONFIG_DIR to $PUID:$PGID, so Mediarium may not be able to write to it."
  fi
  exec setpriv --reuid="$PUID" --regid="$PGID" --clear-groups sh "$0" "$@"
fi

if [ -n "${UMASK:-}" ]; then
  case "$UMASK" in
    [0-7] | [0-7][0-7] | [0-7][0-7][0-7] | [0-7][0-7][0-7][0-7]) umask "$UMASK" ;;
    *) note "ignoring UMASK=$UMASK: it must be an octal mask such as 022." ;;
  esac
fi

if image_identity; then
  export MEDIARIUM_IMAGE_VERSION="$IMAGE_VERSION"
else
  note "the program in the image ($IMAGE_BIN) does not answer --version-check."
fi

# Replace IMAGE with the program to start, keeping every other argument as it is.
have_image=0
for a in "$@"; do
  if [ "$a" = IMAGE ]; then
    have_image=1
  fi
done
if [ "$have_image" = 1 ]; then
  PROGRAM=$(choose_program)
  n=$#
  i=0
  while [ "$i" -lt "$n" ]; do
    a=$1
    shift
    if [ "$a" = IMAGE ]; then
      set -- "$@" "$PROGRAM"
    else
      set -- "$@" "$a"
    fi
    i=$((i + 1))
  done
fi

exec "$@"
