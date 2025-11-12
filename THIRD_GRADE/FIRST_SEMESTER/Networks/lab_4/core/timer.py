import time

class Ticker:
    def __init__(self, delay_ms, on_tick):
        self.delay = delay_ms / 1000.0
        self.on_tick = on_tick
        self._acc = 0.0
    def pump(self):
        now = time.perf_counter()
        if not hasattr(self, "_last"): self._last = now
        dt = now - self._last; self._last = now; self._acc += dt
        while self._acc >= self.delay:
            self._acc -= self.delay
            self.on_tick()