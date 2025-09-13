import argparse
import ipaddress
import select
import signal
import socket
import struct
import sys
import time
from typing import Dict, Optional, Set, Tuple

MSG = b"alive"
HEARTBEAT_SEC = 1.0
EXPIRY_SEC = 3.5
RECV_BUF = 2048

DEFAULT_IFNAME: Optional[str] = None
DEFAULT_HOPS: int = 1
DEFAULT_LOOP: int = 1


def get_default_iface_v4_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 88))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def create_recv_socket(group_ip: str, port: int, ifname: Optional[str] = DEFAULT_IFNAME, loop: int = DEFAULT_LOOP) -> socket.socket:
    is_v6 = ":" in group_ip
    fam = socket.AF_INET6 if is_v6 else socket.AF_INET
    sock = socket.socket(fam, socket.SOCK_DGRAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    sock.settimeout(0)

    if is_v6:
        sock.bind(("::", port))
        group_bin = socket.inet_pton(socket.AF_INET6, group_ip)
        ifindex = socket.if_nametoindex(ifname) if ifname else 0
        mreq = struct.pack("16sI", group_bin, ifindex)
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
    else:
        sock.bind(("", port))
        iface_ip = get_default_iface_v4_ip()
        mreq = socket.inet_aton(group_ip) + socket.inet_aton(iface_ip)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock


def create_send_socket(group_ip: str, ifname: Optional[str] = DEFAULT_IFNAME, hops: int = DEFAULT_HOPS, loop: int = DEFAULT_LOOP) -> socket.socket:
    is_v6 = ":" in group_ip
    fam = socket.AF_INET6 if is_v6 else socket.AF_INET
    sock = socket.socket(fam, socket.SOCK_DGRAM)

    if is_v6:  
        ifindex = socket.if_nametoindex(ifname)
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_IF, struct.pack("I", ifindex))
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, hops)
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, int(loop))
    else:
        iface_ip = get_default_iface_v4_ip()
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(iface_ip))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, hops)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, int(loop))
    return sock


def main(group_ip: str, port: int, ifname: Optional[str]) -> None:
    hops = DEFAULT_HOPS
    loop = DEFAULT_LOOP

    is_v6 = ":" in group_ip
    dest = (group_ip, port, 0, 0) if is_v6 else (group_ip, port)

    recv_sock = create_recv_socket(group_ip, port, ifname, loop)
    send_sock = create_send_socket(group_ip, ifname, hops, loop)

    print(f"Multicast group: {group_ip} {ifname or ''} : {port} | family = {'IPv6' if is_v6 else 'IPv4'}")
    print(f"Loopback={'on' if loop else 'off'}, hop_limit/ttl={hops}")

    last_seen: Dict[Tuple[str, int], float] = {}
    last_printed_alive: Set[Tuple[str, int]] = set()
    last_beat = 0.0

    def handle_exit(signum, frame):
        print("\nExiting...")
        try:
            if is_v6:
                group_bin = socket.inet_pton(socket.AF_INET6, group_ip)
                ifindex = socket.if_nametoindex(ifname) if ifname else 0
                if ifindex:
                    mreq = struct.pack("16sI", group_bin, ifindex)
                    recv_sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_LEAVE_GROUP, mreq)
        except Exception:
            pass
        recv_sock.close()
        send_sock.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    while True:
        now = time.time()
        if now - last_beat >= HEARTBEAT_SEC:
            try:
                send_sock.sendto(MSG, dest)
            except Exception as e:
                print(f"send error: {e}")
            last_beat = now

        r, _, _ = select.select([recv_sock], [], [], 0.2)
        if r:
            try:
                data, addr = recv_sock.recvfrom(RECV_BUF)
                if data == MSG:
                    sender_ip, sender_port = addr[0], addr[1]
                    last_seen[(sender_ip, sender_port)] = now
            except BlockingIOError:
                pass
            except Exception as e:
                print(f"recv error: {e}")

        for peer, ts in list(last_seen.items()):
            if now - ts > EXPIRY_SEC:
                last_seen.pop(peer, None)

        alive_pairs = {peer for peer, ts in last_seen.items() if now - ts <= EXPIRY_SEC}
        if alive_pairs != last_printed_alive:
            uniq_ips = sorted({ip for (ip, _port) in alive_pairs})
            print(f"[{time.strftime('%H:%M:%S')}] alive peers: {sorted(alive_pairs)}")
            print(f"[{time.strftime('%H:%M:%S')}] alive IPs  : {uniq_ips}")
            last_printed_alive = alive_pairs

        time.sleep(0.02)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="ff02::1234")     
    parser.add_argument("--port", type=int, default=6666)
    parser.add_argument("--ifname", default="lo0")
    args = parser.parse_args()

    try:
        ipaddress.ip_address(args.host)
    except ValueError:
        print("Invalid IP address.")
        sys.exit(1)

    main(args.host, args.port, args.ifname)