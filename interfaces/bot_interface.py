"""Contains information about the bots that the bots themselves
should not be privy to."""

from enums.bot_state import BotState
from microbot import MicroBot
from nest import Nest
from arena import Arena


class BotInterface:
    def __init__(
        self, bot: MicroBot, nest: Nest, location: list[float], arena: Arena
    ) -> None:
        self.bot: MicroBot = bot
        self.nest: Nest = nest
        self.location: list[float] = location
        self.arena: Arena = arena

    def report_collision(self, other) -> None:
        self.nest.handle_collision(other, self.location, self.bot.id)

    def set_location(self, location: list[float]) -> None:
        new_x = self.location[0] + location[0]
        new_y = self.location[1] + location[1]

        # Get bot radius for boundary checking
        bot_radius = self.bot.collider.radius

        # Check arena boundaries and clamp position
        if new_x - bot_radius < 0:
            self.bot.set_state(BotState.IDLE)
            self.location[0] = new_x = 0
            self.report_collision(self.arena)
        elif new_x + bot_radius > self.arena.x:
            self.bot.set_state(BotState.IDLE)
            self.location[0] = new_x = self.arena.x
            self.report_collision(self.arena)

        if new_y - bot_radius < 0:
            self.bot.set_state(BotState.IDLE)
            self.location[1] = new_y = 0
            self.report_collision(self.arena)
        elif new_y + bot_radius > self.arena.y:
            self.bot.set_state(BotState.IDLE)
            self.location[1] = new_y = self.arena.y
            self.report_collision(self.arena)

        self.location[0] = new_x
        self.location[1] = new_y

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
