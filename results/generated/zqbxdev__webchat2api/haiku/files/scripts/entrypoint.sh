#!/bin/sh
# Container entrypoint for webchat2api.
#
# 1. Starts the Grok Browser Bridge (Node + system Chromium) in the background and
#    waits for its /health endpoint. The bridge is optional: if it cannot start, the
#    main service still runs, and Grok app-chat falls back to direct requests.
# 2. Replaces this shell with the requested command (default: python main.py).
#
# The Dockerfile runs this under tini (-g), so signals reach the bridge as well.

set -eu

BRIDGE_DIR="/app/services/browser_bridge"
BRIDGE_PORT="${BRIDGE_PORT:-3080}"
BRIDGE_WAIT_SECONDS="${BRIDGE_WAIT_SECONDS:-30}"

start_browser_bridge() {
    if [ ! -f "${BRIDGE_DIR}/server.js" ]; then
        echo "[entrypoint] Browser Bridge not found, skipping"
        return 0
    fi
    if ! command -v node >/dev/null 2>&1; then
        echo "[entrypoint] node not found, skipping Browser Bridge"
        return 0
    fi

    echo "[entrypoint] Starting Browser Bridge on port ${BRIDGE_PORT}..."
    node "${BRIDGE_DIR}/server.js" &
    bridge_pid=$!

    waited=0
    while [ "${waited}" -lt "${BRIDGE_WAIT_SECONDS}" ]; do
        if curl -fsS "http://127.0.0.1:${BRIDGE_PORT}/health" >/dev/null 2>&1; then
            echo "[entrypoint] Browser Bridge ready"
            return 0
        fi
        if ! kill -0 "${bridge_pid}" 2>/dev/null; then
            echo "[entrypoint] Browser Bridge exited during startup; continuing without it" >&2
            return 0
        fi
        waited=$((waited + 1))
        sleep 1
    done
    echo "[entrypoint] Browser Bridge not ready after ${BRIDGE_WAIT_SECONDS}s; continuing without it" >&2
    return 0
}

start_browser_bridge

if [ "$#" -eq 0 ]; then
    set -- python main.py
fi
exec "$@"
