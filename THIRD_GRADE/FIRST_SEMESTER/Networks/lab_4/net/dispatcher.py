import time
from collections import deque

class Dispatcher:
    def __init__(self, state_delay_ms: int):
        self.seq = 1
        self.waiting = {}
        self.retry_int = max(1, state_delay_ms // 10) / 1000.0

    def next_seq(self) -> int:
        s = self.seq; self.seq += 1; return s

    def track(self, addr, seq: int, payload: bytes):
        self.waiting[(addr, seq)] = (payload, time.monotonic() + self.retry_int, 10)

    def ack(self, addr, seq:int):
        self.waiting.pop((addr, seq), None)

    def due_retries(self):
        now = time.monotonic()
        for key, (payload, deadline, left) in list(self.waiting.items()):
            if now >= deadline:
                if left <= 0:
                    self.waiting.pop(key, None)
                else:
                    self.waiting[key] = (payload, now + self.retry_int, left - 1)
                    yield key, payload