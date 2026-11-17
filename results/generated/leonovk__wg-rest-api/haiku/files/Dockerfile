# syntax=docker/dockerfile:1
#
# WireGuard REST API (Sinatra + Puma on Ruby 4.0.6)
#
# Build:
#   docker build -t wg-rest-api .
#
# Run. The app drives a WireGuard interface (wg, wg-quick, iptables), so the
# container needs NET_ADMIN and forwarding enabled. The host kernel must
# provide WireGuard (mainline Linux >= 5.6 does).
#
#   docker run -d --name wg-rest-api \
#     --cap-add NET_ADMIN \
#     --sysctl net.ipv4.ip_forward=1 \
#     --sysctl net.ipv6.conf.all.forwarding=1 \
#     -e AUTH_TOKEN=change-me \
#     -e WG_HOST=vpn.example.com \
#     -p 3000:3000 \
#     -p 51820:51820/udp \
#     -v wg-data:/etc/wireguard \
#     wg-rest-api
#
# Environment variables (see config/settings/production.yaml):
#   AUTH_TOKEN or AUTH_DIGEST_TOKEN  API authorization (required)
#   WG_HOST, WG_PORT, WG_DEFAULT_DNS, WG_ALLOWED_IPS, ...  WireGuard settings
#   PORT                              HTTP port (default 3000)
#   WG_PATH                           state and config directory (default /etc/wireguard)

ARG RUBY_VERSION=4.0.6

# ---------------------------------------------------------------------------
# Stage 1: install gems (needs compilers for native extensions such as puma,
# nio4r, byebug and stackprof, which the full ruby image provides)
# ---------------------------------------------------------------------------
FROM ruby:${RUBY_VERSION} AS build

ENV GEM_HOME=/usr/local/bundle \
    PATH=/usr/local/bundle/bin:$PATH \
    BUNDLE_WITHOUT=development:test:rerun

WORKDIR /app

# Gemfile.lock was generated with Bundler 2.5.9 ("BUNDLED WITH"). Install that
# exact version so Bundler does not have to fetch it during the build.
RUN gem install bundler -v 2.5.9 --no-document

COPY Gemfile Gemfile.lock ./
RUN bundle _2.5.9_ install \
 && rm -rf /usr/local/bundle/cache

# ---------------------------------------------------------------------------
# Stage 2: runtime
# ---------------------------------------------------------------------------
FROM ruby:${RUBY_VERSION}-slim AS runtime

ENV GEM_HOME=/usr/local/bundle \
    PATH=/usr/local/bundle/bin:$PATH \
    BUNDLE_WITHOUT=development:test:rerun \
    ENVIRONMENT=production \
    WG_PATH=/etc/wireguard \
    PORT=3000

# wireguard-tools provides wg and wg-quick; iptables/ip6tables are used in
# PostUp/PostDown rules; iproute2 is used by wg-quick; procps provides sysctl.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      wireguard-tools \
      iproute2 \
      iptables \
      procps \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# lib/wire_guard/server_config_updater.rb runs
#   Kernel.system('wg syncconf wg0 <(wg-quick strip wg0)')
# Ruby sends this string through /bin/sh. Debian's /bin/sh is dash, which does
# not support process substitution (<(...)), so peer changes would never be
# applied to the running interface. Point /bin/sh at bash.
RUN ln -sf /bin/bash /bin/sh

# Gems from the build stage (same Ruby version and base OS, so the native
# extensions are compatible).
COPY --from=build /usr/local/bundle /usr/local/bundle

WORKDIR /app
COPY . .

# Keeps WireGuard state (wg0.json, wg0.conf, wg0_stat.json, backups) and the
# server keys across container restarts.
RUN mkdir -p /etc/wireguard
VOLUME ["/etc/wireguard"]

EXPOSE 3000 51820/udp

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD ruby -rnet/http -e "exit(Net::HTTP.get_response(URI('http://127.0.0.1:' + ENV.fetch('PORT', '3000') + '/healthz')).is_a?(Net::HTTPSuccess) ? 0 : 1)"

# The app runs as root because it must create and configure the wg0 interface.
# config/config.rb brings wg0 up at boot when /etc/wireguard/wg0.conf exists.
# Puma loads config/puma.rb automatically.
CMD ["bundle", "_2.5.9_", "exec", "puma", "config.ru"]
