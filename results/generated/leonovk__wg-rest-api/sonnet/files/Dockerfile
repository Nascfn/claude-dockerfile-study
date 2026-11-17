# syntax=docker/dockerfile:1

# Ruby version matches .ruby-version
ARG RUBY_VERSION=4.0.6

# ---------------------------------------------------------------------------
# Build stage: compile native gems (puma, byebug, stackprof, ...)
# ---------------------------------------------------------------------------
FROM ruby:${RUBY_VERSION}-slim AS build

RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV BUNDLE_DEPLOYMENT=1 \
    BUNDLE_WITHOUT="development:test:rerun"

WORKDIR /app

COPY Gemfile Gemfile.lock ./
RUN bundle install --jobs 4 \
    && rm -rf /usr/local/bundle/cache \
    && find /usr/local/bundle -name "*.o" -delete \
    && find /usr/local/bundle -name "*.a" -delete

# ---------------------------------------------------------------------------
# Runtime stage
# ---------------------------------------------------------------------------
FROM ruby:${RUBY_VERSION}-slim

# The app shells out to wg / wg-quick (which needs ip, iptables, ip6tables).
# bash is required because the app runs `wg syncconf wg0 <(wg-quick strip wg0)`
# through Kernel.system, which relies on bash process substitution; /bin/sh is
# therefore pointed at bash below.
RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
        wireguard-tools \
        iproute2 \
        iptables \
        bash \
        openresolv \
    && ln -sf /bin/bash /bin/sh \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /etc/wireguard

ENV ENVIRONMENT=production \
    PORT=3000 \
    BUNDLE_DEPLOYMENT=1 \
    BUNDLE_WITHOUT="development:test:rerun"

WORKDIR /app

COPY --from=build /usr/local/bundle /usr/local/bundle
COPY . .

# WireGuard server config (wg0.conf) and the JSON state (wg0.json) live here.
VOLUME ["/etc/wireguard"]

# REST API (TCP) and WireGuard (UDP, default WG_PORT)
EXPOSE 3000/tcp
EXPOSE 51820/udp

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ruby -rnet/http -e 'exit(Net::HTTP.get_response(URI("http://127.0.0.1:#{ENV.fetch("PORT", "3000")}/healthz")).is_a?(Net::HTTPSuccess) ? 0 : 1)' || exit 1

# Runtime notes:
#   * Required env: AUTH_TOKEN (or AUTH_DIGEST_TOKEN), WG_HOST
#   * Needs: --cap-add=NET_ADMIN --cap-add=SYS_MODULE (if the kernel module must
#     be loaded) and sysctls net.ipv4.ip_forward=1,
#     net.ipv4.conf.all.src_valid_mark=1, and net.ipv6.conf.all.forwarding=1
#   * Example:
#       docker run -d --name wg-rest-api \
#         --cap-add=NET_ADMIN --cap-add=SYS_MODULE \
#         --sysctl net.ipv4.ip_forward=1 \
#         --sysctl net.ipv4.conf.all.src_valid_mark=1 \
#         --sysctl net.ipv6.conf.all.forwarding=1 \
#         -e AUTH_TOKEN=secret -e WG_HOST=your.server.ip \
#         -p 3000:3000 -p 51820:51820/udp \
#         -v wg-data:/etc/wireguard \
#         wg-rest-api
CMD ["bundle", "exec", "puma", "config.ru"]
