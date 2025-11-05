import threading
import asyncio
import queue
import math
import pygame
from pygame import (
    K_w, K_a, K_s, K_d, K_ESCAPE, K_h, K_j, K_r,
    K_BACKSPACE, K_RETURN, K_n, MOUSEBUTTONDOWN
)
from core.config import GameConfig
from game.snapshot import from_proto_state
from proto.snakes_pb2 import UP, DOWN, LEFT, RIGHT
from roles.normal import NormalController
from roles.master import MasterController

BG = (12, 12, 16)
PANEL = (150, 30, 40)
PANEL_TXT = (235, 235, 235)
FOOD = (120, 90, 200)
YELLOW = (230, 230, 40)
RED = (220, 50, 50)
GREEN = (60, 200, 120)
WHITE = (230, 230, 230)
BLACK = (0, 0, 0)
CELL = 20
SIDEBAR_W = 360
RIGHT_PAD = 32

def draw_box(surface, rect, title, font, color=PANEL, pad=8):
    pygame.draw.rect(surface, color, rect, width=3, border_radius=4)
    if title:
        tx = font.render(title, True, PANEL_TXT)
        surface.blit(tx, (rect.x + pad, rect.y - tx.get_height() - 4))

def draw_star(surface, center, r, color=YELLOW):
    cx, cy = center
    pts = []
    for i in range(10):
        ang = -math.pi/2 + i * math.pi/5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr*math.cos(ang), cy + rr*math.sin(ang)))
    pygame.draw.polygon(surface, color, pts)

def draw_arrow_enter(surface, rect, color=PANEL):
    pygame.draw.rect(surface, color, rect, width=2, border_radius=4)
    x, y, w, h = rect
    mid = y + h//2
    pygame.draw.line(surface, color, (x+6, mid), (x+w-8, mid), 2)
    pygame.draw.polygon(surface, color, [(x+w-10, mid-6), (x+w-2, mid), (x+w-10, mid+6)])

class NetPump:
    def __init__(self, loop):
        self.loop = loop
        self.th = threading.Thread(target=self._run, daemon=True)
        self.th.start()
    def submit(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop)
    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.th.join(timeout=1)
    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

class App:
    def __init__(self):
        pygame.init()
        grid_w = GameConfig().width * CELL
        grid_h = GameConfig().height * CELL
        self.screen = pygame.display.set_mode((grid_w + SIDEBAR_W + RIGHT_PAD, grid_h))
        pygame.display.set_caption("Snakenet")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 18)
        self.big = pygame.font.SysFont("monospace", 28, bold=True)

        self.running = True
        self.mode = "lobby"
        self.role = "none"
        self.nickname = "player"
        self.cfg = GameConfig()
        self.state_view = None

        self.games = []
        self.games_q = queue.Queue(maxsize=32)
        self.state_q = queue.Queue(maxsize=32)
        self.respawn_pending = False
        self.edit_name = False
        self.ctrl_normal = None
        self.ctrl_master = None
        self.net = NetPump(asyncio.new_event_loop())
        self._ensure_normal_started()

        self.btn_exit = None
        self.btn_newgame = None
        self.join_buttons = []

    def _get_my_pid(self):
        if self.role == "normal" and self.ctrl_normal and self.ctrl_normal.player_id:
            return self.ctrl_normal.player_id
        if self.role == "master":
            return 1
        return None

    def _cb_push_state(self, state_pb):
        try:
            self.state_q.put_nowait(state_pb)
        except queue.Full:
            with self.state_q.mutex:
                self.state_q.queue.clear()
            self.state_q.put_nowait(state_pb)

    def _cb_set_games(self, games_list):
        try:
            self.games_q.put_nowait(games_list)
        except queue.Full:
            with self.games_q.mutex:
                self.games_q.queue.clear()
            self.games_q.put_nowait(games_list)

    def _ensure_normal_started(self):
        if self.ctrl_normal is None:
            self.ctrl_normal = NormalController(
                self.net.loop, self.cfg,
                ui_push_state=self._cb_push_state,
                ui_set_games=self._cb_set_games
            )
            self.net.submit(self.ctrl_normal.start())

    def _stop_normal(self):
        if self.ctrl_normal:
            self.net.submit(self.ctrl_normal.stop())
            self.ctrl_normal = None

    def _start_master(self):
        if self.ctrl_master is None:
            self.ctrl_master = MasterController(
                self.net.loop, self.cfg,
                ui_push_state=self._cb_push_state,
                player_name=self.nickname
            )
            self.net.submit(self.ctrl_master.start())
            self.role = "master"
            self.mode = "game"
            self.state_view = None
            self.respawn_pending = False

    def _stop_master(self):
        if self.ctrl_master:
            self.net.submit(self.ctrl_master.stop())
            self.ctrl_master = None

    def run(self):
        while self.running:
            self._drain_net_queues()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.KEYDOWN:
                    self._on_key_event(e)
                elif e.type == MOUSEBUTTONDOWN:
                    self._on_mouse(e.pos)
            if self.mode == "lobby":
                self._draw_lobby()
            else:
                self._draw_game()
            pygame.display.flip()
            self.clock.tick(60)
        self._stop_master()
        self._stop_normal()
        self.net.stop()
        pygame.quit()

    def _drain_net_queues(self):
        try:
            while True:
                state_pb = self.state_q.get_nowait()
                self.state_view = from_proto_state(state_pb, self.cfg.width, self.cfg.height)
        except queue.Empty:
            pass
        try:
            while True:
                self.games = self.games_q.get_nowait()
        except queue.Empty:
            pass

        if self.role == "normal" and self.ctrl_normal and getattr(self.ctrl_normal, "lost_master", False):
            self.ctrl_normal.lost_master = False
            self.mode = "lobby"
            self.role = "none"
            self.state_view = None
            self.games = []
            with self.games_q.mutex:
                self.games_q.queue.clear()
            with self.state_q.mutex:
                self.state_q.queue.clear()
            self.respawn_pending = False
            self._stop_master()
            self._ensure_normal_started()

        if self.respawn_pending and not self._is_dead_me():
            self.respawn_pending = False

    def _is_dead_me(self):
        if not self.state_view:
            return False
        my_pid = self._get_my_pid()
        if my_pid is None:
            return False
        cells = self.state_view["snakes"].get(my_pid)
        return (cells is None) or (len(cells) == 0)

    def _on_mouse(self, pos):
        if self.mode == "game":
            if self.btn_exit and self.btn_exit.collidepoint(pos):
                self._go_lobby()
            elif self.btn_newgame and self.btn_newgame.collidepoint(pos):
                self._new_game()
            else:
                for rect, idx in self.join_buttons:
                    if rect.collidepoint(pos):
                        if self.role == "master":
                            self._stop_master()
                        if self.role == "normal" and self.ctrl_normal:
                            self.net.submit(self.ctrl_normal.leave())
                        self._ensure_normal_started()
                        self._join_index(idx)
                        break
        else:
            for rect, idx in self.join_buttons:
                if rect.collidepoint(pos):
                    self._join_index(idx)
                    break

    def _go_lobby(self):
        if self.role == "normal" and self.ctrl_normal:
            self.net.submit(self.ctrl_normal.leave())
        self.mode = "lobby"
        self.role = "none"
        self.state_view = None
        self.games = []
        with self.games_q.mutex:
            self.games_q.queue.clear()
        with self.state_q.mutex:
            self.state_q.queue.clear()
        self.respawn_pending = False
        self._stop_master()
        self._ensure_normal_started()
    def _new_game(self):
        if self.role == "normal" and self.ctrl_normal:
            self.net.submit(self.ctrl_normal.leave())

        if self.ctrl_master:
            self._stop_master()

        self._ensure_normal_started()
        self._start_master()

    def _join_index(self, idx):
        if self.ctrl_normal and self._games_len() > 0:
            self.net.submit(self.ctrl_normal.join(idx, self.nickname))
            self.role = "normal"
            self.mode = "game"
            self.state_view = None
            self.respawn_pending = False

    def _games_len(self):
        return len(self.games) if self.games else 0

    def _my_host_port(self):
        if self.ctrl_master:
            return self.ctrl_master.transport.unicast_addr()[1]
        return None

    def _entry_addr(self, entry):
        if isinstance(entry, tuple):
            return entry[1]
        return (entry.get("addr")
                or entry.get("address")
                or entry.get("center"))

    def _my_host_addr(self):
        return self.ctrl_master.transport.unicast_addr() if self.ctrl_master else None

    def _entry_addr(self, entry):
        if isinstance(entry, tuple):
            return entry[1]
        return (entry.get("addr") or
                entry.get("address") or
                entry.get("center"))

    def _on_key_event(self, e):
        key = e.key
        if key == K_ESCAPE:
            self._go_lobby()
            return

        if self.mode == "lobby":
            if key == K_h:
                self._ensure_normal_started()
                self._start_master()
            elif key == K_j:
                if self._games_len() > 0:
                    self._join_index(0)
            elif key == K_n:
                self.edit_name = not self.edit_name
            elif self.edit_name:
                ch = getattr(e, "unicode", "")
                if key == K_BACKSPACE:
                    if self.nickname:
                        self.nickname = self.nickname[:-1]
                elif key == K_RETURN:
                    self.edit_name = False
                elif ch and (ch.isalnum() or ch in "_-"):
                    if len(self.nickname) < 16:
                        self.nickname += ch

        elif self.mode == "game":
            if self._is_dead_me():
                if key == K_r and not self.respawn_pending:
                    self.respawn_pending = True
                    if self.role == "normal" and self.ctrl_normal:
                        self.net.submit(self.ctrl_normal.leave_and_respawn(0, self.nickname))
                    elif self.role == "master" and self.ctrl_master:
                        self.net.submit(self.ctrl_master.respawn_self())
                return
            if key == K_w:
                if self.role == "master" and self.ctrl_master:
                    self.net.submit(self.ctrl_master.steer_local(UP))
                elif self.ctrl_normal:
                    self.net.submit(self.ctrl_normal.steer(UP))
            elif key == K_s:
                if self.role == "master" and self.ctrl_master:
                    self.net.submit(self.ctrl_master.steer_local(DOWN))
                elif self.ctrl_normal:
                    self.net.submit(self.ctrl_normal.steer(DOWN))
            elif key == K_a:
                if self.role == "master" and self.ctrl_master:
                    self.net.submit(self.ctrl_master.steer_local(LEFT))
                elif self.ctrl_normal:
                    self.net.submit(self.ctrl_normal.steer(LEFT))
            elif key == K_d:
                if self.role == "master" and self.ctrl_master:
                    self.net.submit(self.ctrl_master.steer_local(RIGHT))
                elif self.ctrl_normal:
                    self.net.submit(self.ctrl_normal.steer(RIGHT))

    def _draw_lobby(self):
        self.screen.fill(BG)
        self.screen.blit(self.big.render("SNAKENET - Lobby", True, WHITE), (20, 20))
        self.screen.blit(self.font.render("H - host   J - join (selected)   N - nickname   Esc - quit", True, WHITE), (20, 60))

        y = 100
        edit_color = GREEN if self.edit_name else WHITE
        name_text = f"Nickname: {self.nickname}" + (" ▎" if self.edit_name else "")
        self.screen.blit(self.font.render(name_text, True, edit_color), (20, y))

        cfg_box = pygame.Rect(self.screen.get_width() - SIDEBAR_W + 16, 90, SIDEBAR_W - 40, 70)
        draw_box(self.screen, cfg_box, "Default config", self.font)
        cfg_y = cfg_box.y + 8
        self.screen.blit(self.font.render(f"Size: {self.cfg.width}x{self.cfg.height}", True, PANEL_TXT), (cfg_box.x + 10, cfg_y)); cfg_y += 24
        self.screen.blit(self.font.render(f"Food: {self.cfg.food_static}+1x", True, PANEL_TXT), (cfg_box.x + 10, cfg_y))

        self.join_buttons = []
        box = pygame.Rect(20, 160, self.screen.get_width() - 40, self.screen.get_height() - 180)
        draw_box(self.screen, box, "Available games", self.font)
        hdr_y = box.y - 26
        cols = ["", "#", "Size", "Food", ""]
        col_x = [box.x + 12, box.x + 260, box.x + 320, box.x + 400, box.right - 44]
        for i, h in enumerate(cols):
            self.screen.blit(self.font.render(h, True, PANEL_TXT), (col_x[i], hdr_y))

        row_y = box.y + 10
        if self._games_len() == 0:
            self.screen.blit(self.font.render("Searching for games (multicast announcement)...", True, WHITE),
                             (box.x + 12, row_y))
        else:
            for idx, entry in enumerate(self.games):
                if isinstance(entry, tuple):
                    name, addr = entry
                    leader = name
                    players = "-"
                    size = "-"
                    food = "-"
                else:
                    leader = entry.get("leader") or entry.get("name") or "host"
                    players = str(entry.get("players", "-"))
                    size = entry.get("size", "-")
                    food = entry.get("food", "-")

                self.screen.blit(self.font.render(str(leader), True, WHITE), (col_x[0], row_y))
                self.screen.blit(self.font.render(str(players), True, WHITE), (col_x[1], row_y))
                self.screen.blit(self.font.render(str(size), True, WHITE), (col_x[2], row_y))
                self.screen.blit(self.font.render(str(food), True, WHITE), (col_x[3], row_y))

                btn = pygame.Rect(col_x[4], row_y - 2, 28, 22)
                draw_arrow_enter(self.screen, btn)
                self.join_buttons.append((btn, idx))
                row_y += 26

    def _draw_game(self):
        self.screen.fill(BG)
        grid_w = self.cfg.width * CELL
        if self.state_view:
            for (x, y) in self.state_view["food"]:
                pygame.draw.rect(self.screen, FOOD, (x * CELL, y * CELL, CELL, CELL))
            my_pid = self._get_my_pid()
            for pid, cells in self.state_view["snakes"].items():
                color = YELLOW if (my_pid is not None and pid == my_pid) else RED
                for (x, y) in cells:
                    pygame.draw.rect(self.screen, color, (x * CELL, y * CELL, CELL, CELL))

        x0 = grid_w + 24
        y0 = 24

        score_box = pygame.Rect(x0 - 8, y0 + 18, SIDEBAR_W - 40, 160)
        draw_box(self.screen, score_box, "Leaderboard", self.font)
        list_y = score_box.y + 8
        names = self.state_view.get("names", {}) if self.state_view else {}
        scores = self.state_view.get("scores", {}) if self.state_view else {}
        my_pid = self._get_my_pid()
        rank = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        for i, (pid, sc) in enumerate(rank[:8], start=1):
            nm = names.get(pid, f"player#{pid}")
            line = f"{i}. {nm}  {sc}"
            surf = self.font.render(line, True, WHITE)
            self.screen.blit(surf, (score_box.x + 10, list_y))
            if my_pid is not None and pid == my_pid:
                draw_star(self.screen, (score_box.x + 10 + surf.get_width() + 10, list_y + surf.get_height()//2), 7)
            list_y += 22

        y0 = score_box.bottom + 24
        game_box = pygame.Rect(x0 - 8, y0 + 18, SIDEBAR_W - 40, 110)
        draw_box(self.screen, game_box, "Current game", self.font)
        gy = game_box.y + 8
        leader = names.get(1, "-") if self.state_view else "-"
        size_txt = f"Size: {self.cfg.width}x{self.cfg.height}"
        food_txt = f"Food: {self.cfg.food_static}+1x"
        self.screen.blit(self.font.render(f"Host: {leader}", True, WHITE), (game_box.x + 10, gy)); gy += 24
        self.screen.blit(self.font.render(size_txt, True, WHITE), (game_box.x + 10, gy)); gy += 24
        self.screen.blit(self.font.render(food_txt, True, WHITE), (game_box.x + 10, gy)); gy += 24

        y0 = game_box.bottom + 24
        exit_text = self.big.render("Exit", True, WHITE)
        new_text  = self.big.render("New Game", True, WHITE)
        padx, pady = 16, 8
        self.btn_exit = pygame.Rect(x0, y0,exit_text.get_width() + 2*padx, exit_text.get_height() + 2*pady)
        self.btn_newgame = pygame.Rect(self.btn_exit.right + 24, y0, new_text.get_width() + 2*padx, new_text.get_height() + 2*pady)
        pygame.draw.rect(self.screen, PANEL, self.btn_exit, width=3, border_radius=6)
        pygame.draw.rect(self.screen, PANEL, self.btn_newgame, width=3, border_radius=6)
        self.screen.blit(exit_text, (self.btn_exit.x + padx, self.btn_exit.y + pady))
        self.screen.blit(new_text,  (self.btn_newgame.x + padx, self.btn_newgame.y + pady))

        y0 = self.btn_exit.bottom + 24
        list_box = pygame.Rect(x0 - 8, y0 + 18, SIDEBAR_W - 40, self.screen.get_height() - (y0 + 30))
        draw_box(self.screen, list_box, "Host      #      Join", self.font)
        self.join_buttons = []
        row_y = list_box.y + 8

        pairs = [(i, e) for i, e in enumerate(self.games)]
        if self.role == "normal" and self.ctrl_normal and self.ctrl_normal.center:
            cur = self.ctrl_normal.center
            pairs = [(i, e) for i, e in pairs if self._entry_addr(e) != cur]

        if self.role == "master" and self.ctrl_master:
            my_port = self._my_host_port()
            if my_port is not None:
                pairs = [
                    (i, e) for i, e in pairs
                    if (self._entry_addr(e) and self._entry_addr(e)[1] != my_port)
                ]

        for j, (orig_idx, entry) in enumerate(pairs[:8]):
            if isinstance(entry, tuple):
                name, addr = entry
                leader = name
                players = "-"
            else:
                leader = entry.get("leader") or entry.get("name") or "host"
                players = str(entry.get("players", "-"))

            line = f"{leader:16} {players:>2}"
            self.screen.blit(self.font.render(line, True, WHITE), (list_box.x + 10, row_y))

            btn = pygame.Rect(list_box.right - 36, row_y - 2, 26, 22)
            draw_arrow_enter(self.screen, btn)
            self.join_buttons.append((btn, orig_idx))
            row_y += 24

        if self._is_dead_me() and not self.respawn_pending:
            cx = (self.cfg.width * CELL) // 2
            cy = self.screen.get_height() // 2
            msg1 = self.big.render("You are dead", True, RED)
            msg2 = self.font.render("R - respawn   Esc - menu", True, WHITE)
            self.screen.blit(msg1, (cx - msg1.get_width() // 2, cy - 20))
            self.screen.blit(msg2, (cx - msg2.get_width() // 2, cy + 16))

def run():
    App().run()

if __name__ == "__main__":
    run()