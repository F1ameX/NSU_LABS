# snakenet/roles/normal.py
import asyncio
import time

from proto import snakes_pb2 as pb
from net.transport import Transport
from net.dispatcher import Dispatcher
from net.peers import Peers


class NormalController:
    """
    NORMAL-узел:
      - слушает multicast Announcement
      - делает Join к выбранной игре (ровно один раз)
      - шлёт Steer мастеру
      - принимает State и отправляет Ack на каждый StateMsg
      - пушит pb.GameState в UI через ui_push_state
    """

    def __init__(self, loop, cfg, ui_push_state, ui_set_games):
        self.loop = loop
        self.cfg = cfg
        self.transport = Transport(loop, cfg.state_delay_ms)
        self.dispatch = Dispatcher(cfg.state_delay_ms)
        self.peers = Peers()

        self.player_id: int | None = None
        self.center: tuple[str, int] | None = None  # текущий адрес мастера (ip, port)
        self.joining: bool = False  # флаг «Join отправлен, ждём Ack»

        self.ui_push_state = ui_push_state
        self.ui_set_games = ui_set_games

        # Множество/словарь игр по уникальному ключу (ip, port)
        self.games_map: dict[tuple[str, int], str] = {}           # (ip,port) -> name
        self.games: list[tuple[str, tuple[str, int]]] = []        # [(name, (ip,port))] для UI

        self._last_unicast = time.monotonic()

    # ---- lifecycle ----
    async def start(self):
        self.transport.on_multicast(self._on_mc)
        self.tasks = [
            self.loop.create_task(self._loop_unicast()),
            self.loop.create_task(self._loop_retries()),
            self.loop.create_task(self._loop_timeout()),
        ]

    async def stop(self):
        for t in getattr(self, "tasks", []):
            t.cancel()
        self.transport.close()

    # ---- multicast handler ----
    def _on_mc(self, data, addr):
        msg = pb.GameMessage()
        try:
            msg.ParseFromString(data)
        except Exception:
            return

        if msg.HasField("announcement") and msg.announcement.games:
            g = msg.announcement.games[0]
            name = g.game_name or "snakenet"

            # извлекаем реальный unicast-порт из имени игры "snakenet:<port>"
            port = addr[1]
            try:
                if ":" in name:
                    _, p = name.rsplit(":", 1)
                    p_int = int(p)
                    if 1 <= p_int <= 65535:
                        port = p_int
            except Exception:
                pass

        fixed_addr = (addr[0], port)
        # обновляем/добавляем уникальную запись по ключу (ip,port)
        self.games_map[fixed_addr] = name

        # Строим список для UI (стабильно отсортируем по ip, затем по порту)
        self.games = [(nm, ad) for ad, nm in sorted(self.games_map.items(), key=lambda x: (x[0][0], x[0][1]))]

        if self.ui_set_games:
            self.ui_set_games(self.games)

    # ---- unicast RX loop ----
    async def _loop_unicast(self):
        while True:
            data, addr = await self.transport.recv_unicast()
            self._last_unicast = time.monotonic()

            # Любой входящий unicast считаем «правильным» адресом мастера
            if self.center != addr:
                self.center = addr
                self.peers.set_center(addr)

            msg = pb.GameMessage()
            try:
                msg.ParseFromString(data)
            except Exception:
                continue

            # входящий Ack
            if msg.HasField("ack"):
                self.dispatch.ack(addr, msg.msg_seq)
                # Ack на Join содержит наш player_id в receiver_id
                if msg.receiver_id and not self.player_id:
                    self.player_id = msg.receiver_id
                    self.joining = False  # Join завершён
                continue

            # входящий State — пробрасываем в UI и подтверждаем Ack'ом
            if msg.HasField("state"):
                if self.ui_push_state:
                    self.ui_push_state(msg.state.state)

                # по протоколу подтверждаем StateMsg
                if self.center:
                    ack = pb.GameMessage(
                        msg_seq=self.dispatch.next_seq(),
                        sender_id=self.player_id or 0,
                        receiver_id=0,
                        ack=pb.GameMessage.AckMsg(),
                    )
                    data_ack = ack.SerializeToString()
                    await self.transport.send_unicast(self.center, data_ack)
                    self.dispatch.track(self.center, ack.msg_seq, data_ack)
                continue

            # входящая ошибка — можно показать в UI; также даём повторить Join
            if msg.HasField("error"):
                self.joining = False

    # ---- commands ----
    async def join(self, game_idx: int, player_name: str):
        """Подключиться к игре по индексу (обычно 0). Второй Join не отправляем, если уже есть player_id или Join в процессе."""
        if self.player_id is not None or self.joining:
            return
        if not (0 <= game_idx < len(self.games)):
            return
        game_name, addr = self.games[game_idx]  # addr уже (ip,port)
        self.center = addr
        self.peers.set_center(addr)

        join = pb.GameMessage.JoinMsg(
            player_type=pb.HUMAN,
            player_name=player_name,
            game_name=game_name,
            requested_role=pb.NORMAL,
        )
        msg = pb.GameMessage(msg_seq=self.dispatch.next_seq(), join=join)
        data = msg.SerializeToString()
        await self.transport.send_unicast(addr, data)
        self.dispatch.track(addr, msg.msg_seq, data)
        self.joining = True

    async def steer(self, direction_pb):
        """Отправка Steer мастеру. direction_pb — одно из {pb.UP, pb.DOWN, pb.LEFT, pb.RIGHT}."""
        if not self.center or self.player_id is None:
            return
        steer = pb.GameMessage.SteerMsg(direction=direction_pb)
        msg = pb.GameMessage(
            msg_seq=self.dispatch.next_seq(),
            sender_id=self.player_id,
            receiver_id=0,
            steer=steer,
        )
        data = msg.SerializeToString()
        await self.transport.send_unicast(self.center, data)
        self.dispatch.track(self.center, msg.msg_seq, data)

    async def leave_and_respawn(self, game_idx: int, player_name: str):
        """
        RoleChange(VIEWER) -> короткая пауза -> Join заново с новым pid и обнулённым счётом.
        Пауза нужна, чтобы мастер успел отвязать старый pid от нашего addr.
        """
        if not self.center or self.joining:
            return
        # 1) Явный выход
        rc = pb.GameMessage.RoleChangeMsg(sender_role=pb.VIEWER)
        msg = pb.GameMessage(msg_seq=self.dispatch.next_seq(), sender_id=self.player_id or 0, role_change=rc)
        data = msg.SerializeToString()
        await self.transport.send_unicast(self.center, data)
        self.dispatch.track(self.center, msg.msg_seq, data)

        # 2) Небольшая пауза и новый Join
        self.player_id = None
        await asyncio.sleep(0.05)
        await self.join(game_idx, player_name)

    # ---- service loops ----
    async def _loop_retries(self):
        while True:
            for (addr, seq), payload in self.dispatch.due_retries():
                await self.transport.send_unicast(addr, payload)
            await asyncio.sleep(0.01)

    async def _loop_timeout(self):
        while True:
            if time.monotonic() - self._last_unicast > 0.8 * (self.cfg.state_delay_ms / 1000.0):
                # Можно уведомить UI, в MVP — молчим (Esc → Lobby)
                pass
            await asyncio.sleep(0.05)