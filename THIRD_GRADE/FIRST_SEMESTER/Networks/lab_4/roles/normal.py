import asyncio
import time
from proto import snakes_pb2 as pb
from net.transport import Transport
from net.dispatcher import Dispatcher
from net.peers import Peers

IGNORE_TTL = 10.0          
HANDOVER_GRACE = 10.0       
DEPUTY_FAST_THR = 0.45      
NO_DEPUTY_GRACE = 12.0      
HANDOVER_FALLBACK_PAD = 2.0 

class NormalController:
    def __init__(self, loop, cfg, ui_push_state, ui_set_games, ui_error=None, ui_promote=None):
        self.loop = loop
        self.cfg = cfg
        self.transport = Transport(loop, cfg.state_delay_ms, getattr(cfg, "mcast_iface_ip", None))
        self.dispatch = Dispatcher(cfg.state_delay_ms)
        self.peers = Peers()

        self.ui_push_state = ui_push_state
        self.ui_set_games = ui_set_games
        self.ui_error = ui_error
        self.ui_promote = ui_promote

        self.player_id = None
        self.center = None
        self.master_addr = None
        self.deputy_addr = None
        self.pending_join_addr = None
        self.joining = False
        self.master_id = None
        self.deputy_id = None
        self.await_unicast = True

        self._last_unicast = time.monotonic()
        self._last_tx = {}
        self._last_state_order = -1
        self._last_state = None

        self.games_map = {}
        self.games_ts = {}
        self.games = []
        self.current_game = None

        self._await_rc_seq = None
        self._respawn_name = None
        self._join_deadline = None
        self._respawn_failsafe_at = None

        self.lost_master = False
        self._lost_since = None
        self.ignore_unicast_until = {}

        self.tasks = []
        self._promoted_master = None
        self._promoting = False

        self._handover_until = None
        self._handover_fallback_at = None
        self._announce_seen_at = 0.0
        self._auto_rebind_tried = set()

        self._timeout_thr = 1.5

    async def start(self):
        self.transport.on_multicast(self._on_mc)
        if self.ui_set_games:
            self.ui_set_games([])

        self.tasks = [
            self.loop.create_task(self._loop_unicast()),
            self.loop.create_task(self._loop_retries_and_ping()),
            self.loop.create_task(self._loop_timeout()),
            self.loop.create_task(self._loop_games_gc()),
            self.loop.create_task(self._loop_join_watchdog()),
        ]

    async def stop(self):
        tasks = list(self.tasks)
        for t in tasks:
            t.cancel()
        try:
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            self.tasks.clear()
            try:
                self.transport.close()
            except Exception:
                pass

    def _touch_tx(self, addr):
        self._last_tx[addr] = time.monotonic()

    def _my_name(self) -> str:
        name = "player"
        try:
            if self._last_state and self.player_id is not None:
                for gp in self._last_state.players.players:
                    if gp.id == self.player_id and getattr(gp, "name", None):
                        return gp.name
        except Exception:
            pass
        return name

    def _on_mc(self, data, addr):
        msg = pb.GameMessage()
        try:
            msg.ParseFromString(data)
        except Exception:
            return

        if msg.HasField("announcement") and msg.announcement.games:
            g = msg.announcement.games[0]
            name = g.game_name or "o_TT_A_p_bI_III_bI"
            fixed_addr = (addr[0], addr[1])
            self.games_map[fixed_addr] = name
            self.games_ts[fixed_addr] = time.monotonic()
            self.games = [(nm, ad) for ad, nm in sorted(self.games_map.items(), key=lambda x: (x[0][0], x[0][1]))]
            if self.ui_set_games:
                self.ui_set_games(self.games)

            self._announce_seen_at = time.monotonic()

            if (self._handover_until or self.lost_master) and self.current_game and not self.joining:
                if fixed_addr not in self._auto_rebind_tried:
                    self._auto_rebind_tried.add(fixed_addr)
                    self._adopt_center(fixed_addr)
                    self.loop.create_task(self._poke_new_master(fixed_addr))
                    try:
                        pname = self._my_name()
                        self.loop.create_task(self._send_join_to(name, fixed_addr, pname))
                    except Exception:
                        pass

    def _purge_ignored(self):
        now = time.monotonic()
        stale = [a for a, until in self.ignore_unicast_until.items() if until <= now]
        for a in stale:
            self.ignore_unicast_until.pop(a, None)

    def _adopt_center(self, addr2):
        if self.center != addr2:
            self.center = addr2
            self.master_addr = addr2
            self.peers.set_center(addr2)

    async def _promote_to_master(self):
        if self._promoting:
            return
        self._promoting = True

        try:
            local_port = self.transport.unicast_addr()[1]
        except Exception:
            local_port = None
        try:
            self.transport.close()
        except Exception:
            pass

        pname = self._my_name()

        try:
            self.ui_promote(self._last_state, local_port, pname, self.player_id or 1)
        except Exception:
            pass

    def _end_handover(self):
        self._handover_until = None
        self._handover_fallback_at = None

    async def _poke_new_master(self, addr):
        if not addr:
            return
        try:
            discover = pb.GameMessage(discover=pb.GameMessage.DiscoverMsg())
            await self.transport.send_unicast(addr, discover.SerializeToString())
        except Exception:
            pass
        try:
            ping = pb.GameMessage(
                msg_seq=self.dispatch.next_seq(),
                sender_id=self.player_id or 0,
                receiver_id=self.master_id or 0,
                ping=pb.GameMessage.PingMsg(),
            )
            data = ping.SerializeToString()
            await self.transport.send_unicast(addr, data)
            self.dispatch.track(addr, ping.msg_seq, data)
            self._touch_tx(addr)
        except Exception:
            pass

    async def _loop_unicast(self):
        while True:
            try:
                data, addr = await self.transport.recv_unicast()
            except (OSError, RuntimeError, asyncio.CancelledError):
                return
            addr2 = (addr[0], addr[1])

            msg = pb.GameMessage()
            try:
                msg.ParseFromString(data)
            except Exception:
                continue

            self._purge_ignored()
            until = self.ignore_unicast_until.get(addr2)
            if until is not None:
                continue

            if msg.HasField("ack"):
                self.dispatch.ack(addr2, msg.msg_seq)
                self._adopt_center(addr2)
                self._end_handover()

                if self.joining:
                    if msg.receiver_id:
                        if (self.player_id is None) or (self.player_id != msg.receiver_id):
                            self.player_id = msg.receiver_id
                    self.joining = False
                    self._join_deadline = None
                    self.pending_join_addr = None
                    self.ignore_unicast_until.pop(addr2, None)

                if self._await_rc_seq is not None and msg.msg_seq == self._await_rc_seq:
                    self._await_rc_seq = None
                    self._respawn_failsafe_at = None
                    name = self._respawn_name or self._my_name()
                    self._respawn_name = None
                    if self.current_game:
                        game_name, _ = self.current_game
                        self.loop.create_task(self._send_join_to(game_name, addr2, name))

                self._last_unicast = time.monotonic()
                self.await_unicast = False
                self._lost_since = None
                self.lost_master = False
                continue

            if self.center is None or addr2 != self.center:
                self._adopt_center(addr2)

            need_ack = False

            if msg.HasField("state"):
                st = msg.state.state

                self._adopt_center(addr2)
                self._end_handover()

                if self.joining:
                    self.joining = False
                    self._join_deadline = None
                    self.pending_join_addr = None
                    if self.player_id is None:
                        try:
                            my_ip, my_port = self.transport.unicast_addr()
                            for gp in st.players.players:
                                if getattr(gp, "ip_address", None) == my_ip and getattr(gp, "port", 0) == my_port:
                                    self.player_id = gp.id
                                    break
                        except Exception:
                            pass

                if st.state_order > self._last_state_order:
                    self._last_state_order = st.state_order
                    self._last_state = st
                    if self.ui_push_state:
                        self.ui_push_state(st)
                need_ack = True

                try:
                    m_id = None
                    d_id = None
                    m_addr = None
                    d_addr = None
                    for gp in st.players.players:
                        if gp.role == pb.MASTER:
                            m_id = gp.id
                            if getattr(gp, "ip_address", None) and getattr(gp, "port", 0):
                                m_addr = (gp.ip_address, gp.port)
                        elif gp.role == pb.DEPUTY:
                            d_id = gp.id
                            if getattr(gp, "ip_address", None) and getattr(gp, "port", 0):
                                d_addr = (gp.ip_address, gp.port)
                    if m_id is not None:
                        self.master_id = m_id
                    if d_id is not None:
                        self.deputy_id = d_id
                    if d_addr is not None:
                        self.deputy_addr = d_addr
                    if m_addr is not None and self.center != m_addr:
                        self._adopt_center(m_addr)
                except Exception:
                    pass

                self._last_unicast = time.monotonic()
                self.await_unicast = False
                self._lost_since = None
                self.lost_master = False

            elif msg.HasField("ping"):
                need_ack = True
                self._adopt_center(addr2)
                self._end_handover()
                self._last_unicast = time.monotonic()
                self.await_unicast = False
                self._lost_since = None
                self.lost_master = False

            elif msg.HasField("role_change"):
                need_ack = True
                try:
                    if (
                        msg.role_change.receiver_role == pb.MASTER
                        and (self.player_id is not None)
                        and (msg.receiver_id == self.player_id)
                    ):
                        await self._promote_to_master()
                        return
                except Exception:
                    pass
                self._adopt_center(addr2)
                self._end_handover()
                self._last_unicast = time.monotonic()
                self.await_unicast = False
                self._lost_since = None
                self.lost_master = False

            elif msg.HasField("error"):
                need_ack = True
                if self.ui_error:
                    try:
                        self.ui_error(msg.error.error_message or "Error")
                    except Exception:
                        pass
                self._adopt_center(addr2)
                self._end_handover()
                self._last_unicast = time.monotonic()
                self.await_unicast = False
                self._lost_since = None
                self.lost_master = False

            if need_ack:
                rid = msg.sender_id if msg.sender_id is not None else (self.master_id or 0)
                dest = addr2
                try:
                    ack = pb.GameMessage(
                        msg_seq=self.dispatch.next_seq(),
                        sender_id=self.player_id or 0,
                        receiver_id=rid,
                        ack=pb.GameMessage.AckMsg(),
                    )
                    data_ack = ack.SerializeToString()
                    await self.transport.send_unicast(dest, data_ack)
                    self.dispatch.track(dest, ack.msg_seq, data_ack)
                    self._touch_tx(dest)
                except (OSError, RuntimeError, asyncio.CancelledError):
                    return

    async def _send_join_to(self, game_name, addr, player_name):
        addr2 = (addr[0], addr[1])
        self._adopt_center(addr2)
        self.pending_join_addr = addr2
        self.await_unicast = True
        the_time = time.monotonic()
        self._last_unicast = the_time
        self._lost_since = None
        self.ignore_unicast_until.pop(addr2, None)

        join = pb.GameMessage.JoinMsg(
            player_type=pb.HUMAN,
            player_name=player_name,
            game_name=game_name if isinstance(game_name, str) else (self.current_game[0] if self.current_game else "O_TT_A_p_bI_III_bI"),
            requested_role=pb.NORMAL,
        )
        seq = self.dispatch.next_seq()
        msg = pb.GameMessage(msg_seq=seq, sender_id=(self.player_id or 0), join=join)
        data = msg.SerializeToString()
        try:
            await self.transport.send_unicast(addr2, data)
            self.dispatch.track(addr2, seq, data)
            self._touch_tx(addr2)
        except (OSError, RuntimeError, asyncio.CancelledError):
            return

        self.joining = True
        self._join_deadline = the_time + 5.0

    async def join(self, game_idx, player_name):
        self.lost_master = False
        self._lost_since = None
        if self.player_id is not None or self.joining:
            return
        if not (0 <= game_idx < len(self.games)):
            if self.ui_error:
                self.ui_error("No games available")
            return
        game_name, addr = self.games[game_idx]
        self.current_game = (game_name, addr)
        await self._send_join_to(game_name, addr, player_name)

    async def join_by_addr(self, game_tuple, player_name):
        self.lost_master = False
        self._lost_since = None
        if self.player_id is not None or self.joining:
            return
        if not game_tuple:
            if self.ui_error:
                self.ui_error("No game selected")
            return
        game_name, addr = game_tuple
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
        try:
            await self.transport.send_unicast(self.center, data)
            self.dispatch.track(self.center, msg.msg_seq, data)
            self._touch_tx(self.center)
        except (OSError, RuntimeError, asyncio.CancelledError):
            return

    async def leave_and_respawn(self, game_idx, player_name):
        if not self.center or self.joining:
            return
        if self.current_game is None:
            if 0 <= game_idx < len(self.games):
                self.current_game = self.games[game_idx]
            else:
                return

        old_center = self.center

        rc = pb.GameMessage.RoleChangeMsg(sender_role=pb.VIEWER)
        seq = self.dispatch.next_seq()
        msg = pb.GameMessage(
            msg_seq=seq,
            sender_id=self.player_id or 0,
            receiver_id=self.master_id or 0,
            role_change=rc
        )
        data = msg.SerializeToString()
        try:
            await self.transport.send_unicast(old_center, data)
            self.dispatch.track(old_center, seq, data)
            self._touch_tx(old_center)
        except (OSError, RuntimeError, asyncio.CancelledError):
            return

        self._await_rc_seq = seq
        self._respawn_name = player_name
        self._respawn_failsafe_at = time.monotonic() + 0.6

        self.joining = True
        self.pending_join_addr = old_center
        self.center = old_center
        self.await_unicast = True
        self._last_unicast = time.monotonic()

        self.player_id = None

    async def leave(self):
        if not self.center:
            return
        old_center = self.center
        rc = pb.GameMessage.RoleChangeMsg(sender_role=pb.VIEWER)
        msg = pb.GameMessage(
            msg_seq=self.dispatch.next_seq(),
            sender_id=self.player_id or 0,
            receiver_id=self.master_id or 0,
            role_change=rc
        )
        data = msg.SerializeToString()
        try:
            await self.transport.send_unicast(old_center, data)
            self.dispatch.track(old_center, msg.msg_seq, data)
            self._touch_tx(old_center)
        except (OSError, RuntimeError, asyncio.CancelledError):
            pass

        self.joining = False
        self._join_deadline = None
        self._respawn_failsafe_at = None
        self._await_rc_seq = None
        self._respawn_name = None
        self.ignore_unicast_until[old_center] = time.monotonic() + IGNORE_TTL
        self.center = None
        self.pending_join_addr = None

    async def _loop_retries_and_ping(self):
        while True:
            try:
                for (addr, _), payload in self.dispatch.due_retries():
                    await self.transport.send_unicast(addr, payload)
                    self._touch_tx(addr)

                dest = self.center or self.master_addr
                if self._handover_until and self.deputy_addr:
                    dest = self.deputy_addr

                if dest:
                    last = self._last_tx.get(dest, 0.0)
                    ping_interval = 0.3
                    if time.monotonic() - last > ping_interval:
                        ping = pb.GameMessage(
                            msg_seq=self.dispatch.next_seq(),
                            sender_id=self.player_id or 0,
                            receiver_id=self.master_id or 0,
                            ping=pb.GameMessage.PingMsg(),
                        )
                        data_ping = ping.SerializeToString()
                        await self.transport.send_unicast(dest, data_ping)
                        self.dispatch.track(dest, ping.msg_seq, data_ping)
                        self._touch_tx(dest)
            except (OSError, RuntimeError, asyncio.CancelledError):
                return

            await asyncio.sleep(0.01)

    async def _loop_timeout(self):
        while True:
            now = time.monotonic()
            if (self.center or self.pending_join_addr) and not self.await_unicast and not self.joining:
                is_deputy_me = (self.deputy_id is not None and self.player_id == self.deputy_id)
                thr = DEPUTY_FAST_THR if is_deputy_me else self._timeout_thr

                if now - self._last_unicast > thr:
                    if is_deputy_me:
                        await self._promote_to_master()
                        return

                    know_deputy_somehow = bool(self.deputy_addr) or (self.deputy_id is not None)

                    if know_deputy_somehow:
                        if not self._handover_until:
                            self._handover_until = now + HANDOVER_GRACE
                            self._handover_fallback_at = self._handover_until + HANDOVER_FALLBACK_PAD
                            if self.deputy_addr:
                                self._adopt_center(self.deputy_addr)
                                self._last_unicast = now
                                self._lost_since = None
                                self.loop.create_task(self._poke_new_master(self.deputy_addr))
                            self.lost_master = True
                            await asyncio.sleep(0.05)
                            continue

                        if now < self._handover_until:
                            await asyncio.sleep(0.05)
                            continue

                        if self._handover_fallback_at and now < self._handover_fallback_at:
                            await asyncio.sleep(0.05)
                            continue

                        self._end_handover()
                        await self._handle_host_lost(to_lobby=True)

                    else:
                        if self._lost_since is None:
                            self._lost_since = now
                            self.lost_master = True
                        else:
                            if (now - self._announce_seen_at) < NO_DEPUTY_GRACE:
                                await asyncio.sleep(0.05)
                                continue
                            if now - self._lost_since >= NO_DEPUTY_GRACE:
                                await self._handle_host_lost(to_lobby=True)
            await asyncio.sleep(0.05)

    async def _handle_host_lost(self, to_lobby: bool = False):
        if self.center:
            self.ignore_unicast_until[self.center] = time.monotonic() + IGNORE_TTL

        self.center = None
        self.master_addr = None
        self.deputy_addr = None

        self.joining = False
        self._join_deadline = None
        self._await_rc_seq = None
        self._respawn_name = None
        self._respawn_failsafe_at = None
        self._lost_since = None
        self._end_handover()

        self.lost_master = True
        if to_lobby:
            self.master_id = None
            self.current_game = None
            self.pending_join_addr = None
            if self.ui_error:
                try:
                    self.ui_error("Host disconnected")
                except Exception:
                    pass

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

    async def _loop_join_watchdog(self):
        while True:
            if self.joining and self._join_deadline is not None and time.monotonic() > self._join_deadline:
                self.joining = False
                self._join_deadline = None
                if self.ui_error:
                    self.ui_error("Join timed out")

            if self._await_rc_seq is not None and self._respawn_failsafe_at is not None:
                if time.monotonic() >= self._respawn_failsafe_at:
                    self._respawn_failsafe_at = None
                    name = self._respawn_name or self._my_name()
                    self._respawn_name = None
                    if self.current_game and (self.pending_join_addr or self.center):
                        addr = self.pending_join_addr or self.center
                        game_name, _ = self.current_game
                        await self._send_join_to(game_name, addr, name)

            await asyncio.sleep(0.05)
