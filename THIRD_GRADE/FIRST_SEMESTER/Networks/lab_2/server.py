import argparse
import os
import socket
import threading
import time
from typing import Tuple

from protocol import unpack_header, send_reply

UPLOADS_DIR = "uploads"

def ensure_uploads_dir() -> str:
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    return os.path.realpath(UPLOADS_DIR)


def safe_target_path(upload_dir_real: str, filename: str) -> str:
    """
    Garantees that the returned path is inside upload_dir_real. 
    If the file already exists, appends " (N)" before the extension.
    """
    candidate = os.path.join(upload_dir_real, filename)
    real = os.path.realpath(candidate)
    if not real.startswith(upload_dir_real + os.sep):
        base_only = os.path.basename(filename)
        real = os.path.realpath(os.path.join(upload_dir_real, base_only))
        if not real.startswith(upload_dir_real + os.sep):
            raise ValueError("invalid path")

    if not os.path.exists(real):
        return real
    base, ext = os.path.splitext(real)
    i = 1
    while True:
        alt = f"{base} ({i}){ext}"
        if not os.path.exists(alt):
            return alt
        i += 1


def human_bps(bps: float) -> str:
    units = ["B/s", "KB/s", "MB/s", "GB/s"]
    v = bps
    u = 0
    while v >= 1024 and u < len(units) - 1:
        v /= 1024.0
        u += 1
    return f"{v:.2f} {units[u]}"


def recv_file(sock: socket.socket, size: int, dst_path: str, client_tag: str) -> Tuple[int, float]:
    """
    Accepts exactly size bytes and writes to dst_path.
    Every ~3 seconds prints inst/avg speed; at least one message per session.
    """
    bytes_total = 0
    bytes_window = 0
    t_session0 = time.monotonic()
    t_window0 = t_session0
    printed = False

    with open(dst_path, "wb") as f:
        while bytes_total < size:
            need = min(65536, size - bytes_total)
            chunk = sock.recv(need)
            if not chunk:
                raise ConnectionError("peer closed before sending all data")
            f.write(chunk)
            n = len(chunk)
            bytes_total += n
            bytes_window += n

            now = time.monotonic()
            if now - t_window0 >= 3.0:
                inst = bytes_window / (now - t_window0)
                avg = bytes_total / (now - t_session0)
                print(f"[{client_tag}] inst={human_bps(inst)}, avg={human_bps(avg)}")
                t_window0 = now
                bytes_window = 0
                printed = True

    if not printed:
        now = time.monotonic()
        dur = max(now - t_session0, 1e-9)
        bps = bytes_total / dur
        print(f"[{client_tag}] inst={human_bps(bps)}, avg={human_bps(bps)}")

    duration = time.monotonic() - t_session0
    return bytes_total, duration


def handle_client(conn: socket.socket, addr: Tuple[str, int], uploads_real: str) -> None:
    client_tag = f"{addr[0]}:{addr[1]}"
    try:
        filename, size = unpack_header(conn)
        
        target_path = safe_target_path(uploads_real, filename)
        rel_name = os.path.relpath(target_path, uploads_real)

        print(f"[{client_tag}] incoming file: '{rel_name}' ({size} bytes)")
        received, dur = recv_file(conn, size, target_path, client_tag)

        ok = (received == size)
        if ok:
            msg = f"OK: saved '{rel_name}', {received} bytes in {dur:.2f} s"
        else:
            msg = f"ERROR: size mismatch (got {received}, expected {size})"
        send_reply(conn, ok, msg)
        print(f"[{client_tag}] done: {msg}")

    except Exception as e:
        try:
            send_reply(conn, False, f"ERROR: {e}")
        except Exception:
            pass
        print(f"[{client_tag}] aborted: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def serve(host: str, port: int) -> None:
    uploads_real = ensure_uploads_dir()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(128)
        print(f"Server listening on {host}:{port}, uploads dir: {uploads_real}")

        while True:
            try:
                conn, addr = srv.accept()
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
            t = threading.Thread(target=handle_client, args=(conn, addr, uploads_real), daemon=True)
            t.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=12345)
    args = parser.parse_args()
    serve(args.host, args.port)