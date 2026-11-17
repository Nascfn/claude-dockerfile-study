#!/bin/bash
set -e

cd /app

if [ -z "${AUTH_TOKEN}" ] && [ -z "${AUTH_DIGEST_TOKEN}" ]; then
  echo "WARNING: neither AUTH_TOKEN nor AUTH_DIGEST_TOKEN is set; all /api requests will be rejected." >&2
fi

mkdir -p "${WG_PATH:-/etc/wireguard}"

# Webhook notifications (beta) rely on `rake send_events` being run
# periodically. Only start the background loop when a webhook URL is set.
if [ -n "${WEBHOOKS_URL}" ]; then
  interval="${WEBHOOKS_INTERVAL:-60}"
  echo "Webhooks enabled: sending events every ${interval}s to ${WEBHOOKS_URL}"
  (
    # Give Puma time to bring up wg0 before the first run.
    sleep "${interval}"
    while true; do
      bundle exec rake send_events || echo "send_events failed" >&2
      sleep "${interval}"
    done
  ) &
fi

exec "$@"
