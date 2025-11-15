import selectors
import socket
import sys
import struct
from config import Config
from State import State

SOCKS_VERSION = 5
METHOD_NO_AUTH = 0x00
CMD_CONNECT = 0x01
ATYP_IPV4 = 0x01
ATYP_DOMAIN = 0x03

MAX_BUFFER_SIZE = 64 * 1024

DNS_RESOLVER = None


class ProxyConnection:
    def __init__(self, client_sock: socket.socket, remote_sock: socket.socket, target_addr: tuple[str, int]):
        self.client = client_sock
        self.remote = remote_sock
        self.target = target_addr
        self.buffer_c2r = bytearray()
        self.buffer_r2c = bytearray()
        self.client_eof = False
        self.remote_eof = False
        self.connecting = True
        self.closed = False
        self.client_registered = False
        self.remote_registered = False


def build_dns_query(name: str, txid: int) -> bytes:
    flags = 0x0100
    header = struct.pack("!HHHHHH", txid, flags, 1, 0, 0, 0)
    labels = name.strip(".").split(".")
    qname = b"".join(len(label).to_bytes(1, "big") + label.encode("ascii") for label in labels) + b"\x00"
    question = qname + struct.pack("!HH", 1, 1)
    return header + question


def _skip_dns_name(data: bytes, offset: int) -> int:
    length = data[offset]
    while length != 0:
        if length & 0xC0 == 0xC0:
            offset += 2
            return offset
        offset += 1 + length
        length = data[offset]
    offset += 1
    return offset


def parse_dns_response(data: bytes) -> tuple[int, list[str]]:
    if len(data) < 12:
        return 0, []
    txid, flags, qdcount, ancount, nscount, arcount = struct.unpack("!HHHHHH", data[:12])
    offset = 12
    for _ in range(qdcount):
        offset = _skip_dns_name(data, offset)
        offset += 4
    ips: list[str] = []
    for _ in range(ancount):
        offset = _skip_dns_name(data, offset)
        if offset + 10 > len(data):
            break
        rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", data[offset:offset + 10])
        offset += 10
        if offset + rdlength > len(data):
            break
        rdata = data[offset:offset + rdlength]
        offset += rdlength
        if rtype == 1 and rclass == 1 and rdlength == 4:
            ips.append(socket.inet_ntoa(rdata))
    return txid, ips


class DnsQuery:
    def __init__(self, hostname: str, port: int, client_sock: socket.socket, client_data: dict):
        self.hostname = hostname
        self.port = port
        self.client_sock = client_sock
        self.client_data = client_data


class DnsResolver:
    def __init__(self, selector: selectors.BaseSelector, server_addr: tuple[str, int] | None = None):
        self.server_addr = server_addr or ("8.8.8.8", 53)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.selector = selector
        self.selector.register(self.sock, selectors.EVENT_READ, data=self)
        self.pending: dict[int, DnsQuery] = {}
        self._next_id = 1

    def _next_txid(self) -> int:
        txid = self._next_id & 0xFFFF
        self._next_id = (self._next_id + 1) & 0xFFFF
        while txid in self.pending:
            txid = (txid + 1) & 0xFFFF
        return txid

    def resolve(self, hostname: str, port: int, client_sock: socket.socket, client_data: dict) -> None:
        txid = self._next_txid()
        message = build_dns_query(hostname, txid)
        self.pending[txid] = DnsQuery(hostname, port, client_sock, client_data)
        try:
            self.sock.sendto(message, self.server_addr)
        except BlockingIOError:
            self.pending.pop(txid, None)
            send_socks_reply(client_sock, 0x04, "0.0.0.0", 0)
            try:
                self.selector.unregister(client_sock)
            except Exception:
                pass
            try:
                client_sock.close()
            except Exception:
                pass

    def handle_read(self) -> None:
        try:
            data, addr = self.sock.recvfrom(512)
        except BlockingIOError:
            return
        txid, ips = parse_dns_response(data)
        query = self.pending.pop(txid, None)
        if query is None:
            return
        if not ips:
            send_socks_reply(query.client_sock, 0x04, "0.0.0.0", 0)
            try:
                self.selector.unregister(query.client_sock)
            except Exception:
                pass
            try:
                query.client_sock.close()
            except Exception:
                pass
            return
        ip = ips[0]
        start_proxy_connection(query.client_sock, query.client_data, self.selector, ip, query.port)


def send_socks_reply(sock: socket.socket, rep: int, bind_addr: str, bind_port: int) -> None:
    try:
        addr_bytes = socket.inet_aton(bind_addr)
    except OSError:
        addr_bytes = socket.inet_aton("0.0.0.0")
    reply = bytes([
        SOCKS_VERSION,
        rep,
        0x00,
        ATYP_IPV4,
    ]) + addr_bytes + bind_port.to_bytes(2, "big", signed=False)
    try:
        sock.send(reply)
    except BlockingIOError:
        pass


def start_proxy_connection(client_sock: socket.socket, client_data: dict,
                           selector: selectors.BaseSelector, ip: str, port: int) -> None:
    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote.setblocking(False)
    try:
        remote.connect((ip, port))
    except BlockingIOError:
        pass
    conn = ProxyConnection(client_sock, remote, (ip, port))
    try:
        selector.unregister(client_sock)
    except Exception:
        pass
    selector.register(client_sock, selectors.EVENT_READ, data=conn)
    conn.client_registered = True
    selector.register(remote, selectors.EVENT_WRITE, data=conn)
    conn.remote_registered = True
    print(f"Connecting to {ip}:{port}")


def handle_greeting_state(sock: socket.socket, data: dict) -> bool:
    buf: bytearray = data.setdefault("buffer", bytearray())
    if len(buf) < 2:
        return False
    ver = buf[0]
    if ver != SOCKS_VERSION:
        raise Exception("Unsupported SOCKS version")
    nmethods = buf[1]
    if len(buf) < 2 + nmethods:
        return False
    methods = buf[2:2 + nmethods]
    if METHOD_NO_AUTH not in methods:
        raise Exception("No suitable auth method")
    del buf[:2 + nmethods]
    response = bytes([SOCKS_VERSION, METHOD_NO_AUTH])
    try:
        sock.send(response)
    except BlockingIOError:
        pass
    data["state"] = State.CONNECTION_REQUEST
    return True


def handle_connection_request(sock: socket.socket, data: dict,
                              selector: selectors.BaseSelector) -> bool:
    buf: bytearray = data.setdefault("buffer", bytearray())
    if len(buf) < 4:
        return False
    ver, cmd, rsv, atyp = buf[0], buf[1], buf[2], buf[3]
    if ver != SOCKS_VERSION:
        raise Exception("Unsupported SOCKS version")
    if cmd != CMD_CONNECT:
        raise Exception("Only CONNECT command is supported")
    if rsv != 0x00:
        raise Exception("Reserved field must be 0")
    offset = 4
    if atyp == ATYP_IPV4:
        if len(buf) < offset + 4 + 2:
            return False
        addr_bytes = buf[offset:offset + 4]
        offset += 4
        port_bytes = buf[offset:offset + 2]
        offset += 2
        host = socket.inet_ntoa(addr_bytes)
        port = int.from_bytes(port_bytes, "big")
        del buf[:offset]
        start_proxy_connection(sock, data, selector, host, port)
        return False
    elif atyp == ATYP_DOMAIN:
        if len(buf) < offset + 1:
            return False
        name_len = buf[offset]
        offset += 1
        if len(buf) < offset + name_len + 2:
            return False
        name_bytes = buf[offset:offset + name_len]
        offset += name_len
        port_bytes = buf[offset:offset + 2]
        offset += 2
        host = name_bytes.decode("ascii", errors="ignore")
        port = int.from_bytes(port_bytes, "big")
        del buf[:offset]
        data["state"] = State.RESOLVING
        if DNS_RESOLVER is None:
            raise RuntimeError("DNS resolver is not initialized")
        DNS_RESOLVER.resolve(host, port, sock, data)
        return False
    else:
        raise Exception("Address type not supported")


def handle_client(key: selectors.SelectorKey, selector: selectors.BaseSelector) -> None:
    sock = key.fileobj
    data: dict = key.data
    buf: bytearray = data.setdefault("buffer", bytearray())
    try:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionResetError()
        buf.extend(chunk)
        while True:
            if data["state"] == State.GREETING:
                if not handle_greeting_state(sock, data):
                    break
            elif data["state"] == State.CONNECTION_REQUEST:
                if not handle_connection_request(sock, data, selector):
                    break
            elif data["state"] == State.RESOLVING:
                break
            else:
                break
    except Exception as e:
        print("Client handler error:", e, file=sys.stderr)
        try:
            selector.unregister(sock)
        except Exception:
            pass
        try:
            sock.close()
        except Exception:
            pass


def update_events_for(conn: ProxyConnection, selector: selectors.BaseSelector,
                      sock: socket.socket) -> None:
    if conn.closed:
        return
    if sock is conn.client:
        registered_attr = "client_registered"
        want_read = (not conn.client_eof) and (len(conn.buffer_c2r) < MAX_BUFFER_SIZE)
        want_write = len(conn.buffer_r2c) > 0
    else:
        registered_attr = "remote_registered"
        if conn.connecting:
            want_read = False
            want_write = True
        else:
            want_read = (not conn.remote_eof) and (len(conn.buffer_r2c) < MAX_BUFFER_SIZE)
            want_write = len(conn.buffer_c2r) > 0
    events = 0
    if want_read:
        events |= selectors.EVENT_READ
    if want_write:
        events |= selectors.EVENT_WRITE
    registered = getattr(conn, registered_attr)
    try:
        if events == 0:
            if registered:
                selector.unregister(sock)
                setattr(conn, registered_attr, False)
        else:
            if registered:
                selector.modify(sock, events, conn)
            else:
                selector.register(sock, events, conn)
                setattr(conn, registered_attr, True)
    except KeyError:
        pass


def handle_proxy_io(key: selectors.SelectorKey, mask: int,
                    selector: selectors.BaseSelector) -> None:
    conn: ProxyConnection = key.data
    sock: socket.socket = key.fileobj
    other = conn.remote if sock is conn.client else conn.client
    if conn.closed:
        return
    try:
        if conn.connecting and sock is conn.remote and (mask & selectors.EVENT_WRITE):
            err = conn.remote.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if err != 0:
                send_socks_reply(conn.client, 0x05, "0.0.0.0", 0)
                cleanup_proxy(conn, selector)
                return
            conn.connecting = False
            try:
                bind_addr, bind_port = conn.remote.getsockname()
            except OSError:
                bind_addr, bind_port = "0.0.0.0", 0
            send_socks_reply(conn.client, 0x00, bind_addr, bind_port)
            update_events_for(conn, selector, conn.remote)
            update_events_for(conn, selector, conn.client)
        if not conn.connecting:
            if mask & selectors.EVENT_READ:
                if sock is conn.client and len(conn.buffer_c2r) >= MAX_BUFFER_SIZE:
                    update_events_for(conn, selector, sock)
                elif sock is conn.remote and len(conn.buffer_r2c) >= MAX_BUFFER_SIZE:
                    update_events_for(conn, selector, sock)
                else:
                    data = sock.recv(4096)
                    if not data:
                        if sock is conn.client:
                            conn.client_eof = True
                        else:
                            conn.remote_eof = True
                        update_events_for(conn, selector, sock)
                    else:
                        if sock is conn.client:
                            conn.buffer_c2r.extend(data)
                            update_events_for(conn, selector, conn.remote)
                        else:
                            conn.buffer_r2c.extend(data)
                            update_events_for(conn, selector, conn.client)
                        update_events_for(conn, selector, sock)
            if mask & selectors.EVENT_WRITE:
                if sock is conn.client:
                    buf = conn.buffer_r2c
                else:
                    buf = conn.buffer_c2r
                if buf:
                    sent = sock.send(buf)
                    if sent == 0:
                        raise ConnectionError("send returned 0")
                    del buf[:sent]
                    update_events_for(conn, selector, sock)
                    update_events_for(conn, selector, other)
        if conn.client_eof and conn.remote_eof and not conn.buffer_c2r and not conn.buffer_r2c:
            cleanup_proxy(conn, selector)
    except Exception as e:
        print("Proxy IO error:", e, file=sys.stderr)
        cleanup_proxy(conn, selector)


def cleanup_proxy(conn: ProxyConnection, selector: selectors.BaseSelector) -> None:
    if conn.closed:
        return
    conn.closed = True
    for s, attr in ((conn.client, "client_registered"), (conn.remote, "remote_registered")):
        try:
            if getattr(conn, attr):
                selector.unregister(s)
        except Exception:
            pass
        setattr(conn, attr, False)
        try:
            s.close()
        except Exception:
            pass


def handle_new_connection(key: selectors.SelectorKey,
                          selector: selectors.BaseSelector) -> None:
    sock = key.fileobj
    conn, addr = sock.accept()
    print("Accepted from", addr)
    conn.setblocking(False)
    data = {"handler": handle_client, "state": State.GREETING, "buffer": bytearray()}
    selector.register(conn, selectors.EVENT_READ, data=data)


def run_server(config: Config) -> None:
    global DNS_RESOLVER
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(False)
    server_socket.bind((config.host, config.port))
    server_socket.listen()
    selector = selectors.DefaultSelector()
    selector.register(server_socket, selectors.EVENT_READ,
                      {'handler': handle_new_connection, 'state': None})
    DNS_RESOLVER = DnsResolver(selector)
    print(f"[SOCKS5 Proxy] Listening on {config.host}:{config.port}")
    while True:
        events = selector.select()
        for key, mask in events:
            data = key.data
            if isinstance(data, dict):
                callback = data['handler']
                callback(key, selector)
            elif isinstance(data, ProxyConnection):
                handle_proxy_io(key, mask, selector)
            elif isinstance(data, DnsResolver):
                data.handle_read()


if __name__ == "__main__":
    run_server(Config())