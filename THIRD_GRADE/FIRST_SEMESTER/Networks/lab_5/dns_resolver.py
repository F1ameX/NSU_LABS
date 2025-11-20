import selectors
import socket
import struct
from proxy import send_socks_reply, start_proxy_connection


def build_dns_query(name: str, txid: int) -> bytes:
    flags = 0x0100 # Recursion Desired (only IP)
    '''
    Big-endian DNS query message, 12 bytes
    Txid - unique identifier
    Flags - recursion desired
    QDCOUNT - 1 question
    ANCOUNT, NSCOUNT, ARCOUNT - 0
    '''
    header = struct.pack("!HHHHHH", txid, flags, 1, 0, 0, 0)
    labels = name.strip(".").split(".")
    # <length byte><label><length byte><label>...<0 byte>
    qname = b"".join(len(label).to_bytes(1, "big") + label.encode("ascii") for label in labels) + b"\x00" 
    question = qname + struct.pack("!HH", 1, 1) # IPv4, Internet 
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
    if len(data) < 12: # No header
        return 0, []
    txid, _, qdcount, ancount, _, _ = struct.unpack("!HHHHHH", data[:12])
    offset = 12
    for _ in range(qdcount):
        offset = _skip_dns_name(data, offset)
        offset += 4
    ips: list[str] = []
    for _ in range(ancount):
        offset = _skip_dns_name(data, offset)
        if offset + 10 > len(data):
            break
        rtype, rclass, _, rdlength = struct.unpack("!HHIH", data[offset:offset + 10])
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
        start = self._next_id & 0xFFFF
        txid = start

        for _ in range(65536):
            if txid not in self.pending:
                self._next_id = (txid + 1) & 0xFFFF
                return txid
            txid = (txid + 1) & 0xFFFF

        return -1

    def resolve(self, hostname, port, client_sock, client_data):
        txid = self._next_txid()

        if txid == -1:
            send_socks_reply(client_sock, 0x04, "0.0.0.0", 0)
            try: 
                self.selector.unregister(client_sock)
            except: 
                pass
            client_sock.close()
            return

        message = build_dns_query(hostname, txid)
        self.pending[txid] = DnsQuery(hostname, port, client_sock, client_data)

        try:
            self.sock.sendto(message, self.server_addr)
        except BlockingIOError:
            self.pending.pop(txid, None)
            send_socks_reply(client_sock, 0x04, "0.0.0.0", 0)
            try: 
                self.selector.unregister(client_sock)
            except: 
                pass
            client_sock.close()

    def handle_read(self) -> None:
        try:
            data, _ = self.sock.recvfrom(512)
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
        start_proxy_connection(query.client_sock, self.selector, ip, query.port)