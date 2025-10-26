import random
from core.util import wrap
from game.model import Cell, Snake, UP, DOWN, LEFT, RIGHT

OPP = {UP:DOWN, DOWN:UP, LEFT:RIGHT, RIGHT:LEFT}

class Engine:
    def __init__(self, cfg, rng=None):
        self.cfg = cfg
        self.rng = rng or random.Random()
        self.snakes: dict[int, Snake] = {}   # player_id -> Snake
        self.scores: dict[int, int] = {}
        self.state_order = 0
        self.food: set[tuple[int,int]] = set()

    def add_snake(self, player_id:int, head_xy, tail_dir:int):
        hx, hy = head_xy
        tx, ty = {
            UP:(hx, hy+1), DOWN:(hx, hy-1), LEFT:(hx+1, hy), RIGHT:(hx-1, hy)
        }[tail_dir]
        hx, hy = wrap(hx, self.cfg.width), wrap(hy, self.cfg.height)
        tx, ty = wrap(tx, self.cfg.width), wrap(ty, self.cfg.height)
        s = Snake([Cell(hx,hy), Cell(tx,ty)], OPP[tail_dir])
        self.snakes[player_id] = s
        self.scores.setdefault(player_id, 0)

    def desired_food_count(self):
        alive = sum(1 for s in self.snakes.values() if s.alive)
        return self.cfg.food_static + alive

    def steer(self, player_id:int, new_dir:int):
        s = self.snakes.get(player_id)
        if not s or not s.alive: return
        if new_dir != OPP[s.dir]:
            s.dir = new_dir

    def step(self):
        self.state_order += 1
        # 1) move heads
        new_heads = {}
        for pid, s in self.snakes.items():
            if not s.alive: continue
            hx, hy = s.cells[0].x, s.cells[0].y
            dx, dy = {UP:(0,-1), DOWN:(0,1), LEFT:(-1,0), RIGHT:(1,0)}[s.dir]
            nx, ny = wrap(hx+dx, self.cfg.width), wrap(hy+dy, self.cfg.height)
            new_heads[pid] = (nx, ny)

        # 2) grow or move tail
        for pid, s in self.snakes.items():
            if not s.alive: continue
            head_xy = new_heads[pid]
            if head_xy in self.food:     # eat
                self.food.remove(head_xy)
                self.scores[pid] = self.scores.get(pid,0) + 1
                s.cells.appendleft(Cell(*head_xy))  # tail stays
            else:                         # normal move
                s.cells.appendleft(Cell(*head_xy))
                s.cells.pop()

        # 3) collisions
        occupied = {}  # cell -> list(pid)
        for pid, s in self.snakes.items():
            if not s.alive: continue
            for c in s.cells:
                occupied.setdefault((c.x,c.y), []).append(pid)

        to_die = set()
        # head into body (own/others) after movement
        for pid, (hx,hy) in new_heads.items():
            # if multiple heads in one cell -> all die
            if sum((1 for p,(x,y) in new_heads.items() if (x,y)==(hx,hy))) > 1:
                to_die.add(pid); continue
            # if head cell occupied by any snake (including its own tail after move)
            if len(occupied.get((hx,hy), [])) >= 2:  # head + someone else
                to_die.add(pid)
            else:
                # head on own body excluding head itself
                if any((c.x,c.y)==(hx,hy) for c in list(self.snakes[pid].cells)[1:]):
                    to_die.add(pid)

        # 4) deaths → 0.5 food
        for pid in to_die:
            s = self.snakes[pid]
            s.alive = False
            for c in s.cells:
                if self.rng.random() < 0.5:
                    self.food.add((c.x,c.y))

        # 5) respawn food up to target
        target = self.desired_food_count()
        blocked = set()
        for s in self.snakes.values():
            for c in s.cells: blocked.add((c.x,c.y))
        free_cells = [(x,y) for y in range(self.cfg.height) for x in range(self.cfg.width)
                      if (x,y) not in blocked and (x,y) not in self.food]
        self.rng.shuffle(free_cells)
        for (x,y) in free_cells:
            if len(self.food) >= target: break
            self.food.add((x,y))