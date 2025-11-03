# snakenet/game/rules.py
from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Dict, Set, Tuple, List

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

@dataclass
class Cell:
    x: int
    y: int

@dataclass
class Snake:
    player_id: int
    cells: list[Cell]        # head -> tail
    dir: int                 # UP/DOWN/LEFT/RIGHT
    alive: bool = True

class Engine:
    def __init__(self, cfg, rng: random.Random):
        self.cfg = cfg
        self.rng = rng
        self.width = cfg.width
        self.height = cfg.height
        self.state_order = 0

        self.snakes: Dict[int, Snake] = {}    # pid -> Snake
        self.scores: Dict[int, int] = {}      # pid -> score
        self.food: Set[Tuple[int, int]] = set()

        self._ensure_food()

    def add_snake(self, pid: int, center: Tuple[int, int], tail_dir: int):
        if pid in self.snakes:
            return
        cx, cy = center
        if tail_dir == UP:
            tail = (cx, (cy + 1) % self.height); dir0 = DOWN
        elif tail_dir == DOWN:
            tail = (cx, (cy - 1) % self.height); dir0 = UP
        elif tail_dir == LEFT:
            tail = ((cx + 1) % self.width, cy); dir0 = RIGHT
        else:  # RIGHT
            tail = ((cx - 1) % self.width, cy); dir0 = LEFT

        self.food.discard(center); self.food.discard(tail)
        snake = Snake(pid, [Cell(cx, cy), Cell(tail[0], tail[1])], dir0, True)
        self.snakes[pid] = snake
        self.scores.setdefault(pid, 0)
        self._ensure_food()

    def steer(self, pid: int, new_dir: int):
        s = self.snakes.get(pid)
        if not s or not s.alive:
            return
        if (s.dir == UP and new_dir == DOWN) or (s.dir == DOWN and new_dir == UP) or \
           (s.dir == LEFT and new_dir == RIGHT) or (s.dir == RIGHT and new_dir == LEFT):
            return
        s.dir = new_dir

    def step(self):
        self.state_order += 1
        if not self.snakes:
            self._ensure_food()
            return

        w, h = self.width, self.height

        # 1) вычисляем новые головы + кто ест
        new_heads: Dict[int, Tuple[int, int]] = {}
        grew: Set[int] = set()
        for pid, s in self.snakes.items():
            if not s.alive: continue
            hx, hy = s.cells[0].x, s.cells[0].y
            if s.dir == UP:    hy = (hy - 1) % h
            elif s.dir == DOWN: hy = (hy + 1) % h
            elif s.dir == LEFT: hx = (hx - 1) % w
            else:               hx = (hx + 1) % w
            new_heads[pid] = (hx, hy)
            if (hx, hy) in self.food:
                grew.add(pid)

        # 2) применяем движение
        for pid, s in self.snakes.items():
            if not s.alive: continue
            hx, hy = new_heads[pid]
            s.cells.insert(0, Cell(hx, hy))
            if pid in grew:
                self.food.discard((hx, hy))
                self.scores[pid] = self.scores.get(pid, 0) + 1
            else:
                s.cells.pop()

        # 3) коллизии и начисление очков «жертве»
        # строим карту: клетка -> список (pid, index_in_snake)
        occ: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
        for pid, s in self.snakes.items():
            if not s.alive: continue
            for idx, c in enumerate(s.cells):
                occ.setdefault((c.x, c.y), []).append((pid, idx))

        dead: Set[int] = set()
        bonus_for_victim: Dict[int, int] = {}  # victim_pid -> +1 (накопим; на многократные попадания можно увеличить)

        for pid, s in self.snakes.items():
            if not s.alive: continue
            hx, hy = s.cells[0].x, s.cells[0].y
            occupants = occ.get((hx, hy), [])
            # если в клетке >1 головы (несколько змей приехали в одну): все головы умрут, без бонусов
            heads_here = sum(1 for (opid, idx) in occupants if idx == 0)
            if heads_here > 1:
                dead.add(pid)
                continue

            # самоврез (голова в собственное тело)
            for (opid, idx) in occupants:
                if opid == pid and idx > 0:
                    dead.add(pid)
                    # self-collision НЕ даёт бонуса «жертве» (жертва = сам себя)
                    occupants = []  # чтобы ниже не дать бонус
                    break
            if pid in dead:
                continue

            # врезались в чужое тело/хвост ⇒ умираем, жертве +1
            for (opid, idx) in occupants:
                if opid != pid:  # чужая змея
                    dead.add(pid)
                    # «жертве» (той, в кого врезались) +1, если она не сама умерла «сама о себя»
                    # Бонус давать только если это не множественная голова (мы уже исключили heads_here>1)
                    bonus_for_victim[opid] = bonus_for_victim.get(opid, 0) + 1
                    break

        # 4) применяем смерти: конвертация клеток в еду p=0.5
        if dead:
            for pid in dead:
                s = self.snakes.get(pid)
                if not s: continue
                s.alive = False
                for c in s.cells:
                    if self.rng.random() < 0.5:
                        self.food.add((c.x, c.y))
                s.cells = []

        # 5) начисляем бонусы жертвам (если они ещё существуют — «не врезались сами в себя»)
        for victim_pid, add in bonus_for_victim.items():
            vs = self.snakes.get(victim_pid)
            if vs and vs.alive:
                self.scores[victim_pid] = self.scores.get(victim_pid, 0) + add

        # 6) поддерживаем объём еды
        self._ensure_food()

    def _ensure_food(self):
        need = int(self.cfg.food_static) + sum(1 for s in self.snakes.values() if s.alive)
        cur = len(self.food)
        if cur >= need: return

        occupied = {(c.x, c.y) for s in self.snakes.values() for c in s.cells if s.alive}
        free_total = self.width * self.height - len(occupied) - cur
        to_place = min(need - cur, max(0, free_total))

        tries = 0
        while to_place > 0 and tries < 10000:
            tries += 1
            x = self.rng.randrange(self.width); y = self.rng.randrange(self.height)
            if (x, y) in occupied or (x, y) in self.food: continue
            self.food.add((x, y)); to_place -= 1