from dataclasses import dataclass, field
from typing import Optional
import subprocess

def iface_ip(iface: str = "en0") -> str:
    try:
        return subprocess.check_output(["ipconfig", "getifaddr", iface]).decode().strip()
    except Exception:
        return "0.0.0.0"

@dataclass
class GameConfig:
    width: int = 40
    height: int = 30
    food_static: int = 1
    state_delay_ms: int = 200
    mcast_iface_ip: Optional[str] = field(default=None)

    def __post_init__(self):
        if self.mcast_iface_ip is None:
            self.mcast_iface_ip = iface_ip("en0") 