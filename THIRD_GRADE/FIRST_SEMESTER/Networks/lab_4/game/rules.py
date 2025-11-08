# snakenet/game/rules.py
from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Dict, Set, Tuple, List

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

def wrap(v:int, m:int) -> int:
    return v % m

@dataclass
class Cell:
    x: int
    y: int

@dataclass
class Snake:
    player_id: int
    cells: List[Cell]
    dir: int
    alive: bool = True

class Engine:
    def __init__(self, cfg, rng: random.Random | None = None):
        self.cfg = cfg
        self.width: int = int(cfg.width)
        self.height: int = int(cfg.height)
        self.rng: random.Random = rng or random.Random()
        self.snakes: Dict[int, Snake] = {}
        self.scores: Dict[int, int] = {}
        self.food: Set[Tuple[int,int]] = set()
        self.state_order: int = 0

    # --- helpers ---
    def _dir_vec(self, d:int) -> Tuple[int,int]:
        return {
            UP:(0,-1), DOWN:(0,1), LEFT:(-1,0), RIGHT:(1,0)
        }[d]

    def _opposite(self, d:int) -> int:
        return {UP:DOWN, DOWN:UP, LEFT:RIGHT, RIGHT:LEFT}[d]

    # --- public API ---

    def add_snake(self, pid:int, center:Tuple[int,int], start_score:int=0):
        """
        Спавним змейку длиной 2:
        голова — в center, хвост — случайно в соседней клетке,
        направление — от хвоста к голове (то есть «противоположно хвосту»).
        Еду на этих клетках убираем.
        """
        cx, cy = center
        # выберем один из 4 соседей в пределах тора
        dirs = [UP, DOWN, LEFT, RIGHT]
        self.rng.shuffle(dirs)
        for d in dirs:
            dx, dy = self._dir_vec(d)
            tx, ty = wrap(cx - dx, self.width), wrap(cy - dy, self.height)  # хвост позади головы
            tail = (tx, ty)
            break
        head = (cx, cy)
        # убираем еду на стартовых клетках
        self.food.discard(head); self.food.discard(tail)
        # направление — «от хвоста к голове»
        s = Snake(pid, [Cell(head[0], head[1]), Cell(tail[0], tail[1])], dir=self._opposite(d))
        self.snakes[pid] = s
        self.scores[pid] = int(start_score)

    def steer(self, pid: int, new_dir: int):
        s = self.snakes.get(pid)
        if not s or not s.alive:
            return
        # запрет разворота «в себя»
        if (s.dir == UP and new_dir == DOWN) or (s.dir == DOWN and new_dir == UP) or \
           (s.dir == LEFT and new_dir == RIGHT) or (s.dir == RIGHT and new_dir == LEFT):
            return
        s.dir = new_dir

    def step(self):
        self.state_order += 1
        if not self.snakes:
            self._ensure_food()
            return

        # --- движение (и еда) ---
        new_heads: Dict[int, Tuple[int,int]] = {}
        grew: Set[int] = set()

        for pid, s in list(self.snakes.items()):
            if not s.alive:
                continue
            hx, hy = s.cells[0].x, s.cells[0].y
            dx, dy = self._dir_vec(s.dir)
            nx, ny = wrap(hx + dx, self.width), wrap(hy + dy, self.height)
            new_heads[pid] = (nx, ny)

        # применяем перемещения
        for pid, (nx, ny) in new_heads.items():
            s = self.snakes[pid]
            if not s.alive:
                continue
            # вставляем новую голову
            s.cells.insert(0, Cell(nx, ny))
            if (nx, ny) in self.food:
                # съели еду — растём, очко +1
                self.food.remove((nx, ny))
                self.scores[pid] = self.scores.get(pid, 0) + 1
                grew.add(pid)
            else:
                # обычный ход — хвост сдвигается
                s.cells.pop()

        # --- проверка коллизий ---
        # 1) head-to-head: все, кто делят одну клетку головами — умирают
        head_counts: Dict[Tuple[int,int], List[int]] = {}
        for pid, (x, y) in new_heads.items():
            head_counts.setdefault((x,y), []).append(pid)
        deaths: Set[int] = set()
        for xy, pids in head_counts.items():
            if len(pids) > 1:
                deaths.update(pids)

        # соберём множество клеток корпусов (без голов)
        body_owners: Dict[Tuple[int,int], int] = {}
        for pid, s in self.snakes.items():
            if not s.alive:
                continue
            for c in s.cells[1:]:
                body_owners[(c.x, c.y)] = pid

        # 2) врезка головой в чужое тело → умираем, жертве бонус
        for pid, (hx, hy) in new_heads.items():
            s = self.snakes[pid]
            if not s.alive or pid in deaths:
                continue
            owner = body_owners.get((hx, hy))
            if owner is None:
                continue
            if owner == pid:
                # самоврез — без бонусов
                deaths.add(pid)
                continue
            # голова pid врезалась в тело owner → pid умирает, owner получает бонус
            deaths.add(pid)
            self._reward_side_hit(victim_pid=owner, attacker_pid=pid)

        # пометить умерших
        for pid in deaths:
            s = self.snakes.get(pid)
            if s and s.alive:
                s.alive = False
                # каждая клетка трупа с шансом 0.5 становится едой
                for c in s.cells:
                    if self.rng.random() < 0.5:
                        self.food.add((c.x, c.y))

        # поддерживаем нужное кол-во еды
        self._ensure_food()

    # --- внутренняя логика ---

    def _reward_side_hit(self, victim_pid: int, attacker_pid: int) -> None:
        """
        Вызывается, когда голова attacker въехала в ТЕЛО victim (не head-to-head).
        Начисляет +1 очко victim и увеличивает его длину на 1.
        """
        if victim_pid == attacker_pid:
            return  # самоврез — без бонусов
        victim = self.snakes.get(victim_pid)
        if not victim or not victim.alive or not victim.cells:
            return
        # +1 очко жертве столкновения
        self.scores[victim_pid] = self.scores.get(victim_pid, 0) + 1
        # Увеличиваем длину на 1: дублируем последнюю клетку хвоста
        tail = victim.cells[-1]
        victim.cells.append(Cell(tail.x, tail.y))

    def _ensure_food(self):
        need = int(self.cfg.food_static) + sum(1 for s in self.snakes.values() if s.alive)
        cur = len(self.food)
        if cur >= need:
            return

        occupied = {(c.x, c.y) for s in self.snakes.values() for c in s.cells if s.alive}
        free_total = self.width * self.height - len(occupied) - cur
        to_place = min(need - cur, max(0, free_total))

        tries = 0
        while to_place > 0 and tries < 10000:
            tries += 1
            x = self.rng.randrange(self.width); y = self.rng.randrange(self.height)
            if (x, y) in occupied or (x, y) in self.food:
                continue
            self.food.add((x, y)); to_place -= 1
