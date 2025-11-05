import asyncio, socket, struct

MCAST_GRP = "239.192.0.4"
MCAST_PORT = 9192

class Transport:
    def __init__(self, loop: asyncio.AbstractEventLoop, state_delay_ms: int):
        self.loop = loop # Asyncio event loop
        self.state_delay_ms = state_delay_ms

        self.uni = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # IPv4, UDP-socket, UDP-protocol
        self.uni.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Socket level, reuse address
        self.uni.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) # Socket level, reuse port

        self.uni.bind(('', 0)) # Bind to any address, any port
        self.uni.setblocking(False) # Non-blocking mode

        self.uni.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1) # Multicast loopback
        self.uni.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1)) # Multicast TTL = 1


        self.mc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # IPv4, UDP-socket, UDP-protocol
        self.mc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Socket level, reuse address
        self.mc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) # Socket level, reuse port


        try:
            self.mc.bind(('', MCAST_PORT)) # Bind to any address, multicast port
        except OSError:
            self.mc.bind((MCAST_GRP, MCAST_PORT)) # Bind to multicast address, multicast port

        mreq = struct.pack("=4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY) # =: native byte order, 4s: 4-byte string, l: long

        self.mc.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq) # Join multicast group
        self.mc.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1) # Multicast loopback

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
        self._mc_handler = cb # Callback for incoming multicast packets
        self.loop.add_reader(self.mc.fileno(), self._read_mc)

    def _read_mc(self):
        try:
            data, addr = self.mc.recvfrom(65535) # Non-blocking UDP recv
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