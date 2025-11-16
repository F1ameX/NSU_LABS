import selectors
import socket
import sys

from State import State
from proxy import start_proxy_connection, send_socks_reply

SOCKS_VERSION = 5
METHOD_NO_AUTH = 0x00
CMD_CONNECT = 0x01
ATYP_IPV4 = 0x01
ATYP_DOMAIN = 0x03

DNS_RESOLVER = None


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