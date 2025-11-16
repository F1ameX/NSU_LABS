import selectors
import socket

from config import Config
from State import State
from socks5 import handle_client
from dns_resolver import DnsResolver
from proxy import handle_proxy_io, ProxyConnection


def handle_new_connection(key: selectors.SelectorKey,
                          selector: selectors.BaseSelector) -> None:
    sock = key.fileobj
    conn, addr = sock.accept()
    print("Accepted from", addr)
    conn.setblocking(False)
    data = {"handler": handle_client, "state": State.GREETING, "buffer": bytearray()}
    selector.register(conn, selectors.EVENT_READ, data=data)


def run_server(config: Config) -> None:
    selector = selectors.DefaultSelector()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(False)
    server_socket.bind((config.host, config.port))
    server_socket.listen()

    selector.register(server_socket, selectors.EVENT_READ,
                      {'handler': handle_new_connection, 'state': None})

    dns_resolver = DnsResolver(selector)

    import socks5
    socks5.DNS_RESOLVER = dns_resolver

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