#!/bin/sh
# Container entrypoint for Mediarium.
#
#   entrypoint.sh [command...]        (default command: the image's program)
#
# 1. As root: creates the config and media folders that are missing, gives
#    them to PUID:PGID, and starts itself again as that user (su-exec).
# 2. Applies UMASK when it is set to an octal mask.
# 3. Tells the app the version of the program inside the image
#    (MEDIARIUM_IMAGE_VERSION) and where that program is (MEDIARIUM_IMAGE_BIN).
# 4. Chooses the program to start: an update installed from the app in
#    <config>/update/app (see internal/selfupdate) when it is there, matches its
#    checksum, answers as a Mediarium program for this system, is not older than
#    the image's own and hasn't stopped 3 times in a row before proving itself;
#    otherwise the image's program. Every argument that is the image's program
#    is replaced by the chosen one, so it also works inside a longer command.
#
# The file names and rules match internal/selfupdate/selfupdate.go and next.go;
# internal/selfupdate/entrypoint_test.go runs this script.

IMAGE_BIN="${MEDIARIUM_IMAGE_BIN:-/app/app}"
CONFIG_DIR="${CONFIG_DIR:-/config}"
MAX_BOOT_ATTEMPTS=3
PROBE_TIMEOUT=10

note() {
	printf 'mediarium: %s\n' "$*" >&2
}

truthy() {
	case "$1" in
	1 | [Tt][Rr][Uu][Ee] | [Yy][Ee][Ss] | [Oo][Nn]) return 0 ;;
	esac
	return 1
}

numeric() {
	case "$1" in
	'' | *[!0-9]*) return 1 ;;
	esac
	return 0
}

[ $# -gt 0 ] || set -- "$IMAGE_BIN"

# --- 1. Root: prepare the folders, then run as PUID:PGID. --------------------
if [ "$(id -u)" = 0 ]; then
	puid="${PUID:-1000}"
	pgid="${PGID:-1000}"
	if ! numeric "$puid"; then
		note "PUID=$puid is not a number; using 1000"
		puid=1000
	fi
	if ! numeric "$pgid"; then
		note "PGID=$pgid is not a number; using 1000"
		pgid=1000
	fi

	if [ "$puid" != 0 ]; then
		mkdir -p "$CONFIG_DIR" 2>/dev/null
		# Only what is not already owned by the user is changed, so this is quick
		# on every start after the first one.
		find "$CONFIG_DIR" -xdev \( ! -user "$puid" -o ! -group "$pgid" \) \
			-exec chown -h "$puid:$pgid" {} + 2>/dev/null ||
			note "could not give everything in $CONFIG_DIR to $puid:$pgid"

		# Media folders are yours: only the ones that don't exist yet are made,
		# and only those are given to PUID:PGID. Existing folders are left alone.
		downloads="${DOWNLOADS_DIR:-/downloads}"
		for dir in "$downloads" "$downloads/incomplete" "$downloads/complete" \
			"${MOVIES_DIR:-/movies}" "${TV_DIR:-/tv}"; do
			if [ ! -e "$dir" ] && mkdir -p "$dir" 2>/dev/null; then
				chown "$puid:$pgid" "$dir" 2>/dev/null
			fi
		done

		if command -v su-exec >/dev/null 2>&1; then
			exec su-exec "$puid:$pgid" /bin/sh "$0" "$@"
		fi
		note "su-exec is missing, so Mediarium runs as root"
	fi
fi

# --- 2. UMASK -------------------------------------------------------------------
if [ -n "${UMASK:-}" ]; then
	case "$UMASK" in
	[0-7][0-7][0-7] | [0-7][0-7][0-7][0-7]) umask "$UMASK" ;;
	*) note "ignoring UMASK=$UMASK: it must be three or four octal digits, like 002 or 022" ;;
	esac
fi

# --- Helpers to look at a program ------------------------------------------------

# probe PROGRAM: runs PROGRAM --version-check with an empty environment and a
# time limit, and puts what it printed in PROBE_OUT. The output goes to a file,
# not a pipe, so a program that leaves something running can't hold this up.
probe() {
	PROBE_OUT=""
	_tmp=$(mktemp "${TMPDIR:-/tmp}/mediarium-probe.XXXXXX" 2>/dev/null) || return 1
	if command -v timeout >/dev/null 2>&1; then
		timeout "$PROBE_TIMEOUT" env -i "$1" --version-check >"$_tmp" 2>/dev/null </dev/null
	else
		env -i "$1" --version-check >"$_tmp" 2>/dev/null </dev/null
	fi
	_st=$?
	PROBE_OUT=$(head -c 512 "$_tmp" 2>/dev/null)
	rm -f "$_tmp"
	return $_st
}

# parse_line LINE: splits "mediarium <version> <os>/<arch>" into P_VERSION and
# P_PLATFORM. Fails for anything else.
parse_line() {
	P_VERSION=""
	P_PLATFORM=""
	set -f
	# shellcheck disable=SC2086
	set -- $1
	set +f
	[ $# -eq 3 ] && [ "$1" = mediarium ] || return 1
	case "$3" in
	?*/?*) ;;
	*) return 1 ;;
	esac
	P_VERSION=$2
	P_PLATFORM=$3
	return 0
}

# accepts VERSION: asks the image's program whether VERSION may replace it.
# 0 = not older, 1 = older, anything else = not a version number.
accepts() {
	if command -v timeout >/dev/null 2>&1; then
		timeout "$PROBE_TIMEOUT" env -i "$IMAGE_BIN" --accepts-update "$1" >/dev/null 2>&1 </dev/null
	else
		env -i "$IMAGE_BIN" --accepts-update "$1" >/dev/null 2>&1 </dev/null
	fi
}

# --- 3. The image's own program -----------------------------------------------------
IMAGE_VERSION=""
IMAGE_PLATFORM=""
if probe "$IMAGE_BIN" && parse_line "$PROBE_OUT"; then
	IMAGE_VERSION=$P_VERSION
	IMAGE_PLATFORM=$P_PLATFORM
	MEDIARIUM_IMAGE_VERSION=$IMAGE_VERSION
	export MEDIARIUM_IMAGE_VERSION
fi
MEDIARIUM_IMAGE_BIN=$IMAGE_BIN
export MEDIARIUM_IMAGE_BIN

# --- 4. Choose the program ------------------------------------------------------------
UPDATE_DIR="$CONFIG_DIR/update"
APP="$UPDATE_DIR/app"

# choose: prints nothing on stdout; sets CHOSEN and writes at most one note.
choose() {
	CHOSEN=$IMAGE_BIN

	[ -e "$APP" ] || [ -L "$APP" ] || return 0

	if truthy "${MEDIARIUM_SKIP_INSTALLED_UPDATE:-}"; then
		note "MEDIARIUM_SKIP_INSTALLED_UPDATE is set, so the installed update is not used; starting the version in the image"
		return 0
	fi

	if [ ! -f "$APP" ] || [ ! -x "$APP" ]; then
		note "the installed update $APP is not an executable file; starting the version in the image"
		return 0
	fi

	if [ ! -w "$UPDATE_DIR" ]; then
		note "the update folder $UPDATE_DIR can't be written, so the starts of the installed update can't be counted and it is not used; starting the version in the image"
		return 0
	fi

	# Starts since the installed program last proved itself. Anything that is
	# not a plain number counts as 0; leading zeros are dropped so the shell
	# never reads the number as octal.
	count=$(tr -d ' \t\r\n' <"$UPDATE_DIR/boot-count" 2>/dev/null)
	numeric "$count" || count=0
	while [ "${count#0}" != "$count" ]; do count=${count#0}; done
	[ -n "$count" ] || count=0
	[ ${#count} -le 6 ] || count=$MAX_BOOT_ATTEMPTS
	if [ "$count" -ge "$MAX_BOOT_ATTEMPTS" ]; then
		failed_version=$(head -n 1 "$UPDATE_DIR/VERSION" 2>/dev/null | tr -d ' \t\r')
		mv -f "$APP" "$UPDATE_DIR/app.failed" 2>/dev/null
		if [ -f "$UPDATE_DIR/VERSION" ]; then
			mv -f "$UPDATE_DIR/VERSION" "$UPDATE_DIR/VERSION.failed" 2>/dev/null
		fi
		rm -f "$UPDATE_DIR/app.sha256" "$UPDATE_DIR/boot-count" 2>/dev/null
		note "the installed update ${failed_version:-(unknown version)} stopped $count times in a row right after it started, so it was put aside (app.failed); starting the version in the image"
		return 0
	fi

	if [ -f "$UPDATE_DIR/app.sha256" ]; then
		want=$(head -n 1 "$UPDATE_DIR/app.sha256" 2>/dev/null | awk '{print $1}' | tr 'A-F' 'a-f')
		if [ -n "$want" ]; then
			if ! command -v sha256sum >/dev/null 2>&1; then
				note "sha256sum is missing, so the installed update can't be checked and is not used; starting the version in the image"
				return 0
			fi
			have=$(sha256sum "$APP" 2>/dev/null | awk '{print $1}')
			if [ "$have" != "$want" ]; then
				note "the installed update does not match its checksum (app.sha256); starting the version in the image"
				return 0
			fi
		fi
	fi

	if [ -z "$IMAGE_VERSION" ]; then
		note "the program in the image ($IMAGE_BIN) did not tell its version, so the installed update can't be compared with it and is not used"
		return 0
	fi

	if ! probe "$APP" || ! parse_line "$PROBE_OUT" || [ "$P_PLATFORM" != "$IMAGE_PLATFORM" ]; then
		note "the installed update does not answer as a Mediarium program for $IMAGE_PLATFORM; starting the version in the image"
		return 0
	fi

	accepts "$P_VERSION"
	case $? in
	0) ;;
	1)
		note "the installed update $P_VERSION is older than the version in the image ($IMAGE_VERSION); starting the version in the image"
		return 0
		;;
	*)
		note "the installed update says its version is \"$P_VERSION\", which is not a version number; starting the version in the image"
		return 0
		;;
	esac

	if ! printf '%d\n' $((count + 1)) >"$UPDATE_DIR/boot-count" 2>/dev/null; then
		note "the start counter in $UPDATE_DIR can't be written, so the installed update is not used; starting the version in the image"
		return 0
	fi

	note "starting the installed update $P_VERSION (the image has $IMAGE_VERSION)"
	CHOSEN=$APP
	return 0
}

# Only look for an update when the command starts the image's program.
uses_image=0
for arg in "$@"; do
	if [ "$arg" = "$IMAGE_BIN" ]; then
		uses_image=1
		break
	fi
done

if [ "$uses_image" = 1 ]; then
	choose
	if [ "$CHOSEN" != "$IMAGE_BIN" ]; then
		for arg in "$@"; do
			shift
			[ "$arg" = "$IMAGE_BIN" ] && arg=$CHOSEN
			set -- "$@" "$arg"
		done
	fi
fi

exec "$@"
