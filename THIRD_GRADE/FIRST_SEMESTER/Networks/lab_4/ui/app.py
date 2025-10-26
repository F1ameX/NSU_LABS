import pygame
from core.config import GameConfig
from core.timer import Ticker
from game.rules import Engine
from game.snapshot import snapshot
from game.place import find_free_5x5

CELL = 20
MARGIN_RIGHT = 260

class App:
    def __init__(self):
        pygame.init()
        self.cfg = GameConfig()
        w = self.cfg.width*CELL + MARGIN_RIGHT
        h = self.cfg.height*CELL
        self.screen = pygame.display.set_mode((w,h))
        pygame.display.set_caption("Snakenet (offline MVP)")
        self.clock = pygame.time.Clock()
        self.engine = Engine(self.cfg)

        # одна локальная змея
        occupied=set()
        pos = find_free_5x5(occupied, self.cfg.width, self.cfg.height) or (self.cfg.width//2,self.cfg.height//2)
        self.engine.add_snake(player_id=1, head_xy=pos, tail_dir=0)  # tail_dir=UP
        self.ticker = Ticker(self.cfg.state_delay_ms, self.on_tick)
        self.running = True

    def on_tick(self):
        self.engine.step()

    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: self.running=False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_w: self.engine.steer(1,0)
                    if e.key == pygame.K_s: self.engine.steer(1,1)
                    if e.key == pygame.K_a: self.engine.steer(1,2)
                    if e.key == pygame.K_d: self.engine.steer(1,3)

            self.ticker.pump()
            self.draw(snapshot(self.engine))
            pygame.display.flip()
            self.clock.tick(60)

    def draw(self, state):
        self.screen.fill((0,0,0))
        # поле
        for (x,y) in state["food"]:
            pygame.draw.rect(self.screen,(128,0,200),(x*CELL,y*CELL,CELL,CELL))
        for pid, cells in state["snakes"].items():
            for (x,y) in cells:
                pygame.draw.rect(self.screen,(255,255,0),(x*CELL,y*CELL,CELL,CELL))
        # правая панель (минимум — счёт)
        pygame.draw.rect(self.screen,(50,50,50),(self.cfg.width*CELL,0,MARGIN_RIGHT,self.cfg.height*CELL))
        self._text(f"Score: {state['scores'].get(1,0)}", self.cfg.width*CELL+10, 10)

    def _text(self, s, x, y):
        font = pygame.font.SysFont(None, 24)
        surf = font.render(s, True, (255,255,255))
        self.screen.blit(surf,(x,y))