from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Dict, Set, Tuple, List
from core.util import wrap

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

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

    def _dir_vec(self, d:int) -> Tuple[int,int]:
        return {UP:(0,-1), DOWN:(0,1), LEFT:(-1,0), RIGHT:(1,0)}[d]

    def _opposite(self, d:int) -> int:
        return {UP:DOWN, DOWN:UP, LEFT:RIGHT, RIGHT:LEFT}[d]

    def add_snake(self, pid:int, center:Tuple[int,int], start_score:int=0):
        # Head + directon chosen randomly
        cx, cy = center
        dirs = [UP, DOWN, LEFT, RIGHT]
        self.rng.shuffle(dirs)

        occupied = {(c.x, c.y) for s in self.snakes.values() for c in s.cells if s.alive}
        for d in self.rng.sample((UP, DOWN, LEFT, RIGHT), 4):
            dx, dy = self._dir_vec(d)
            head = (cx, cy)
            tail = (wrap(cx - dx, self.width), wrap(cy - dy, self.height))
            if head not in occupied and tail not in occupied:
                break
        
        # Snake appending
        self.food.discard(head)
        self.food.discard(tail)
        s = Snake(pid, [Cell(head[0], head[1]), Cell(tail[0], tail[1])], dir=self._opposite(d))
        self.snakes[pid] = s
        self.scores[pid] = int(start_score)

    def steer(self, pid: int, new_dir: int):
        s = self.snakes.get(pid)
        if not s or not s.alive:
            return
        if new_dir == self._opposite(s.dir):
            return
        s.dir = new_dir

    def step(self):
        self.state_order += 1
        if not self.snakes:
            self._ensure_food()
            return

        new_heads: Dict[int, Tuple[int,int]] = {}
        grew: Set[int] = set()

        # New head positions
        for pid, s in list(self.snakes.items()):
            if not s.alive:
                continue
            hx, hy = s.cells[0].x, s.cells[0].y
            dx, dy = self._dir_vec(s.dir)
            nx, ny = wrap(hx + dx, self.width), wrap(hy + dy, self.height)
            new_heads[pid] = (nx, ny)

        # Move snakes, eat food
        for pid, (nx, ny) in new_heads.items():
            s = self.snakes[pid]
            if not s.alive:
                continue
            s.cells.insert(0, Cell(nx, ny))
            if (nx, ny) in self.food:
                self.food.remove((nx, ny))
                self.scores[pid] = self.scores.get(pid, 0) + 1
                grew.add(pid)
            else:
                s.cells.pop()

        # Check collisions (head - head)
        head_counts: Dict[Tuple[int,int], List[int]] = {}
        for pid, (x, y) in new_heads.items():
            head_counts.setdefault((x,y), []).append(pid)
        deaths: Set[int] = set()
        for _, pids in head_counts.items():
            if len(pids) > 1:
                deaths.update(pids)

        # Check collisions (head - body)
        body_owners: Dict[Tuple[int,int], int] = {}
        for pid, s in self.snakes.items():
            if not s.alive:
                continue
            for c in s.cells[1:]:
                body_owners[(c.x, c.y)] = pid

        for pid, (hx, hy) in new_heads.items():
            s = self.snakes[pid]
            if not s.alive or pid in deaths:
                continue
            owner = body_owners.get((hx, hy)) # owner of the cell where head moved
            if owner is None:
                continue
            if owner == pid: # suicide
                deaths.add(pid)
                continue
            deaths.add(pid) # killed by another snake
            self._reward_side_hit(victim_pid=owner)

        for pid in deaths:
            s = self.snakes.get(pid)
            if s and s.alive:
                s.alive = False # snake dies
                for c in s.cells: # every cell has 50% chance to become food
                    if self.rng.random() < 0.5:
                        self.food.add((c.x, c.y))

        self._ensure_food()

    def _reward_side_hit(self, victim_pid: int) -> None:
        victim = self.snakes.get(victim_pid)
        if not victim or not victim.alive or not victim.cells:
            return
        self.scores[victim_pid] = self.scores.get(victim_pid, 0) + 1
        tail = victim.cells[-1]
        victim.cells.append(Cell(tail.x, tail.y))

    def _ensure_food(self):
        need = int(self.cfg.food_static) + sum(1 for s in self.snakes.values() if s.alive)
        cur = len(self.food)

        if cur >= need:
            return

        occupied = {(c.x, c.y) for s in self.snakes.values() if s.alive for c in s.cells}
        free = [(x, y) for x in range(self.width) for y in range(self.height)
                if (x, y) not in occupied and (x, y) not in self.food]
        if not free:
            return
        
        to_add = min(need - cur, len(free))
        if to_add == 0:
            return

        for xy in self.rng.sample(free, to_add):
            self.food.add(xy)
