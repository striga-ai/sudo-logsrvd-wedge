# Vulnerable sudo_logsrvd collector.
#
# By default this uses the sudo package the distribution ships, which is enough
# to reproduce the hang: Ubuntu 24.04 carries sudo 1.9.15p5 and /usr/sbin/sudo_logsrvd
# comes with the base `sudo` package, not a separate one.
#
# To reproduce against the release the advisory names instead, build with:
#   docker compose build --build-arg SOURCE_BUILD=1 collector
FROM ubuntu:24.04

ARG SOURCE_BUILD=0
ARG SUDO_VERSION=1.9.17p2
ARG SUDO_SHA256=4a38a1ab3adb1199257edc2a7c4a2bd714665eb605b04368843b06dada2cfcfb

RUN apt-get update && apt-get install -y --no-install-recommends \
        sudo iproute2 procps ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN if [ "$SOURCE_BUILD" = "1" ]; then \
        apt-get update && apt-get install -y --no-install-recommends \
            build-essential libssl-dev zlib1g-dev pkg-config curl && \
        cd /tmp && curl -fLO "https://www.sudo.ws/dist/sudo-${SUDO_VERSION}.tar.gz" && \
        echo "${SUDO_SHA256}  sudo-${SUDO_VERSION}.tar.gz" | sha256sum -c - && \
        tar xzf "sudo-${SUDO_VERSION}.tar.gz" && cd "sudo-${SUDO_VERSION}" && \
        ./configure --prefix=/opt/sudo-plain --sysconfdir=/opt/sudo-plain/etc \
            --disable-nls --without-pam >/dev/null && \
        make -j"$(nproc)" >/dev/null && make install >/dev/null && \
        rm -f /opt/sudo-plain/bin/sudo /opt/sudo-plain/bin/sudoedit && \
        rm -rf /tmp/sudo-* /var/lib/apt/lists/* ; \
    fi

RUN mkdir -p /var/log/sudo-io /var/run/sudo
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
EXPOSE 30343
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
