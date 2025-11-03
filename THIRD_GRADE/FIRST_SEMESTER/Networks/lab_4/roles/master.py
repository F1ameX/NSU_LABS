# snakenet/roles/master.py
import asyncio
import random

from proto import snakes_pb2 as pb
from net.transport import Transport
from net.dispatcher import Dispatcher
from net.peers import Peers
from game.rules import Engine
from game.place import find_free_5x5
from game.snapshot import to_proto_state


class MasterController:
    def __init__(self, loop: asyncio.AbstractEventLoop, cfg, ui_push_state, player_name: str = "player"):
        self.loop = loop
        self.cfg = cfg
        self.transport = Transport(loop, cfg.state_delay_ms)
        self.dispatch = Dispatcher(cfg.state_delay_ms)
        self.peers = Peers()
        self.engine = Engine(cfg, rng=random.Random())
        self.players: dict[int, pb.GamePlayer] = {}
        self.next_player_id = 1  # скорректируем в start()
        self.ui_push_state = ui_push_state
        self.pending_steer: dict[int, int] = {}
        self.master_name = player_name

    async def start(self):
        # Мастер мультикаст не слушает (только шлёт), но регистрируем пустой хендлер для единообразия
        self.transport.on_multicast(lambda *_: None)

        # Создаём свою змею (игрок #1 — MASTER)
        self.players[1] = pb.GamePlayer(name=self.master_name, id=1, role=pb.MASTER, score=0)
        pos = find_free_5x5(set(), self.cfg.width, self.cfg.height) or (
            self.cfg.width // 2,
            self.cfg.height // 2,
        )
        self.engine.add_snake(1, pos, 0)  # tail_dir=UP

        # ВАЖНО: следующий выданный id = 2 (чтобы не пересекаться с мастером)
        self.next_player_id = 2

        self.tasks = [
            self.loop.create_task(self._loop_unicast()),
            self.loop.create_task(self._loop_tick()),
            self.loop.create_task(self._loop_announce()),
            self.loop.create_task(self._loop_retries()),
            self.loop.create_task(self._loop_ping()),
        ]

    async def stop(self):
        for t in getattr(self, "tasks", []):
            t.cancel()
        self.transport.close()

    async def _loop_unicast(self):
        while True:
            data, addr = await self.transport.recv_unicast()
            msg = pb.GameMessage()
            try:
                msg.ParseFromString(data)
            except Exception:
                continue

            # входящий Ack
            if msg.HasField("ack"):
                self.dispatch.ack(addr, msg.msg_seq)
                continue

            # отметим/создадим peer-запись
            peer = self.peers.touch(addr)

            # Join нового игрока (или повтор Join от того же addr)
            if msg.HasField("join"):
                pid, ok, reused = self._on_join(addr, msg, peer)
                if not ok:
                    # Ошибка уже отправлена в _on_join
                    continue

                # Ack с присвоенным player_id
                ack = pb.GameMessage(
                    msg_seq=self.dispatch.next_seq(),
                    sender_id=1,
                    receiver_id=pid,
                    ack=pb.GameMessage.AckMsg(),
                )
                payload = ack.SerializeToString()
                await self.transport.send_unicast(addr, payload)
                self.dispatch.track(addr, ack.msg_seq, payload)

                # Сразу отправим текущее состояние этому игроку (не ждём тик)
                players_pb = []
                for _pid, gp in self.players.items():
                    cp = pb.GamePlayer()
                    cp.name, cp.id, cp.role = gp.name, gp.id, gp.role
                    cp.score = self.engine.scores.get(_pid, 0)
                    players_pb.append(cp)
                state = to_proto_state(self.engine, players_pb)
                st_msg = pb.GameMessage(
                    msg_seq=self.dispatch.next_seq(),
                    state=pb.GameMessage.StateMsg(state=state),
                )
                data_state = st_msg.SerializeToString()
                await self.transport.send_unicast(addr, data_state)
                self.dispatch.track(addr, st_msg.msg_seq, data_state)
                # print(f"[MASTER] Join from {addr} -> pid={pid} reused={reused}")

            # Steer от игрока
            elif msg.HasField("steer") and msg.sender_id:
                # применяем только к живой змее отправителя
                sid = msg.sender_id
                if sid not in self.engine.snakes or not self.engine.snakes[sid].alive:
                    continue

                d = msg.steer.direction
                dir_map = {pb.UP: 0, pb.DOWN: 1, pb.LEFT: 2, pb.RIGHT: 3}
                self.pending_steer[sid] = dir_map[d]

                # Ack на SteerMsg (по протоколу)
                ack = pb.GameMessage(
                    msg_seq=self.dispatch.next_seq(),
                    sender_id=1,
                    receiver_id=sid,
                    ack=pb.GameMessage.AckMsg(),
                )
                payload = ack.SerializeToString()
                await self.transport.send_unicast(addr, payload)
                self.dispatch.track(addr, ack.msg_seq, payload)

            # Явный выход игрока → RoleChange(VIEWER)
            elif msg.HasField("role_change"):
                sender = msg.sender_id or 0
                # убрать змею и счёт
                self.engine.snakes.pop(sender, None)
                self.engine.scores.pop(sender, None)
                self.players.pop(sender, None)
                # отвязать pid от адреса
                if addr in self.peers.by_addr:
                    self.peers.by_addr[addr].player_id = None
                # подтверждение
                ack = pb.GameMessage(
                    msg_seq=self.dispatch.next_seq(),
                    sender_id=1,
                    receiver_id=sender,
                    ack=pb.GameMessage.AckMsg(),
                )
                payload = ack.SerializeToString()
                await self.transport.send_unicast(addr, payload)
                self.dispatch.track(addr, ack.msg_seq, payload)

            # Discover → отвечаем Announcement (unicast)
            elif msg.HasField("discover"):
                ann = self._build_announcement()
                out = pb.GameMessage(msg_seq=self.dispatch.next_seq(), announcement=ann)
                data2 = out.SerializeToString()
                await self.transport.send_unicast(addr, data2)
                self.dispatch.track(addr, out.msg_seq, data2)

    def _on_join(self, addr, msg: pb.GameMessage, peer) -> tuple[int, bool, bool]:
        """
        Пытаемся добавить игрока и его змею.
        Возвращает (pid, ok, reused). reused=True, если Join повторный (мы просто переотправим Ack/State).
        """
        # Если этот адрес уже получил pid — это повторный Join: ничего не добавляем.
        if peer.player_id:
            return peer.player_id, True, True

        # Подберём место 5x5
        occupied = {(c.x, c.y) for s in self.engine.snakes.values() for c in s.cells}
        pos = find_free_5x5(occupied, self.cfg.width, self.cfg.height)
        if not pos:
            err = pb.GameMessage(
                msg_seq=self.dispatch.next_seq(),
                error=pb.GameMessage.ErrorMsg(error_message="No 5x5 free area"),
            )
            self.loop.create_task(self.transport.send_unicast(addr, err.SerializeToString()))
            return 0, False, False

        # Выдаём новый pid и запоминаем его за адресом
        pid = self._alloc_player_id()
        peer.player_id = pid

        # Регистрируем игрока и спавним змею
        player_name = (msg.join.player_name or "player")[:32]
        gp = pb.GamePlayer(name=player_name, id=pid, role=pb.NORMAL, score=0)
        self.players[pid] = gp
        self.engine.add_snake(pid, pos, 0)  # tail_dir=UP

        return pid, True, False

    def _alloc_player_id(self):
        pid = self.next_player_id
        self.next_player_id += 1
        return pid

    def _build_announcement(self):
        ann = pb.GameMessage.AnnouncementMsg()
        ga = pb.GameAnnouncement()
        # Игроки
        for p in self.players.values():
            ga.players.players.append(p)
        # Конфиг
        ga.config.width = self.cfg.width
        ga.config.height = self.cfg.height
        ga.config.food_static = self.cfg.food_static
        ga.config.state_delay_ms = self.cfg.state_delay_ms
        # Прокинем unicast-порт мастера в имя игры
        _, uni_port = self.transport.unicast_addr()
        ga.can_join = True
        ga.game_name = f"snakenet:{uni_port}"
        ann.games.append(ga)
        return ann

    async def _loop_announce(self):
        while True:
            msg = pb.GameMessage(
                msg_seq=self.dispatch.next_seq(),
                announcement=self._build_announcement(),
            )
            await self.transport.send_multicast(msg.SerializeToString())
            await asyncio.sleep(1.0)

    async def _loop_tick(self):
        while True:
            # применим накопленные повороты
            for pid, d in list(self.pending_steer.items()):
                self.engine.steer(pid, d)
            self.pending_steer.clear()

            # шаг игрового движка
            self.engine.step()

            # соберём актуальные очки в pb.GamePlayer
            players_pb = []
            for pid, gp in self.players.items():
                cp = pb.GamePlayer()
                cp.name, cp.id, cp.role = gp.name, gp.id, gp.role
                cp.score = self.engine.scores.get(pid, 0)
                players_pb.append(cp)

            # сформируем и разошлём состояние
            state = to_proto_state(self.engine, players_pb)
            msg = pb.GameMessage(
                msg_seq=self.dispatch.next_seq(),
                state=pb.GameMessage.StateMsg(state=state),
            )
            data = msg.SerializeToString()

            if self.ui_push_state:
                self.ui_push_state(state)

            for addr, _peer in list(self.peers.by_addr.items()):
                await self.transport.send_unicast(addr, data)
                self.dispatch.track(addr, msg.msg_seq, data)

            await asyncio.sleep(self.cfg.state_delay_ms / 1000.0)

    async def _loop_retries(self):
        while True:
            for (addr, seq), payload in self.dispatch.due_retries():
                await self.transport.send_unicast(addr, payload)
            await asyncio.sleep(0.01)

    async def _loop_ping(self):
        while True:
            await asyncio.sleep(self.cfg.state_delay_ms / 1000.0 / 10.0)

    # Локальное управление мастером с клавиатуры (WASD)
    async def steer_local(self, direction_pb):
        dir_map = {pb.UP: 0, pb.DOWN: 1, pb.LEFT: 2, pb.RIGHT: 3}
        self.pending_steer[1] = dir_map[direction_pb]

    # Респаун мастера (локально, без протокола): сбросить счёт и переродиться
    async def respawn_self(self):
        pid = 1
        # удалить старую змею и счёт
        self.engine.snakes.pop(pid, None)
        self.engine.scores.pop(pid, None)
        # заново добавить
        occupied = {(c.x, c.y) for s in self.engine.snakes.values() for c in s.cells}
        pos = find_free_5x5(occupied, self.cfg.width, self.cfg.height) or (
            self.cfg.width // 2,
            self.cfg.height // 2,
        )
        self.engine.add_snake(pid, pos, 0)