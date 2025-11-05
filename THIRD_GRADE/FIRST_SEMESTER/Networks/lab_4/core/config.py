from dataclasses import dataclass
@dataclass
class GameConfig:
    width: int = 40
    height: int = 40
    food_static: int = 1
    state_delay_ms: int = 200