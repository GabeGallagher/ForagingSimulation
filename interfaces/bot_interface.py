"""Contains information about the bots that the bots themselves
should not be privy to."""

from collections import deque
from microbot import MicroBot
from navigation.boundary_follow import BoundaryFollow
from nest import Nest
from arena import Arena
from numpy.typing import NDArray


class BotInterface:
    def __init__(
        self, bot: MicroBot, nest: Nest, location: list[float], arena: Arena
    ) -> None:
        self.bot: MicroBot = bot
        self.nest: Nest = nest
        self.location: list[float] = location
        self.arena: Arena = arena
        self.recent_positions: deque[list[float]] = deque()
        self.follow: BoundaryFollow | None = None

        # Debug state: the force/target the sim actually used most recently.
        # Written by the nest each frame, read (never mutated) by overlays.
        self.debug_force: NDArray | None = None
        self.debug_target: list[float] | None = None

    def report_collision(self, other) -> None:
        self.nest.handle_collision(other, self.location, self.bot.id)

    def set_location(self, location: list[float]) -> None:
        self.location[0] += location[0]
        self.location[1] += location[1]

    @property
    def x(self) -> float:
        return self.location[0]

    @property
    def y(self) -> float:
        return self.location[1]

    def report_unable_to_collect(self, obj) -> None:
        print(f"Bot {self.bot.id} unable to collect object at {obj.position}")

    def report_collected(self, obj) -> None:
        self.nest.handle_collection(self.bot.id, obj)
