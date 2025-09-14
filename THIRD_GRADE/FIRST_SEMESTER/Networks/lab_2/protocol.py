import struct
import socket
from typing import Tuple

SIGN = b"AF52"        
MAX_NAME = 4096
MAX_SIZE = 1 << 40 


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """Receive exactly n bytes from the socket or raise ConnectionError."""
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("socket closed while receiving")
        buf += chunk
    return bytes(buf)


def pack_header(filename: str, filesize: int) -> bytes:
    """SIGNATURE + name_len(uint32 BE) + name(UTF-8) + size(uint64 BE)."""
    name_bytes = filename.encode("utf-8")
    if len(name_bytes) > MAX_NAME:
        raise ValueError("filename too long")
    if not (0 <= filesize <= MAX_SIZE):
        raise ValueError("invalid file size")
    header = bytearray()
    header += SIGN
    header += struct.pack(">I", len(name_bytes))
    header += name_bytes
    header += struct.pack(">Q", filesize)
    return bytes(header)


def unpack_header(sock: socket.socket) -> Tuple[str, int]:
    """Accept and parse the header from the socket."""
    SIGNATURE = recv_exact(sock, 4)
    if SIGNATURE != SIGN:
        raise ValueError("bad SIGNATURE header")
    name_len = struct.unpack(">I", recv_exact(sock, 4))[0]
    if not (0 <= name_len <= MAX_NAME):
        raise ValueError("bad name length")
    name = recv_exact(sock, name_len).decode("utf-8")
    size = struct.unpack(">Q", recv_exact(sock, 8))[0]
    if not (0 <= size <= MAX_SIZE):
        raise ValueError("invalid file size")
    return name, size


def send_reply(sock: socket.socket, ok: bool, msg: str = "") -> None:
    """Serve a reply to the client."""
    payload = msg.encode("utf-8")
    status = b"\x00" if ok else b"\x01"
    sock.sendall(status + struct.pack(">H", len(payload)) + payload)


def recv_reply(sock: socket.socket) -> Tuple[bool, str]:
    """Client-side reception of a reply."""
    ok = (recv_exact(sock, 1) == b"\x00")
    msg_len = struct.unpack(">H", recv_exact(sock, 2))[0]
    msg = recv_exact(sock, msg_len).decode("utf-8") if msg_len else ""
    return ok, msg