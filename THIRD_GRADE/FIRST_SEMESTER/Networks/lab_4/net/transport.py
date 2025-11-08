import asyncio, socket, struct

MCAST_GRP = "239.192.0.4"
MCAST_PORT = 9192

def _detect_default_iface_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
    except Exception:
        return "0.0.0.0"

class Transport:
    def __init__(self, loop: asyncio.AbstractEventLoop, state_delay_ms: int, mcast_iface_ip: str | None = None, uni_port: int | None = None):
        self.loop = loop
        self.state_delay_ms = state_delay_ms
        self.mcast_iface_ip = mcast_iface_ip or _detect_default_iface_ip()

        self.uni = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            self.uni.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError:
            pass
        try:
            self.uni.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except OSError:
            pass
        bind_port = 0 if uni_port is None else int(uni_port)
        self.uni.bind(('', bind_port))
        self.uni.setblocking(False)
        try:
            self.uni.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        except OSError:
            pass
        try:
            self.uni.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
        except OSError:
            pass
        try:
            iface = socket.inet_aton(self.mcast_iface_ip)
            self.uni.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, iface)
        except OSError:
            pass

        self.mc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            self.mc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError:
            pass
        try:
            self.mc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except OSError:
            pass
        try:
            self.mc.bind(('', MCAST_PORT))
        except OSError:
            self.mc.bind((MCAST_GRP, MCAST_PORT))
        try:
            mreq = struct.pack("=4s4s", socket.inet_aton(MCAST_GRP), socket.inet_aton(self.mcast_iface_ip))
            self.mc.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except OSError:
            mreq = struct.pack("=4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
            self.mc.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        try:
            self.mc.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        except OSError:
            pass
        self.mc.setblocking(False)
        self._mc_handler = None

    def unicast_addr(self):
        return self.uni.getsockname()

    async def recv_unicast(self):
        return await self.loop.sock_recvfrom(self.uni, 65535)

    async def send_unicast(self, addr, data: bytes):
        await self.loop.sock_sendto(self.uni, data, addr)

    async def send_multicast(self, data: bytes):
        await self.loop.sock_sendto(self.uni, data, (MCAST_GRP, MCAST_PORT))

    def on_multicast(self, cb):
        self._mc_handler = cb
        self.loop.add_reader(self.mc.fileno(), self._read_mc)

    def _read_mc(self):
        try:
            data, addr = self.mc.recvfrom(65535)
            if self._mc_handler:
                self._mc_handler(data, addr)
        except BlockingIOError:
            pass

    def close(self):
        try:
            self.loop.remove_reader(self.mc.fileno())
        except Exception:
            pass
        try:
            self.mc.close()
        finally:
            try:
                self.uni.close()
            except Exception:
                pass
