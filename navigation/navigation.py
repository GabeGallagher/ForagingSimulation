from abc import ABC, abstractmethod
from numpy.typing import NDArray
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interfaces.bot_interface import BotInterface


class Navigation(ABC):
    def __init__(self) -> None:
        self.last_forces: dict[str, NDArray] = {}

    @abstractmethod
    def set_target(self, target_loc: list[float]) -> None:
        pass

    @abstractmethod
    def get_direction(self, bot_position: list[float], bot_rotation: float) -> float:
        pass

    """Heading for a specific bot. stuck is the nest's report that the bot has
    stopped making progress; navigators with a recovery behavior override this"""

    def get_bot_direction(self, bot_interface: "BotInterface", stuck: bool) -> float:
        return self.get_direction(bot_interface.location, bot_interface.bot.orientation)
