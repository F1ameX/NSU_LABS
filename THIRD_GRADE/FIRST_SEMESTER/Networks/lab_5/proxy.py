import selectors
import socket
import sys

SOCKS_VERSION = 5
ATYP_IPV4 = 0x01
MAX_BUFFER_SIZE = 64 * 1024


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


def cleanup_proxy(conn: ProxyConnection, selector: selectors.BaseSelector) -> None:
    if conn.closed:
        return
    conn.closed = True    # noqa: E702
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