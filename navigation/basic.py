from arena import Arena
from navigation.navigation import Navigation
import numpy as np
from numpy.typing import NDArray


class BasicNavigation(Navigation):
    def __init__(self, arena: Arena) -> None:
        super().__init__()

    def set_target(self, target_loc: list[float]) -> None:
        pass

    def get_direction(self, bot_position: list[float]) -> NDArray:
        return np.zeros(2)
