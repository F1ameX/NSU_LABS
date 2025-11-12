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

_dir_map_pb2eng = {pb.UP: 0, pb.DOWN: 1, pb.LEFT: 2, pb.RIGHT: 3}

class MasterController:
    def __init__(self, loop, cfg, ui_push_state, player_name="player",
                 bootstrap_state=None, bind_port=None, actual_master_id=None):
        self.loop = loop
        self.cfg = cfg
        self.transport = Transport(loop, cfg.state_delay_ms, getattr(cfg, "mcast_iface_ip", None), bind_port)
        self.dispatch = Dispatcher(cfg.state_delay_ms)
        self.peers = Peers()
        self.engine = Engine(cfg, rng=random.Random())
        self.players = {}
        self.next_player_id = 1
        self.ui_push_state = ui_push_state
        self.pending_steer = {}
        self.master_name = player_name
        self._last_tx = {}
        self._last_rx = {}
        self.deputy_id = None
        self.join_order = []
        self._bootstrap_state = bootstrap_state
        self.actual_master_id = actual_master_id or 1


    async def start(self):
        self.transport.on_multicast(lambda *_: None)
        try:
            if self._bootstrap_state:
                self._init_from_bootstrap(self._bootstrap_state)
            else:
                self.players[1] = pb.GamePlayer(name=self.master_name, id=1, role=pb.MASTER, score=0)
                pos = find_free_5x5(set(), self.cfg.width, self.cfg.height) or (self.cfg.width // 2, self.cfg.height // 2)
                self.engine.add_snake(1, pos, 0)
                self.next_player_id = 2
                self.actual_master_id = 1

            self.tasks = [
                self.loop.create_task(self._loop_unicast()),
                self.loop.create_task(self._loop_tick()),
                self.loop.create_task(self._loop_announce()),
                self.loop.create_task(self._loop_retries()),
                self.loop.create_task(self._loop_ping()),
                self.loop.create_task(self._loop_peers_timeout()),
            ]
            await self._announce_new_master()
            await self._push_immediate_state()
            
        except Exception:
            for t in getattr(self, "tasks", []):
                try:
                    t.cancel()
                except Exception:
                    pass
            self.tasks = []
            try:
                self.transport.close()
            except Exception:
                pass
            raise

    async def stop(self):
        tasks = list(getattr(self, "tasks", []))
        for t in tasks:
            t.cancel()
        try:
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            self.transport.close()

    def _touch_tx(self, addr): self._last_tx[addr] = time.monotonic()
    def _touch_rx(self, addr): self._last_rx[addr] = time.monotonic()

    def _addr_for_pid(self, pid):
        for addr, peer in self.peers.by_addr.items():
            if peer.player_id == pid:
                return addr
        return None

    def _seed_peers_from_state(self, st):
        try:
            for gp in st.players.players:
                if getattr(gp, "ip_address", None) and getattr(gp, "port", 0):
                    addr = (gp.ip_address, gp.port)
                    peer = self.peers.touch(addr)
                    peer.player_id = gp.id
        except Exception:
            pass

    def _decode_points_to_cells(self, points):
        cells = []
        if not points:
            return cells
        w, h = self.cfg.width, self.cfg.height
        x = points[0].x
        y = points[0].y
        cells.append((x, y))
        for i in range(1, len(points)):
            x = (x + points[i].x) % w
            y = (y + points[i].y) % h
            cells.append((x, y))
        return cells

    def _init_from_bootstrap(self, st):
        self.players.clear()
        self.engine = Engine(self.cfg, rng=random.Random())

        def _iter_snakes(state):
            snakes_field = getattr(state, "snakes", None)
            if snakes_field is None:
                return []
            try:
                return list(snakes_field.snakes)
            except AttributeError:
                return list(snakes_field)

        def _iter_foods(state):
            foods_field = getattr(state, "foods", None)
            if foods_field is None:
                return []
            try:
                return list(foods_field.foods)
            except AttributeError:
                return list(foods_field)

        master_id_old = None
        order = []
        for gp in st.players.players:
            if gp.role == pb.MASTER:
                master_id_old = gp.id
            if gp.role in (pb.MASTER, pb.NORMAL, pb.DEPUTY, pb.VIEWER):
                self.players[gp.id] = pb.GamePlayer(
                    name=getattr(gp, "name", "player"),
                    id=gp.id,
                    role=gp.role,
                    score=getattr(gp, "score", 0)
                )
                order.append(gp.id)

        for sn in _iter_snakes(st):
            pid = sn.player_id
            pts = list(getattr(sn, "points", []))
            cells_abs = self._decode_points_to_cells(pts)
            if not cells_abs:
                continue
            head = cells_abs[0]
            d = _dir_map_pb2eng.get(getattr(sn, "head_direction", pb.UP), 0)
            self.engine.add_snake(pid, head, d)
            s = self.engine.snakes.get(pid)
            if s and cells_abs:
                CellT = type(s.cells[0])
                s.cells = [CellT(x=px, y=py) for (px, py) in cells_abs]
                s.dir = d
                s.alive = True
            self.engine.scores[pid] = getattr(self.players.get(pid, None), "score", 0)

        foods = _iter_foods(st)
        if foods:
            self.engine.food = {(f.x, f.y) for f in foods}

        self._seed_peers_from_state(st)

        self.next_player_id = max(self.players.keys(), default=self.actual_master_id) + 1

        if self.actual_master_id in self.players:
            self.players[self.actual_master_id].role = pb.MASTER
        if master_id_old is not None and master_id_old in self.players and master_id_old != self.actual_master_id:
            self.players[master_id_old].role = pb.VIEWER

        self.join_order = [
            pid for pid in order
            if pid != self.actual_master_id
            and self.players.get(pid, None)
            and self.players[pid].role == pb.NORMAL
        ]
        self._choose_and_set_deputy()

        try:
            self.engine.state_order = max(getattr(st, "state_order", 0), 0)
        except Exception:
            pass

    async def _announce_new_master(self):
        for addr, peer in list(self.peers.by_addr.items()):
            rid = peer.player_id or 0
            rc = pb.GameMessage.RoleChangeMsg(sender_role=pb.MASTER)
            msg = pb.GameMessage(
                msg_seq=self.dispatch.next_seq(),
                sender_id=self.actual_master_id,
                receiver_id=rid,
                role_change=rc
            )
            data = msg.SerializeToString()
            await self.transport.send_unicast(addr, data)
            self.dispatch.track(addr, msg.msg_seq, data)
            self._touch_tx(addr)

    async def _push_immediate_state(self):
        players_pb = []
        for pid, gp in self.players.items():
            if gp.role == pb.VIEWER:
                continue
            cp = pb.GamePlayer()
            cp.name, cp.id, cp.role = gp.name, gp.id, gp.role
            cp.score = self.engine.scores.get(pid, gp.score)
            a = self._addr_for_pid(pid)
            if a:
                cp.ip_address, cp.port = a[0], a[1]
            if self.deputy_id is not None and pid == self.deputy_id and cp.role == pb.NORMAL:
                cp.role = pb.DEPUTY
            players_pb.append(cp)

        state = to_proto_state(self.engine, players_pb)
        msg = pb.GameMessage(msg_seq=self.dispatch.next_seq(), state=pb.GameMessage.StateMsg(state=state))
        data = msg.SerializeToString()
        for addr, _peer in list(self.peers.by_addr.items()):
            await self.transport.send_unicast(addr, data)
            self.dispatch.track(addr, msg.msg_seq, data)
            self._touch_tx(addr)
        if self.ui_push_state:
            self.ui_push_state(state)

    def _prune_join_order(self):
        cleaned = []
        for pid in self.join_order:
            gp = self.players.get(pid)
            if gp and gp.role == pb.NORMAL and pid != self.actual_master_id:
                cleaned.append(pid)
        self.join_order = cleaned

    def _choose_and_set_deputy(self):
        self._prune_join_order()
        cand = None
        for pid in self.join_order:
            if pid in self.players and self.players[pid].role == pb.NORMAL and pid != self.actual_master_id:
                cand = pid
                break
        if cand is None:
            self.deputy_id = None
            return
        if self.deputy_id == cand:
            return
        self.deputy_id = cand
        addr = self._addr_for_pid(cand)
        if addr:
            rc = pb.GameMessage.RoleChangeMsg(sender_role=pb.MASTER, receiver_role=pb.DEPUTY)
            msg = pb.GameMessage(
                msg_seq=self.dispatch.next_seq(),
                sender_id=self.actual_master_id,
                receiver_id=cand,
                role_change=rc
            )
            data = msg.SerializeToString()
            self.loop.create_task(self.transport.send_unicast(addr, data))
            self.dispatch.track(addr, msg.msg_seq, data)
            self._touch_tx(addr)

    async def _loop_unicast(self):
        while True:
            data, addr = await self.transport.recv_unicast()
            self._touch_rx(addr)
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
                if not peer.player_id:
                    guessed = msg.sender_id or 0
                    if guessed and guessed in self.players:
                        pid = guessed
                        peer.player_id = pid
                        gp = self.players[pid]
                        name_now = (msg.join.player_name or gp.name or "player")[:32]
                        alive = pid in self.engine.snakes and getattr(self.engine.snakes[pid], "alive", False)
                        if not alive:
                            occupied = {(c.x, c.y) for s in self.engine.snakes.values() for c in s.cells}
                            pos = find_free_5x5(occupied, self.cfg.width, self.cfg.height)
                            if not pos:
                                err = pb.GameMessage(
                                    msg_seq=self.dispatch.next_seq(),
                                    error=pb.GameMessage.ErrorMsg(error_message="No 5x5 free area"),
                                )
                                self.loop.create_task(self.transport.send_unicast(addr, err.SerializeToString()))
                                self._touch_tx(addr)
                                continue
                            self.engine.snakes.pop(pid, None)
                            self.engine.scores[pid] = 0
                            self.engine.add_snake(pid, pos, 0)
                        gp.role = pb.NORMAL
                        gp.name = name_now
                        if pid not in self.join_order:
                            self.join_order.append(pid)
                        self._choose_and_set_deputy()

                        ack = pb.GameMessage(
                            msg_seq=self.dispatch.next_seq(),
                            sender_id=self.actual_master_id,
                            receiver_id=pid,
                            ack=pb.GameMessage.AckMsg(),
                        )
                        payload = ack.SerializeToString()
                        await self.transport.send_unicast(addr, payload)
                        self.dispatch.track(addr, ack.msg_seq, payload)
                        self._touch_tx(addr)
                        await self._push_immediate_state_to(addr)
                        continue

                pid, ok = self._on_join(addr, msg, peer)
                if not ok:
                    continue
                ack = pb.GameMessage(
                    msg_seq=self.dispatch.next_seq(),
                    sender_id=self.actual_master_id,
                    receiver_id=pid,
                    ack=pb.GameMessage.AckMsg(),
                )
                payload = ack.SerializeToString()
                await self.transport.send_unicast(addr, payload)
                self.dispatch.track(addr, ack.msg_seq, payload)
                self._touch_tx(addr)
                await self._push_immediate_state_to(addr)

            elif msg.HasField("steer") and msg.sender_id:
                sid = msg.sender_id
                if sid not in self.engine.snakes or not getattr(self.engine.snakes[sid], "alive", False):
                    continue
                d = msg.steer.direction
                self.pending_steer[sid] = _dir_map_pb2eng[d]
                ack = pb.GameMessage(
                    msg_seq=self.dispatch.next_seq(),
                    sender_id=self.actual_master_id,
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
                    sender_id=self.actual_master_id,
                    receiver_id=rid,
                    ack=pb.GameMessage.AckMsg(),
                )
                payload = ack.SerializeToString()
                await self.transport.send_unicast(addr, payload)
                self.dispatch.track(addr, msg.msg_seq, payload)
                self._touch_tx(addr)

            elif msg.HasField("role_change"):
                sender = msg.sender_id or 0
                if sender in self.players:
                    self.players[sender].role = pb.VIEWER

                self.pending_steer.pop(sender, None)
                if sender in self.engine.snakes:
                    self.engine.snakes.pop(sender, None)
                self.engine.scores.pop(sender, None)

                if addr in self.peers.by_addr:
                    self.peers.by_addr[addr].player_id = sender
                self._prune_join_order()
                if self.deputy_id == sender:
                    self.deputy_id = None
                    self._choose_and_set_deputy()

                ack = pb.GameMessage(
                    msg_seq=self.dispatch.next_seq(),
                    sender_id=self.actual_master_id,
                    receiver_id=sender,
                    ack=pb.GameMessage.AckMsg(),
                )
                payload = ack.SerializeToString()
                await self.transport.send_unicast(addr, payload)
                self.dispatch.track(addr, ack.msg_seq, payload)
                self._touch_tx(addr)

                await self._push_immediate_state()

            elif msg.HasField("discover"):
                ann = self._build_announcement()
                out = pb.GameMessage(msg_seq=self.dispatch.next_seq(), announcement=ann)
                data2 = out.SerializeToString()
                await self.transport.send_unicast(addr, data2)
                self.dispatch.track(addr, out.msg_seq, data2)
                self._touch_tx(addr)

    async def _push_immediate_state_to(self, addr):
        players_pb = []
        for pid, gp in self.players.items():
            if gp.role == pb.VIEWER:
                continue
            cp = pb.GamePlayer()
            cp.name, cp.id, cp.role = gp.name, gp.id, gp.role
            cp.score = self.engine.scores.get(pid, gp.score)
            a = self._addr_for_pid(pid)
            if a:
                cp.ip_address, cp.port = a[0], a[1]
            if self.deputy_id is not None and pid == self.deputy_id and cp.role == pb.NORMAL:
                cp.role = pb.DEPUTY
            players_pb.append(cp)
        state = to_proto_state(self.engine, players_pb)
        st_msg = pb.GameMessage(msg_seq=self.dispatch.next_seq(), state=pb.GameMessage.StateMsg(state=state))
        data_state = st_msg.SerializeToString()
        await self.transport.send_unicast(addr, data_state)
        self.dispatch.track(addr, st_msg.msg_seq, data_state)
        self._touch_tx(addr)
        if self.ui_push_state:
            self.ui_push_state(state)

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
                name_now = (msg.join.player_name or "player")[:32]
                if gp is None:
                    self.players[pid] = pb.GamePlayer(name=name_now, id=pid, role=pb.NORMAL, score=0)
                else:
                    self.players[pid].role = pb.NORMAL
                    self.players[pid].score = 0
                    self.players[pid].name = name_now
                self.engine.add_snake(pid, pos, 0)
            if pid not in self.join_order:
                self.join_order.append(pid)
            self._choose_and_set_deputy()
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
        if pid not in self.join_order:
            self.join_order.append(pid)
        self._choose_and_set_deputy()
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
        ga.game_name = f"O_TT_A_p_bI_III_bI:{uni_port}"
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
                if not alive and gp.role != pb.VIEWER:
                    self.engine.scores[pid] = 0
                    gp.score = 0

            players_pb = []
            for pid, gp in self.players.items():
                if gp.role == pb.VIEWER:
                    continue
                cp = pb.GamePlayer()
                cp.name, cp.id, cp.role = gp.name, gp.id, gp.role
                cp.score = self.engine.scores.get(pid, gp.score)
                a = self._addr_for_pid(pid)
                if a:
                    cp.ip_address, cp.port = a[0], a[1]
                if self.deputy_id is not None and pid == self.deputy_id and cp.role == pb.NORMAL:
                    cp.role = pb.DEPUTY
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
            ping_interval = 0.3
            for addr, peer in list(self.peers.by_addr.items()):
                last = self._last_tx.get(addr, 0.0)
                if now - last > ping_interval:
                    ping = pb.GameMessage(
                        msg_seq=self.dispatch.next_seq(),
                        sender_id=self.actual_master_id,
                        receiver_id=peer.player_id or 0,
                        ping=pb.GameMessage.PingMsg(),
                    )
                    data_ping = ping.SerializeToString()
                    await self.transport.send_unicast(addr, data_ping)
                    self.dispatch.track(addr, ping.msg_seq, data_ping)
                    self._touch_tx(addr)

    async def _loop_peers_timeout(self):
        while True:
            await asyncio.sleep(0.05)
            now = time.monotonic()
            thr = 3.0
            to_drop = []
            for addr, peer in list(self.peers.by_addr.items()):
                last_rx = self._last_rx.get(addr, 0.0)
                if now - last_rx > thr:
                    to_drop.append((addr, peer.player_id or 0))
            for addr, pid in to_drop:
                if pid in self.players and self.players[pid].role != pb.VIEWER:
                    self.players[pid].role = pb.VIEWER
                if pid in self.engine.snakes:
                    try:
                        self.engine.snakes[pid].state = "ZOMBIE"
                        self.engine.snakes[pid].alive = True
                    except Exception:
                        pass
                self.engine.scores.pop(pid, None)

                self.peers.by_addr.pop(addr, None)
                self._last_tx.pop(addr, None)
                self._last_rx.pop(addr, None)
                if pid in self.join_order:
                    self.join_order = [p for p in self.join_order if p != pid]
                if self.deputy_id == pid:
                    self.deputy_id = None
                    self._choose_and_set_deputy()

    async def steer_local(self, direction_pb):
        self.pending_steer[self.actual_master_id] = _dir_map_pb2eng[direction_pb]

    async def respawn_self(self):
        pid = self.actual_master_id
        self.engine.snakes.pop(pid, None)
        self.engine.scores.pop(pid, None)
        occupied = {(c.x, c.y) for s in self.engine.snakes.values() for c in s.cells}
        pos = find_free_5x5(occupied, self.cfg.width, self.cfg.height) or (self.cfg.width // 2, self.cfg.height // 2)
        self.engine.add_snake(pid, pos, 0)
