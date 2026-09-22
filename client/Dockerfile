# A sudo client configured to send its audit trail to the collector.
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends sudo \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m -s /bin/bash demo \
    && printf 'demo ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/90-demo \
    && chmod 0440 /etc/sudoers.d/90-demo
# The two lines that put this host behind the collector. Both are required:
# without log_output the I/O plugin reports itself disabled and sudo fails open.
RUN printf 'Defaults log_servers = "collector:30343"\nDefaults log_output\n' \
        > /etc/sudoers.d/99-logsrv \
    && chmod 0440 /etc/sudoers.d/99-logsrv \
    && visudo -c
CMD ["sleep", "infinity"]
