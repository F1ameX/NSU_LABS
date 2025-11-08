import threading
import asyncio
import queue
import hashlib
import json
import pygame
from pygame import (
    K_w, K_a, K_s, K_d,
    K_ESCAPE, K_BACKSPACE, K_RETURN, MOUSEBUTTONDOWN
)

from core.config import GameConfig
from game.snapshot import from_proto_state
from snakes_proto import snakes_pb2 as pb
from roles.normal import NormalController
from roles.master import MasterController

GRAY_BG = (60, 60, 60)
WHITE = (235, 235, 235)
GREEN = (70, 210, 130)
RED = (230, 70, 70)
PANEL_BG = (38, 38, 38)
BORDER = (110, 110, 130)
CELL = 20

def _palette():
    return [
        (230, 57, 70),
        (29, 185, 84),
        (64, 156, 255),
        (255, 159, 28),
        (155, 135, 245),
        (255, 99, 132),
        (53, 201, 165),
        (255, 204, 0),
        (0, 200, 200),
        (200, 0, 200),
        (255, 87, 34),
        (0, 160, 255),
    ]

def _ensure_not_bg(color, bg=GRAY_BG):
    if color == bg:
        r, g, b = color
        return (min(r + 30, 255), g, b)
    return color

def stable_index(seed, mod):
    data = json.dumps(seed, sort_keys=True).encode()
    h = hashlib.sha1(data).digest()
    return h[0] % mod

def snake_color_for_pid(pid: int):
    pal = _palette()
    c = pal[pid % len(pal)]
    return _ensure_not_bg(c)

def food_color_for_coord(x: int, y: int):
    pal = _palette()
    idx = stable_index({"food": [x, y]}, len(pal))
    c = pal[idx]
    return _ensure_not_bg(c)

class NetPump:
    def __init__(self, loop):
        self.loop = loop
        self.th = threading.Thread(target=self._run, daemon=True)
        self.th.start()
    def submit(self, coro):
        self.loop.call_soon_threadsafe(lambda: asyncio.create_task(coro))
    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.th.join(timeout=1)
    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.hover = False
    def draw(self, screen, font):
        base = (85,85,85) if not self.hover else (110,110,110)
        pygame.draw.rect(screen, base, self.rect, border_radius=10)
        pygame.draw.rect(screen, BORDER, self.rect, width=2, border_radius=10)
        label = font.render(self.text, True, WHITE)
        screen.blit(label, (self.rect.centerx - label.get_width()//2, self.rect.centery - label.get_height()//2))
    def hit(self, pos):
        return self.rect.collidepoint(pos)

class App:
    def __init__(self):
        pygame.init()
        self.cfg = GameConfig()
        self.field_px_w = self.cfg.width * CELL
        w = self.field_px_w + 300
        h = max(self.cfg.height * CELL, 600)
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("chervi")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 18)
        self.big = pygame.font.SysFont("monospace", 28, bold=True)
        self.running = True
        self.mode = "lobby"
        self.role = "none"
        self.nickname = "player"
        self.state_view = None
        self.games = []
        self.games_q = queue.Queue(maxsize=64)
        self.state_q = queue.Queue(maxsize=64)
        self.error_q = queue.Queue(maxsize=16)
        self.ctrl_normal = None
        self.ctrl_master = None
        self.net = NetPump(asyncio.new_event_loop())
        self.btn_host = Button((w-280, 120, 240, 44), "Host")
        self.btn_join = Button((w-280, 172, 240, 44), "Join")
        self.input_rect = pygame.Rect(20, 80, 380, 36)
        self.input_focus = False
        self.selected_game_idx = 0
        self.selected_game_tuple = None
        self.pending_join = False
        self.modal_text = None
        self.modal_visible = False
        self.snake_colors = {}
        self._ensure_normal_started()

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

    def _cb_error(self, text):
        try:
            self.error_q.put_nowait(text)
        except queue.Full:
            with self.error_q.mutex:
                self.error_q.queue.clear()
            self.error_q.put_nowait(text)

    def _ensure_normal_started(self):
        if self.ctrl_normal is None:
            self.ctrl_normal = NormalController(
                self.net.loop, self.cfg,
                ui_push_state=self._cb_push_state,
                ui_set_games=self._cb_set_games,
                ui_error=self._cb_error
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
        self.pending_join = False
        self.snake_colors.clear()

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
                    self._on_key(e)
                elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                    self._on_click(e.pos)
            mx, my = pygame.mouse.get_pos()
            for b in [self.btn_host, self.btn_join]:
                b.hover = b.rect.collidepoint((mx, my))
            if self.mode == "lobby":
                self._draw_lobby()
            else:
                self._draw_game()
            if self.modal_visible and self.modal_text:
                self._draw_modal(self.modal_text)
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
                master_id = None
                for gp in state_pb.players.players:
                    if gp.role == pb.MASTER:
                        master_id = gp.id
                        break
                self.state_view = from_proto_state(state_pb, self.cfg.width, self.cfg.height)
                self.state_view["master_id"] = master_id
                if self.pending_join:
                    self.role = "normal"
                    self.mode = "game"
                    self.pending_join = False
                    self.snake_colors.clear()
        except queue.Empty:
            pass
        try:
            updated = False
            while True:
                self.games = self.games_q.get_nowait()
                updated = True
            if updated:
                if self.selected_game_idx >= len(self.games):
                    self.selected_game_idx = max(0, len(self.games) - 1)
                if self.games:
                    self.selected_game_tuple = self.games[self.selected_game_idx]
                else:
                    self.selected_game_tuple = None
        except queue.Empty:
            pass
        try:
            while True:
                err = self.error_q.get_nowait()
                self.modal_text = err
                self.modal_visible = True
                self.mode = "lobby"
                self.role = "none"
                self.pending_join = False
                self.state_view = None
        except queue.Empty:
            pass

    def _on_key(self, e):
        if self.modal_visible:
            if e.key in (K_RETURN, K_ESCAPE):
                self.modal_visible = False
            return
        if e.key == K_ESCAPE:
            if self.role == "normal" and self.ctrl_normal:
                self.net.submit(self.ctrl_normal.leave())
            self.mode = "lobby"
            self.role = "none"
            self.state_view = None
            self.pending_join = False
            self._stop_master()
            self._ensure_normal_started()
            return
        if self.mode != "lobby":
            if self._is_dead_me():
                if e.key == K_RETURN:
                    if self.role == "normal" and self.ctrl_normal:
                        self.net.submit(self.ctrl_normal.leave_and_respawn(self.selected_game_idx, self.nickname))
                    elif self.role == "master" and self.ctrl_master:
                        self.net.submit(self.ctrl_master.respawn_self())
                return
            if e.key == K_w:
                if self.role == "master" and self.ctrl_master:
                    self.net.submit(self.ctrl_master.steer_local(pb.UP))
                elif self.ctrl_normal:
                    self.net.submit(self.ctrl_normal.steer(pb.UP))
            elif e.key == K_s:
                if self.role == "master" and self.ctrl_master:
                    self.net.submit(self.ctrl_master.steer_local(pb.DOWN))
                elif self.ctrl_normal:
                    self.net.submit(self.ctrl_normal.steer(pb.DOWN))
            elif e.key == K_a:
                if self.role == "master" and self.ctrl_master:
                    self.net.submit(self.ctrl_master.steer_local(pb.LEFT))
                elif self.ctrl_normal:
                    self.net.submit(self.ctrl_normal.steer(pb.LEFT))
            elif e.key == K_d:
                if self.role == "master" and self.ctrl_master:
                    self.net.submit(self.ctrl_master.steer_local(pb.RIGHT))
                elif self.ctrl_normal:
                    self.net.submit(self.ctrl_normal.steer(pb.RIGHT))

    def _on_click(self, pos):
        if self.modal_visible:
            self.modal_visible = False
            return
        if self.mode == "lobby":
            if self.input_rect.collidepoint(pos):
                self.input_focus = True
            else:
                self.input_focus = False
            if self.btn_host.hit(pos):
                self._stop_normal()
                self._start_master()
            elif self.btn_join.hit(pos):
                if self.ctrl_normal and self.selected_game_tuple:
                    self.net.submit(self.ctrl_normal.join_by_addr(self.selected_game_tuple, self.nickname))
                    self.pending_join = True
            gx, gy = 20, 160
            row_h = 28
            for i in range(min(12, len(self.games))):
                r = pygame.Rect(gx, gy + i*row_h, 560, row_h)
                if r.collidepoint(pos):
                    self.selected_game_idx = i
                    self.selected_game_tuple = self.games[i]
            if self.input_focus:
                mx, my = pos
                if self.input_rect.collidepoint((mx, my)):
                    pass
        else:
            pass

    def _draw_lobby(self):
        self.screen.fill(GRAY_BG)
        title = self.big.render("CHERVI — Lobby", True, WHITE)
        self.screen.blit(title, (20, 20))
        self._draw_input()
        self.btn_host.draw(self.screen, self.font)
        self.btn_join.draw(self.screen, self.font)
        y = 130
        caption = self.font.render("Available games:", True, GREEN)
        self.screen.blit(caption, (20, y))
        gx, gy = 20, 160
        row_h = 28
        if not self.games:
            self.screen.blit(self.font.render("Searching...", True, WHITE), (gx, gy))
        else:
            max_rows = min(12, len(self.games))
            for i in range(max_rows):
                name, addr = self.games[i]
                r = pygame.Rect(gx, gy + i*row_h, 560, row_h)
                if i == self.selected_game_idx:
                    pygame.draw.rect(self.screen, (90, 90, 90), r, border_radius=6)
                line = f"{i}. {name} @ {addr[0]}:{addr[1]}"
                self.screen.blit(self.font.render(line, True, WHITE), (gx + 8, gy + i*row_h + 5))
        if self.pending_join:
            self.screen.blit(self.font.render("Joining...", True, GREEN), (self.btn_join.rect.x, self.btn_join.rect.y - 40))

    def _draw_input(self):
        pygame.draw.rect(self.screen, PANEL_BG, self.input_rect, border_radius=8)
        pygame.draw.rect(self.screen, BORDER, self.input_rect, width=2, border_radius=8)
        txt = self.font.render(f"Nickname: {self.nickname}", True, WHITE)
        self.screen.blit(txt, (self.input_rect.x + 10, self.input_rect.y + 8))
        if self.input_focus:
            mx, my = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0] and not self.input_rect.collidepoint((mx, my)):
                self.input_focus = False
            else:
                keys = pygame.key.get_pressed()
        if self.input_focus:
            pressed = pygame.key.get_pressed()
        if self.input_focus:
            for e in pygame.event.get(pygame.KEYDOWN):
                if e.key == K_BACKSPACE:
                    self.nickname = self.nickname[:-1]
                elif e.key == K_RETURN:
                    self.input_focus = False
                else:
                    ch = getattr(e, "unicode", "")
                    if ch and (32 <= ord(ch) <= 126) and len(self.nickname) < 16:
                        self.nickname += ch

    def _is_dead_me(self):
        if not self.state_view:
            return False
        if self.role == "normal" and self.ctrl_normal and self.ctrl_normal.player_id:
            pid = self.ctrl_normal.player_id
            cells = self.state_view["snakes"].get(pid)
            return (cells is None) or (len(cells) == 0)
        if self.role == "master":
            cells = self.state_view["snakes"].get(1)
            return (cells is None) or (len(cells) == 0)
        return False

    def _draw_game(self):
        self.screen.fill(GRAY_BG)
        panel_rect = pygame.Rect(self.field_px_w, 0, self.screen.get_width() - self.field_px_w, self.screen.get_height())
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect)
        pygame.draw.line(self.screen, BORDER, (self.field_px_w, 0), (self.field_px_w, self.screen.get_height()), 2)
        if self.state_view:
            for (x, y) in self.state_view["food"]:
                c = food_color_for_coord(x, y)
                pygame.draw.rect(self.screen, c, (x * CELL, y * CELL, CELL, CELL))
            names = self.state_view.get("names", {})
            for pid, cells in self.state_view["snakes"].items():
                col = snake_color_for_pid(pid)
                for (x, y) in cells:
                    pygame.draw.rect(self.screen, col, (x * CELL, y * CELL, CELL, CELL))
            x0 = self.field_px_w + 24
            y0 = 24
            self.screen.blit(self.font.render("Scoreboard", True, WHITE), (x0, y0))
            y0 += 28
            master_id = self.state_view.get("master_id")
            for pid, score in sorted(self.state_view["scores"].items(), key=lambda kv: (-kv[1], kv[0])):
                name = names.get(pid, f"player#{pid}")
                mark = " 卍" if master_id is not None and pid == master_id else ""
                col = snake_color_for_pid(pid)
                self.screen.blit(self.font.render(f"{name}{mark}: {score}", True, col), (x0, y0))
                y0 += 22
        if self._is_dead_me():
            cx = self.screen.get_width() // 2 - 150
            cy = self.screen.get_height() // 2
            msg1 = self.big.render("You are dead", True, RED)
            msg2 = self.font.render("Enter — respawn   Esc — menu", True, WHITE)
            self.screen.blit(msg1, (cx - msg1.get_width() // 2, cy - 20))
            self.screen.blit(msg2, (cx - msg2.get_width() // 2, cy + 16))

    def _draw_modal(self, text):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        bw, bh = 520, 180
        bx, by = (w - bw) // 2, (h - bh) // 2
        pygame.draw.rect(self.screen, PANEL_BG, (bx, by, bw, bh), border_radius=14)
        pygame.draw.rect(self.screen, BORDER, (bx, by, bw, bh), width=2, border_radius=14)
        t1 = self.big.render("Error", True, WHITE)
        self.screen.blit(t1, (bx + 20, by + 20))
        t2 = self.font.render(text, True, WHITE)
        self.screen.blit(t2, (bx + 20, by + 70))
        t3 = self.font.render("Press Enter or click to continue", True, GREEN)
        self.screen.blit(t3, (bx + 20, by + 120))
