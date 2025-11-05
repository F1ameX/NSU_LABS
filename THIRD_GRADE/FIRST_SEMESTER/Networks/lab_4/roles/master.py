import asyncio
import random
import time
from proto import snakes_pb2 as pb
from net.transport import Transport
from net.dispatcher import Dispatcher
from net.peers import Peers
from game.rules import Engine
from game.place import find_free_5x5
from game.snapshot import to_proto_state

class MasterController:
    def __init__(self, loop, cfg, ui_push_state, player_name="player"):
        self.loop = loop
        self.cfg = cfg
        self.transport = Transport(loop, cfg.state_delay_ms)
        self.dispatch = Dispatcher(cfg.state_delay_ms)
        self.peers = Peers()
        self.engine = Engine(cfg, rng=random.Random())
        self.players = {}
        self.next_player_id = 1
        self.ui_push_state = ui_push_state
        self.pending_steer = {}
        self.master_name = player_name
        self._last_tx = {}

    async def start(self):
        self.transport.on_multicast(lambda *_: None) # Multicast handler + register socket in loop(add_reader)
        self.players[1] = pb.GamePlayer(name=self.master_name, id=1, role=pb.MASTER, score=0)
        pos = find_free_5x5(set(), self.cfg.width, self.cfg.height)
        self.engine.add_snake(1, pos, 0)
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

    def _touch_tx(self, addr):
        self._last_tx[addr] = time.monotonic() # Last transmisison mark

    async def _loop_unicast(self):
        while True:
            data, addr = await self.transport.recv_unicast()
            msg = pb.GameMessage()
            try:
                msg.ParseFromString(data)
            except Exception:
                continue

            if msg.HasField("ack"):
                self.dispatch.ack(addr, msg.msg_seq)
                self.peers.touch(addr)
                continue
            peer = self.peers.touch(addr)

            if msg.HasField("join"):
                pid, ok = self._on_join(addr, msg, peer)
                if not ok:
                    continue
                ack = pb.GameMessage(
                    msg_seq=self.dispatch.next_seq(),
                    sender_id=1,
                    receiver_id=pid,
                    ack=pb.GameMessage.AckMsg(),
                )

                payload = ack.SerializeToString()
                await self.transport.send_unicast(addr, payload)
                self.dispatch.track(addr, ack.msg_seq, payload)
                self._touch_tx(addr)

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
                self._touch_tx(addr)

            elif msg.HasField("steer") and msg.sender_id:
                sid = msg.sender_id
                if sid not in self.engine.snakes or not getattr(self.engine.snakes[sid], "alive", False):
                    continue

                d = msg.steer.direction
                dir_map = {pb.UP: 0, pb.DOWN: 1, pb.LEFT: 2, pb.RIGHT: 3}
                self.pending_steer[sid] = dir_map[d]

                ack = pb.GameMessage(
                    msg_seq=self.dispatch.next_seq(),
                    sender_id=1,
                    receiver_id=sid,
                    ack=pb.GameMessage.AckMsg(),
                )
                payload = ack.SerializeToString()
                await self.transport.send_unicast(addr, payload)
                self.dispatch.track(addr, ack.msg_seq, payload)
                self._touch_tx(addr)

            elif msg.HasField("ping"):
                rid = msg.sender_id or 0
                ack = pb.GameMessage(
                    msg_seq=self.dispatch.next_seq(),
                    sender_id=1,
                    receiver_id=rid,
                    ack=pb.GameMessage.AckMsg(),
                )

                payload = ack.SerializeToString()
                await self.transport.send_unicast(addr, payload)
                self.dispatch.track(addr, ack.msg_seq, payload)
                self._touch_tx(addr)

            elif msg.HasField("role_change"):
                sender = msg.sender_id or 0
                if sender in self.players:
                    self.players.pop(sender, None)

                if addr in self.peers.by_addr:
                    self.peers.by_addr[addr].player_id = None

                ack = pb.GameMessage(
                    msg_seq=self.dispatch.next_seq(),
                    sender_id=1,
                    receiver_id=sender,
                    ack=pb.GameMessage.AckMsg(),
                )

                payload = ack.SerializeToString()
                await self.transport.send_unicast(addr, payload)
                self.dispatch.track(addr, ack.msg_seq, payload)
                self._touch_tx(addr)

            elif msg.HasField("discover"):
                ann = self._build_announcement()
                out = pb.GameMessage(msg_seq=self.dispatch.next_seq(), announcement=ann)

                data2 = out.SerializeToString()
                await self.transport.send_unicast(addr, data2)
                self.dispatch.track(addr, out.msg_seq, data2)
                self._touch_tx(addr)

    def _on_join(self, addr, msg, peer):
        if peer.player_id:
            pid = peer.player_id
            gp = self.players.get(pid)
            alive = pid in self.engine.snakes and getattr(self.engine.snakes[pid], "alive", False)

            if gp is None or gp.role != pb.NORMAL or not alive:
                occupied = {(c.x, c.y) for s in self.engine.snakes.values() for c in s.cells}
                pos = find_free_5x5(occupied, self.cfg.width, self.cfg.height)
                if not pos:
                    err = pb.GameMessage(
                        msg_seq=self.dispatch.next_seq(),
                        error=pb.GameMessage.ErrorMsg(error_message="No 5x5 free area"),
                    )
                    self.loop.create_task(self.transport.send_unicast(addr, err.SerializeToString()))
                    self._touch_tx(addr)
                    return 0, False
                
                self.engine.snakes.pop(pid, None)
                self.engine.scores[pid] = 0

                if gp is None:
                    name = (msg.join.player_name or "player")[:32]
                    self.players[pid] = pb.GamePlayer(name=name, id=pid, role=pb.NORMAL, score=0)
                else:
                    self.players[pid].role = pb.NORMAL
                    self.players[pid].score = 0
    
                self.engine.add_snake(pid, pos, 0)
            return pid, True
        
        occupied = {(c.x, c.y) for s in self.engine.snakes.values() for c in s.cells}
        pos = find_free_5x5(occupied, self.cfg.width, self.cfg.height)
        if not pos:
            err = pb.GameMessage(
                msg_seq=self.dispatch.next_seq(),
                error=pb.GameMessage.ErrorMsg(error_message="No 5x5 free area"),
            )
            self.loop.create_task(self.transport.send_unicast(addr, err.SerializeToString()))
            self._touch_tx(addr)
            return 0, False
        
        pid = self._alloc_player_id()
        peer.player_id = pid
        player_name = (msg.join.player_name or "player")[:32]
        gp = pb.GamePlayer(name=player_name, id=pid, role=pb.NORMAL, score=0)
        self.players[pid] = gp
        self.engine.add_snake(pid, pos, 0)
        return pid, True

    def _alloc_player_id(self):
        pid = self.next_player_id
        self.next_player_id += 1
        return pid

    def _build_announcement(self):
        ann = pb.GameMessage.AnnouncementMsg()
        ga = pb.GameAnnouncement()

        for p in self.players.values():
            ga.players.players.append(p)

        ga.config.width = self.cfg.width
        ga.config.height = self.cfg.height
        ga.config.food_static = self.cfg.food_static
        ga.config.state_delay_ms = self.cfg.state_delay_ms

        _, uni_port = self.transport.unicast_addr()
        ga.can_join = True
        ga.game_name = f"snakenet:{uni_port}"
        ann.games.append(ga)
        return ann

    async def _loop_announce(self):
        while True:
            msg = pb.GameMessage(msg_seq=self.dispatch.next_seq(), announcement=self._build_announcement())
            await self.transport.send_multicast(msg.SerializeToString())
            await asyncio.sleep(1.0)

    async def _loop_tick(self):
        while True:
            for pid, d in list(self.pending_steer.items()):
                self.engine.steer(pid, d)
            self.pending_steer.clear()

            self.engine.step()
            for pid, gp in self.players.items():
                alive = pid in self.engine.snakes and getattr(self.engine.snakes[pid], "alive", False)
                if not alive:
                    self.engine.scores[pid] = 0
                    gp.score = 0

            players_pb = []
            for pid, gp in self.players.items():
                cp = pb.GamePlayer()
                cp.name, cp.id, cp.role = gp.name, gp.id, gp.role
                cp.score = self.engine.scores.get(pid, 0)
                players_pb.append(cp)

            state = to_proto_state(self.engine, players_pb)
            msg = pb.GameMessage(msg_seq=self.dispatch.next_seq(), state=pb.GameMessage.StateMsg(state=state))
            data = msg.SerializeToString()

            if self.ui_push_state:
                self.ui_push_state(state)

            for addr, _peer in list(self.peers.by_addr.items()):
                await self.transport.send_unicast(addr, data)
                self.dispatch.track(addr, msg.msg_seq, data)
                self._touch_tx(addr)
                
            await asyncio.sleep(self.cfg.state_delay_ms / 1000.0)

    async def _loop_retries(self):
        while True:
            for (addr, seq), payload in self.dispatch.due_retries():
                await self.transport.send_unicast(addr, payload)
                self._touch_tx(addr)
            await asyncio.sleep(0.01)

    async def _loop_ping(self):
        while True:
            await asyncio.sleep(self.cfg.state_delay_ms / 1000.0 / 10.0)
            now = time.monotonic()
            ping_interval = (self.cfg.state_delay_ms / 10.0) / 1000.0
            for addr, peer in list(self.peers.by_addr.items()):
                last = self._last_tx.get(addr, 0.0)
                if now - last > ping_interval:
                    ping = pb.GameMessage(
                        msg_seq=self.dispatch.next_seq(),
                        sender_id=1,
                        receiver_id=peer.player_id or 0,
                        ping=pb.GameMessage.PingMsg(),
                    )
                    data_ping = ping.SerializeToString()
                    await self.transport.send_unicast(addr, data_ping)
                    self.dispatch.track(addr, ping.msg_seq, data_ping)
                    self._touch_tx(addr)

    async def steer_local(self, direction_pb):
        dir_map = {pb.UP: 0, pb.DOWN: 1, pb.LEFT: 2, pb.RIGHT: 3}
        self.pending_steer[1] = dir_map[direction_pb]

    async def respawn_self(self):
        pid = 1
        self.engine.snakes.pop(pid, None)
        self.engine.scores.pop(pid, None)
        occupied = {(c.x, c.y) for s in self.engine.snakes.values() for c in s.cells}
        pos = find_free_5x5(occupied, self.cfg.width, self.cfg.height) or (self.cfg.width // 2, self.cfg.height // 2)
        self.engine.add_snake(pid, pos, 0)
