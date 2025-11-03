# snakenet/net/transport.py
import asyncio, socket, struct

MCAST_GRP = "239.192.0.4"
MCAST_PORT = 9192

class Transport:
    def __init__(self, loop: asyncio.AbstractEventLoop, state_delay_ms: int):
        self.loop = loop
        self.state_delay_ms = state_delay_ms

        # --- unicast socket (используем и для отправки multicast) ---
        self.uni = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Разрешим переиспользование порта (на macOS помогает запускать несколько процессов)
        try:
            self.uni.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError:
            pass
        try:
            self.uni.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except OSError:
            pass

        self.uni.bind(('', 0))   # OS chooses ephemeral port
        self.uni.setblocking(False)

        # Включим петлю мультикаста (чтобы локальный процесс тоже видел наши анонсы)
        try:
            self.uni.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        except OSError:
            pass
        # TTL=1 достаточно для локалки
        try:
            self.uni.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
        except OSError:
            pass
        # (опционально) можно указать исходящий интерфейс мультикаста:
        # iface = socket.inet_aton("0.0.0.0")  # авто-выбор системой
        # self.uni.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, iface)

        # --- multicast RX socket ---
        self.mc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # важно СНАЧАЛА включить reuse до bind
        try:
            self.mc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError:
            pass
        try:
            self.mc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except OSError:
            pass

        # Пробуем стандартный bind на 0.0.0.0:9192
        try:
            self.mc.bind(('', MCAST_PORT))
        except OSError:
            # На некоторых системах требуется bind на сам групповой адрес
            self.mc.bind((MCAST_GRP, MCAST_PORT))

        # Вступаем в группу на ВСЕХ интерфейсах (INADDR_ANY)
        mreq = struct.pack("=4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        self.mc.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # Включим петлю и на RX-сокете (обычно и так 1, но явно не повредит)
        try:
            self.mc.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        except OSError:
            pass

        self.mc.setblocking(False)
        self._mc_handler = None

    def unicast_addr(self):
        """Локальный адрес/порт нашего unicast-сокета (куда присылать Join)."""
        return self.uni.getsockname()  # (host, port)

    async def recv_unicast(self):
        """Получение любого unicast-пакета (State/Join/Ack/...)"""
        return await self.loop.sock_recvfrom(self.uni, 65535)  # bytes, addr

    async def send_unicast(self, addr, data: bytes):
        """Отправка unicast-пакета на addr=(ip,port)."""
        await self.loop.sock_sendto(self.uni, data, addr)

    async def send_multicast(self, data: bytes):
        """
        Отправка Announcement в группу С ТОГО ЖЕ ПОРТА, что слушает unicast.
        Это критично: клиент берёт адрес источника анонса и шлёт Join туда же.
        """
        await self.loop.sock_sendto(self.uni, data, (MCAST_GRP, MCAST_PORT))

    def on_multicast(self, cb):
        """Подписка на приём мультикаста; cb(data:bytes, addr) дергается из loop."""
        self._mc_handler = cb
        self.loop.add_reader(self.mc.fileno(), self._read_mc)

    def _read_mc(self):
        try:
            data, addr = self.mc.recvfrom(65535)
            # addr — это ИСТОЧНИК (ip, port) отправителя анонса (мастер), что нам и нужно.
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