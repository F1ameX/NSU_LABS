from collections import deque
from dataclasses import dataclass

UP, DOWN, LEFT, RIGHT = (0,1,2,3)

@dataclass
class Cell: x:int; y:int

class Snake:
    def __init__(self, cells: list[Cell], direction:int):
        self.cells = deque(cells)
        self.dir = direction
        self.alive = True

class Board:
    def __init__(self, w:int, h:int):
        self.w, self.h = w, h
        self.food: set[tuple[int,int]] = set()