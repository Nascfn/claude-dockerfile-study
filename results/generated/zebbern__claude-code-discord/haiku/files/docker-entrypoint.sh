#!/bin/sh
# Container entrypoint for claude-code-discord.
# Prepares the workspace (WORK_DIR) that the bot operates on, then starts the bot.
set -eu

WORK_DIR="${WORK_DIR:-/app/workspace}"

mkdir -p "$WORK_DIR"

# Repos mounted from the host are often owned by another UID; without this,
# git refuses to read them and branch/repo detection fails at startup.
git config --global --replace-all safe.directory "$WORK_DIR"

# The bot expects a git repo in WORK_DIR. Initialize one if missing, the same
# way setup.sh does for native installs.
if ! git -C "$WORK_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  git -C "$WORK_DIR" init -q
fi

# Run from /app: index.ts and version-check.ts resolve deno.json relative to cwd.
exec deno run --allow-all /app/index.ts "$@"
