# sudo-logsrvd-wedge

Unbounded `submituser` in `sudo_logsrvd` drives the syslog line budget to exactly zero, hanging the root audit daemon from one unauthenticated packet.

Affected: sudo 1.9.17p2, current `main`, and the 1.9.15p5 package Ubuntu 24.04 ships.
Fixed in: unfixed at the time of writing. No CVE assigned.

Found and reported by Stanisław Kwiatkowski ([striga.ai](https://striga.ai)).

Writeup: https://striga.ai/research/sudo-logsrvd-submituser-wedge

## Requirements

- Docker
- Python 3

## Usage

```sh
docker compose build && docker compose up -d
docker compose exec attacker python3 /opt/wedge.py collector
```

This starts a collector running a vulnerable `sudo_logsrvd`, a sudo client pointed at it, and an attacker. One `AcceptMessage` carrying a 937-byte `submituser` drives `maxlen` to zero in `do_syslog_sudo()`, after which the daemon spins forever, keeps its listening socket, ignores `SIGTERM` and never serves another client.

The client shows the effect:

```sh
docker compose exec client runuser -u demo -- sudo -n cat /etc/shadow
```

It fails with `error initializing I/O plugin sudoers_io` after thirty seconds.

One byte either side of 937 is harmless, because only the clean zero hangs:

```sh
docker compose restart collector
docker compose exec attacker python3 /opt/wedge.py collector --mode control
```

## Cleanup

```sh
docker compose down
```

## Caution

This runs a knowingly vulnerable root daemon. Keep port 30343 inside the lab, and do not point a machine you need at the collector: once it is wedged, no new command runs through `sudo` on that host, including the one you would use to undo it.
