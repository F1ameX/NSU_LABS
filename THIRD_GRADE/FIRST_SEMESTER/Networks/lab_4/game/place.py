from core.util import wrap
def find_free_5x5(occupied: set[tuple[int,int]], w:int, h:int):
    for cy in range(h):
        for cx in range(w):
            ok = True
            for dy in range(-2,3):
                for dx in range(-2,3):
                    if (wrap(cx+dx,w), wrap(cy+dy,h)) in occupied:
                        ok = False; break
                if not ok: break
            if ok: return (cx, cy)
    return None