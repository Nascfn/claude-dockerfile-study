#!/bin/sh
# Container entrypoint for webchat2api.
#
# 1. Optionally starts the Grok Browser Bridge (Node + Playwright + system
#    Chromium) in the background on 127.0.0.1:${BRIDGE_PORT}. The Python
#    backend auto-detects it at http://127.0.0.1:3080 and only accepts a
#    loopback bridge URL, so it has to live in the same container.
# 2. Runs the FastAPI backend (main.py) in the foreground.
set -e

cd /app
mkdir -p /app/data

if [ "${ENABLE_BROWSER_BRIDGE:-1}" = "1" ]; then
    if [ -x "${CHROMIUM_PATH:-/usr/bin/chromium}" ] && command -v node >/dev/null 2>&1; then
        echo "[entrypoint] Starting Browser Bridge on port ${BRIDGE_PORT:-3080}"
        (cd /app/services/browser_bridge && exec node server.js) &
    else
        echo "[entrypoint] Browser Bridge skipped: node or Chromium not found" >&2
    fi
else
    echo "[entrypoint] Browser Bridge disabled (ENABLE_BROWSER_BRIDGE=${ENABLE_BROWSER_BRIDGE})"
fi

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec python main.py
