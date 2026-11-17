#!/bin/sh
# Container startup: make sure the directories the bot inspects are git
# repositories (index.ts calls getGitInfo() from the cwd and exits otherwise),
# then exec the real command.
set -eu

# Mounted volumes are often owned by a different uid.
git config --global --add safe.directory '*'
git config --global --get user.name >/dev/null 2>&1 || git config --global user.name "claude-code-discord"
git config --global --get user.email >/dev/null 2>&1 || git config --global user.email "bot@localhost"

init_repo() {
  dir="$1"
  if [ ! -d "$dir/.git" ] && ! git -C "$dir" rev-parse --git-dir >/dev/null 2>&1; then
    echo "Initializing git repository in $dir"
    git -C "$dir" init -q -b main
    git -C "$dir" commit -q --allow-empty -m "Initial commit"
  fi
}

# Bot's own cwd (branch/repo detection, version check).
init_repo /app

# Claude's working directory (may be a mounted project).
if [ -n "${WORK_DIR:-}" ] && [ -d "$WORK_DIR" ]; then
  init_repo "$WORK_DIR"
fi

if [ -z "${DISCORD_TOKEN:-}" ] || [ -z "${APPLICATION_ID:-}" ]; then
  echo "Warning: DISCORD_TOKEN and/or APPLICATION_ID not set; pass them with --env-file .env or -e." >&2
fi

exec "$@"
