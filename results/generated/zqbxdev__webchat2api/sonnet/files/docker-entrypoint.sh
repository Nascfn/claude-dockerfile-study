#!/bin/sh
set -e

cd /app

# Start the Grok browser bridge in the background (the backend talks to it on
# http://127.0.0.1:${BRIDGE_PORT}). Set DISABLE_BROWSER_BRIDGE=1 to skip it.
if [ "${DISABLE_BROWSER_BRIDGE:-0}" != "1" ]; then
    node services/browser_bridge/server.js &
fi

# Run the API server as PID 1 so it receives signals directly.
exec python main.py
