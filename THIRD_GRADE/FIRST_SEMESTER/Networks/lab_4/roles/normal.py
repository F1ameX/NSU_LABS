import asyncio
import time
from proto import snakes_pb2 as pb
from net.transport import Transport
from net.dispatcher import Dispatcher
from net.peers import Peers

class NormalController:
    def __init__(self, loop, cfg, ui_push_state, ui_set_games):
        self.loop = loop
        self.cfg = cfg
        self.transport = Transport(loop, cfg.state_delay_ms)
        self.dispatch = Dispatcher(cfg.state_delay_ms)
        self.peers = Peers()
        self.player_id = None
        self.center = None
        self.joining = False
        self.master_id = None
        self.deputy_id = None
        self.deputy_addr = None
        self.lost_master = False
        self.await_unicast = True
        self.ui_push_state = ui_push_state
        self.ui_set_games = ui_set_games
        self.games_map = {}
        self.games_ts = {}
        self.games = []
        self._last_unicast = time.monotonic()
        self._last_tx = {}
        self.current_game = None
        self._await_rc_seq = None
        self._respawn_name = None

    async def start(self):
        self.transport.on_multicast(self._on_mc)
        self.tasks = [
            self.loop.create_task(self._loop_unicast()),
            self.loop.create_task(self._loop_retries_and_ping()),
            self.loop.create_task(self._loop_timeout()),
            self.loop.create_task(self._loop_games_gc()),
        ]

    async def stop(self):
        for t in getattr(self, "tasks", []):
            t.cancel()
        self.transport.close()

    def _touch_tx(self, addr):
        self._last_tx[addr] = time.monotonic()

    def _on_mc(self, data, addr):
        msg = pb.GameMessage()
        try:
            msg.ParseFromString(data)
        except Exception:
            return
        
        if msg.HasField("announcement") and msg.announcement.games:
            g = msg.announcement.games[0]
            name = g.game_name or "snakenet"
            fixed_addr = (addr[0], addr[1])
            self.games_map[fixed_addr] = name
            self.games_ts[fixed_addr] = time.monotonic()
            self.games = [(nm, ad) for ad, nm in sorted(self.games_map.items(), key=lambda x: (x[0][0], x[0][1]))]
            if self.ui_set_games:
                self.ui_set_games(self.games)

    async def _loop_unicast(self):
        while True:
            data, addr = await self.transport.recv_unicast()
            self._last_unicast = time.monotonic()
            self.await_unicast = False

            if self.center != addr:
                self.center = addr
                self.peers.set_center(addr)
            msg = pb.GameMessage()
            try:
                msg.ParseFromString(data)
            except Exception:
                continue

            if msg.HasField("ack"):
                self.dispatch.ack(addr, msg.msg_seq)
                if self._await_rc_seq is not None and msg.msg_seq == self._await_rc_seq:
                    self._await_rc_seq = None
                    name = self._respawn_name or "player"
                    self._respawn_name = None

                    if self.current_game and self.center:
                        game_name, center_addr = self.current_game
                        self.loop.create_task(self._send_join_to(game_name, center_addr, name))
                    continue

                if msg.receiver_id and self.joining and not self.player_id:
                    self.player_id = msg.receiver_id
                    self.joining = False
                continue

            need_ack = False
            if msg.HasField("state"):
                if self.ui_push_state:
                    self.ui_push_state(msg.state.state)
                try:
                    pls = msg.state.state.players.players
                    for gp in pls:
                        if gp.role == pb.MASTER:
                            self.master_id = gp.id
                        elif gp.role == pb.DEPUTY:
                            self.deputy_id = gp.id
                            if getattr(gp, "ip_address", None) and getattr(gp, "port", 0):
                                self.deputy_addr = (gp.ip_address, gp.port)
                except Exception:
                    pass
                need_ack = True

            elif msg.HasField("ping"):
                need_ack = True

            elif msg.HasField("role_change"):
                need_ack = True

            elif msg.HasField("error"):
                need_ack = True

            if need_ack and self.center:
                rid = msg.sender_id if msg.sender_id is not None else (self.master_id or 0)
                ack = pb.GameMessage(
                    msg_seq=self.dispatch.next_seq(),
                    sender_id=self.player_id or 0,
                    receiver_id=rid,
                    ack=pb.GameMessage.AckMsg(),
                )

                data_ack = ack.SerializeToString()
                await self.transport.send_unicast(self.center, data_ack)
                self.dispatch.track(self.center, ack.msg_seq, data_ack)
                self._touch_tx(self.center)

    async def _send_join_to(self, game_name, addr, player_name):
        self.center = addr
        self.await_unicast = True
        self._last_unicast = time.monotonic()
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
        self._touch_tx(addr)
        self.joining = True

    async def join(self, game_idx, player_name):
        self.lost_master = False
        if self.player_id is not None or self.joining:
            return
        if not (0 <= game_idx < len(self.games)):
            return
        game_name, addr = self.games[game_idx]
        self.current_game = (game_name, addr)
        await self._send_join_to(game_name, addr, player_name)

    async def steer(self, direction_pb):
        if not self.center or self.player_id is None:
            return
        steer = pb.GameMessage.SteerMsg(direction=direction_pb)
        msg = pb.GameMessage(
            msg_seq=self.dispatch.next_seq(),
            sender_id=self.player_id,
            steer=steer,
        )
        data = msg.SerializeToString()
        await self.transport.send_unicast(self.center, data)
        self.dispatch.track(self.center, msg.msg_seq, data)
        self._touch_tx(self.center)

    async def leave_and_respawn(self, game_idx, player_name):
        if not self.center or self.joining:
            return
        if self.current_game is None:
            if 0 <= game_idx < len(self.games):
                self.current_game = self.games[game_idx]
            else:
                return
            
        rc = pb.GameMessage.RoleChangeMsg(sender_role=pb.VIEWER)
        seq = self.dispatch.next_seq()
        msg = pb.GameMessage(
            msg_seq=seq,
            sender_id=self.player_id or 0,
            receiver_id=self.master_id or 0,
            role_change=rc
        )

        data = msg.SerializeToString()
        await self.transport.send_unicast(self.center, data)
        self.dispatch.track(self.center, seq, data)
        self._touch_tx(self.center)
        self._await_rc_seq = seq
        self._respawn_name = player_name
        self.player_id = None

    async def leave(self):
        if not self.center:
            return
        rc = pb.GameMessage.RoleChangeMsg(sender_role=pb.VIEWER)
        msg = pb.GameMessage(
            msg_seq=self.dispatch.next_seq(),
            sender_id=self.player_id or 0,
            receiver_id=self.master_id or 0,
            role_change=rc
        )

        data = msg.SerializeToString()
        await self.transport.send_unicast(self.center, data)
        self.dispatch.track(self.center, msg.msg_seq, data)
        self._touch_tx(self.center)
        self.player_id = None
        self.joining = False

    async def _loop_retries_and_ping(self):
        while True:
            for (addr, seq), payload in self.dispatch.due_retries():
                await self.transport.send_unicast(addr, payload)
                self._touch_tx(addr)
                
            if self.center:
                last = self._last_tx.get(self.center, 0.0)
                ping_interval = (self.cfg.state_delay_ms / 10.0) / 1000.0
                if time.monotonic() - last > ping_interval:
                    ping = pb.GameMessage(
                        msg_seq=self.dispatch.next_seq(),
                        sender_id=self.player_id or 0,
                        receiver_id=self.master_id or 0,
                        ping=pb.GameMessage.PingMsg(),
                    )
                    
                    data_ping = ping.SerializeToString()
                    await self.transport.send_unicast(self.center, data_ping)
                    self.dispatch.track(self.center, ping.msg_seq, data_ping)
                    self._touch_tx(self.center)
            await asyncio.sleep(0.01)

    async def _loop_timeout(self):
        while True:
            if self.center and not self.await_unicast:
                if time.monotonic() - self._last_unicast > 0.8 * (self.cfg.state_delay_ms / 1000.0):
                    if self.deputy_addr and self.center != self.deputy_addr:
                        self.center = self.deputy_addr
                        self._last_unicast = time.monotonic()
                    else:
                        self.lost_master = True
            await asyncio.sleep(0.05)

    async def _loop_games_gc(self):
        while True:
            now = time.monotonic()
            to_del = []
            for addr, ts in list(self.games_ts.items()):
                if now - ts > 3.2:
                    to_del.append(addr)
            if to_del:
                for addr in to_del:
                    self.games_ts.pop(addr, None)
                    self.games_map.pop(addr, None)
                self.games = [(nm, ad) for ad, nm in sorted(self.games_map.items(), key=lambda x: (x[0][0], x[0][1]))]
                if self.ui_set_games:
                    self.ui_set_games(self.games)
            await asyncio.sleep(0.5)
