import selectors
import socket
import socks5
from config import Config
from State import State
from socks5 import handle_client
from dns_resolver import DnsResolver
from proxy import handle_proxy_io, ProxyConnection


def handle_new_connection(key: selectors.SelectorKey, selector: selectors.BaseSelector) -> None:
    sock = key.fileobj
    conn, addr = sock.accept()
    print("Accepted from", addr)
    conn.setblocking(False)
    data = {"handler": handle_client, "state": State.GREETING, "buffer": bytearray()}
    selector.register(conn, selectors.EVENT_READ, data=data)


def run_server(config: Config) -> None:
    selector = selectors.DefaultSelector() # Smart multiplexer for I/O

    # Server TCP-socket 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4, TCP
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Reuse address
    server_socket.setblocking(False) # Non-blocking mode
    server_socket.bind((config.host, config.port)) # Bind to address and port
    server_socket.listen() # Start listening for connections

    selector.register(server_socket, selectors.EVENT_READ, {'handler': handle_new_connection, 'state': None}) # Register server socket to selector

    dns_resolver = DnsResolver(selector) # Non-blocking UDP DNS resolver
    socks5.DNS_RESOLVER = dns_resolver # For asynchronous DNS resolution in socks5 module

    print(f"[SOCKS5 Proxy] Listening on {config.host}:{config.port}")
    try:
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
    except KeyboardInterrupt:
        print("\n[SOCKS5 Proxy] Shutting down...")
    finally:
        try:
            selector.unregister(server_socket)
        except Exception:
            pass
        try:
            server_socket.close()
        except Exception:
            pass

        selector.close()
        print("[SOCKS5 Proxy] Stopped.")


if __name__ == "__main__":
    run_server(Config()) # 127.0.0.1:8080 (localhost)