# syntax=docker/dockerfile:1

# WireGuard REST API (Sinatra + Puma)
#
# The container manages a WireGuard interface (wg0) itself, so it must be run
# with NET_ADMIN capability and the host kernel must support WireGuard, e.g.:
#
#   docker run -d --name wg-rest-api \
#     --cap-add=NET_ADMIN --cap-add=SYS_MODULE \
#     --sysctl net.ipv4.ip_forward=1 \
#     --sysctl net.ipv4.conf.all.src_valid_mark=1 \
#     --sysctl net.ipv6.conf.all.disable_ipv6=0 \
#     --sysctl net.ipv6.conf.all.forwarding=1 \
#     -e AUTH_TOKEN=your_secret_token \
#     -e WG_HOST=your.public.host \
#     -v wg-data:/etc/wireguard \
#     -p 51820:51820/udp -p 3000:3000 \
#     wg-rest-api

ARG RUBY_VERSION=4.0.6

########################################
# Build stage: compile gems
########################################
FROM ruby:${RUBY_VERSION}-slim AS build

RUN apt-get update -qq \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Use the Bundler that ships with the Ruby image instead of trying to
# auto-install the (older) version recorded in Gemfile.lock.
ENV BUNDLE_VERSION=system \
    BUNDLE_WITHOUT="development:test:rerun" \
    BUNDLE_JOBS=4 \
    BUNDLE_RETRY=3

COPY Gemfile Gemfile.lock ./
RUN bundle install \
 && rm -rf /usr/local/bundle/cache \
           /usr/local/bundle/gems/*/ext \
           /usr/local/bundle/gems/*/spec \
           /usr/local/bundle/gems/*/test

########################################
# Runtime stage
########################################
FROM ruby:${RUBY_VERSION}-slim

# wireguard-tools : wg / wg-quick
# iproute2        : `ip`, used by wg-quick
# iptables        : default PostUp/PostDown NAT rules (iptables + ip6tables)
# procps          : sysctl, used by wg-quick
# bash            : wg-quick and the app's `<(...)` process substitution
RUN apt-get update -qq \
 && apt-get install -y --no-install-recommends \
      wireguard-tools \
      iproute2 \
      iptables \
      procps \
      bash \
 && rm -rf /var/lib/apt/lists/* \
 # The app calls `wg syncconf wg0 <(wg-quick strip wg0)` via Kernel.system,
 # which runs through /bin/sh. Process substitution requires bash, so point
 # /bin/sh at bash (Debian's default is dash).
 && ln -sf /bin/bash /bin/sh

WORKDIR /app

ENV ENVIRONMENT=production \
    BUNDLE_VERSION=system \
    BUNDLE_WITHOUT="development:test:rerun" \
    PORT=3000 \
    WG_PATH=/etc/wireguard \
    PUMA_THREADS=1 \
    WORKERS=1

COPY --from=build /usr/local/bundle /usr/local/bundle
COPY . .
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh bin/wgpass \
 && mkdir -p "${WG_PATH}"

# WireGuard state: keys, wg0.json, wg0.conf, stats
VOLUME ["/etc/wireguard"]

EXPOSE 3000/tcp 51820/udp

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ruby -rnet/http -e 'r = Net::HTTP.get_response(URI("http://127.0.0.1:#{ENV.fetch("PORT", "3000")}/healthz")); exit(r.is_a?(Net::HTTPSuccess) ? 0 : 1)'

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["bundle", "exec", "puma", "-C", "config/puma.rb", "config.ru"]
