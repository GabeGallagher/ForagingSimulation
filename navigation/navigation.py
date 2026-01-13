from abc import ABC, abstractmethod
from numpy.typing import NDArray


class Navigation(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set_target(self, target_loc: list[float]) -> None:
        pass

    @abstractmethod
    def get_direction(self, bot_position: list[float]) -> NDArray:
        pass
