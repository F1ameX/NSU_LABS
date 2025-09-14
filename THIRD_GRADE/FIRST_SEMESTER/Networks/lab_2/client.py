import argparse
import os
import socket

from protocol import pack_header, recv_reply


def send_file(host: str, port: int, path: str, tcp_buf: int = 1 << 16) -> int:
    filename = os.path.basename(path)
    size = os.path.getsize(path)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))

        header = pack_header(filename, size)
        sock.sendall(header)

        sent = 0
        try:
            sendfile = getattr(os, "sendfile", None)
            if sendfile is not None:
                with open(path, "rb") as f:
                    offset = 0
                    while offset < size:
                        n = os.sendfile(sock.fileno(), f.fileno(), offset, size - offset)
                        if n == 0:
                            break
                        offset += n
                        sent = offset
            else:
                with open(path, "rb") as f:
                    while True:
                        chunk = f.read(tcp_buf)
                        if not chunk:
                            break
                        sock.sendall(chunk)
                        sent += len(chunk)
        except Exception:
            raise

        ok, msg = recv_reply(sock)
        print(("SUCCESS" if ok else "FAIL") + f": {msg}")
        return 0 if ok else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("file")
    args = parser.parse_args()

    exit(send_file(args.host, args.port, args.file))