from dataclasses import dataclass, field
import time

@dataclass
class Peer:
    addr: tuple[str,int] 
    player_id: int|None = None
    role: int|None = None
    last_seen: float = field(default_factory=time.monotonic)

class Peers:
    def __init__(self):
        self.by_addr: dict[tuple[str,int], Peer] = {} # All known peers by address
        self.center_addr: tuple[str,int] | None = None # Center of the "star"

    # Peers heartbeat
    def touch(self, addr):
        p = self.by_addr.get(addr)
        if not p:
            p = Peer(addr=addr); self.by_addr[addr] = p
        p.last_seen = time.monotonic()
        return p

    def set_center(self, addr): self.center_addr = addr
    def get_center(self): return self.center_addr