# snakenet/ui/app.py
import threading
import asyncio
import queue
import pygame
from pygame import (
    K_w, K_a, K_s, K_d,
    K_ESCAPE, K_h, K_j, K_r,
    K_BACKSPACE, K_RETURN, K_n
)

from core.config import GameConfig
from game.snapshot import from_proto_state
from proto.snakes_pb2 import UP, DOWN, LEFT, RIGHT

from roles.normal import NormalController
from roles.master import MasterController

CELL = 20
SIDEBAR = 260
BG = (0, 0, 0)
PANEL = (50, 50, 50)
FOOD = (128, 0, 200)
SNAKE = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 40, 40)


class NetThread:
    """Asyncio-цикл в отдельном потоке с submit для корутин."""
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.th = threading.Thread(target=self._run, daemon=True)
        self.th.start()

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def submit(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.th.join(timeout=1)


class App:
    def __init__(self):
        pygame.init()
        self.cfg = GameConfig()
        self.width_px = self.cfg.width * CELL + SIDEBAR
        self.height_px = self.cfg.height * CELL
        self.screen = pygame.display.set_mode((self.width_px, self.height_px))
        pygame.display.set_caption("Snakenet — lab MVP")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.big = pygame.font.SysFont(None, 32)

        self.mode = "lobby"
        self.role = "none"
        self.running = True

        self.state_q: queue.Queue = queue.Queue(maxsize=32)
        self.games_q: queue.Queue = queue.Queue(maxsize=32)
        self.games: list[tuple[str, tuple[str, int]]] = []
        self.state_view = None

        # Никнейм и его редактирование
        self.nickname = "player"
        self.edit_name = False

        # Защита от мульти-респавна по R
        self.respawn_pending = False

        self.net = NetThread()
        self.ctrl_normal: NormalController | None = None
        self.ctrl_master: MasterController | None = None
        self._ensure_normal_started()

    # ---------- callbacks ----------
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

    # ---------- roles ----------
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

    def _stop_master(self):
        if self.ctrl_master:
            self.net.submit(self.ctrl_master.stop())
            self.ctrl_master = None

    # ---------- main loop ----------
    def run(self):
        while self.running:
            self._drain_net_queues()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.KEYDOWN:
                    self._on_key_event(e)

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

        # Если ожидали респавн — как только «я» снова жив, уберём флаг
        if self.respawn_pending and not self._is_dead_me():
            self.respawn_pending = False

    # ---------- helpers ----------
    def _is_dead_me(self) -> bool:
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

    # ---------- input ----------
    def _on_key_event(self, e: pygame.event.Event):
        key = e.key

        if key == K_ESCAPE:
            # Назад в лобби
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
            return

        if self.mode == "lobby":
            if key == K_h:
                self._stop_normal()
                self._start_master()
            elif key == K_j:
                if self.ctrl_normal and self.games:
                    self.net.submit(self.ctrl_normal.join(0, self.nickname))
                    self.role = "normal"
                    self.mode = "game"
            elif key == K_n:
                # Вкл/выкл редактирование ника
                self.edit_name = not self.edit_name
            elif self.edit_name:
                # Простой набор ника: буквы/цифры/_-
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
            # Если мёртв — слушаем только R/Esc; оверлей рисуем только когда НЕ идёт респаун
            if self._is_dead_me():
                if key == K_r and not self.respawn_pending:
                    self.respawn_pending = True
                    if self.role == "normal" and self.ctrl_normal:
                        self.net.submit(self.ctrl_normal.leave_and_respawn(0, self.nickname))
                    elif self.role == "master" and self.ctrl_master:
                        self.net.submit(self.ctrl_master.respawn_self())
                return

            # Движение
            if key in (K_w, K_a, K_s, K_d):
                if self.role == "normal" and self.ctrl_normal:
                    d = {K_w: UP, K_s: DOWN, K_a: LEFT, K_d: RIGHT}[key]
                    self.net.submit(self.ctrl_normal.steer(d))
                elif self.role == "master" and self.ctrl_master:
                    d = {K_w: UP, K_s: DOWN, K_a: LEFT, K_d: RIGHT}[key]
                    self.net.submit(self.ctrl_master.steer_local(d))

    # ---------- draw ----------
    def _draw_lobby(self):
        self.screen.fill(BG)
        title = self.big.render("SNAKENET — Lobby", True, WHITE)
        self.screen.blit(title, (20, 20))
        hint = self.font.render("H — host (MASTER)   J — join (NORMAL)   N — nickname   Esc — quit", True, WHITE)
        self.screen.blit(hint, (20, 60))

        y = 110
        # Ник
        edit_color = GREEN if self.edit_name else WHITE
        name_text = f"Nickname: {self.nickname}" + (" ▎" if self.edit_name else "")
        self._text(name_text, 20, y, edit_color)
        y += 36

        if not self.games:
            self._text("Поиск игр... (ожидаем multicast Announcement)", 20, y, WHITE)
        else:
            self._text("Доступные игры:", 20, y, GREEN)
            y += 30
            for i, (name, addr) in enumerate(self.games[:10]):
                self._text(f"{i}. {name} @ {addr[0]}:{addr[1]}", 40, y, WHITE)
                y += 24
            y += 10
            self._text("Нажми J чтобы присоединиться к 0-й", 20, y, WHITE)

    def _draw_game(self):
        self.screen.fill(BG)
        if self.state_view:
            for (x, y) in self.state_view["food"]:
                pygame.draw.rect(self.screen, FOOD, (x * CELL, y * CELL, CELL, CELL))
            for pid, cells in self.state_view["snakes"].items():
                for (x, y) in cells:
                    pygame.draw.rect(self.screen, SNAKE, (x * CELL, y * CELL, CELL, CELL))

        # Боковая панель
        pygame.draw.rect(self.screen, PANEL,
                         (self.cfg.width * CELL, 0, SIDEBAR, self.cfg.height * CELL))
        self._text(f"Role: {self.role}", self.cfg.width * CELL + 10, 10, WHITE)
        self._text("Esc — в лобби", self.cfg.width * CELL + 10, 36, WHITE)

        if self.state_view:
            y = 70
            self._text("Scores:", self.cfg.width * CELL + 10, y, WHITE)
            y += 26
            names = self.state_view.get("names", {})
            for pid, score in sorted(self.state_view["scores"].items()):
                label = names.get(pid, f"#{pid}")
                self._text(f"{label}: {score}", self.cfg.width * CELL + 20, y, WHITE)
                y += 22

        # Оверлей смерти — НЕ показываем во время ожидаемого респауна
        if self._is_dead_me() and not self.respawn_pending:
            surf = pygame.Surface((self.cfg.width * CELL, self.cfg.height * CELL), flags=pygame.SRCALPHA)
            surf.fill((0, 0, 0, 160))
            self.screen.blit(surf, (0, 0))
            cx = (self.cfg.width * CELL) // 2
            cy = (self.cfg.height * CELL) // 2
            msg1 = self.big.render("Вы умерли", True, RED)
            msg2 = self.font.render("R — возродиться (сброс счёта)   Esc — меню", True, WHITE)
            self.screen.blit(msg1, (cx - msg1.get_width() // 2, cy - 20))
            self.screen.blit(msg2, (cx - msg2.get_width() // 2, cy + 16))

    def _text(self, s, x, y, color):
        self.screen.blit(self.font.render(s, True, color), (x, y))


def run():
    App().run()


if __name__ == "__main__":
    run()