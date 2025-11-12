import random
from core.util import wrap

def find_free_5x5(occupied: set[tuple[int, int]], w: int, h: int):
    centers = [(cx, cy) for cy in range(h) for cx in range(w)]
    random.shuffle(centers)

    for cx, cy in centers:
        ok = True
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if (wrap(cx + dx, w), wrap(cy + dy, h)) in occupied:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return (cx, cy)

    return None
