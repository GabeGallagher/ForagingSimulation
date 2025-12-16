from arena import Arena
import random
from microbot import MicroBot
from enums.bot_state import BotState
from typing import Dict
import math
from time_step_observer import TimeStepObserver


"""Contains information about the bots that the bots themselves
should not be privy to."""


class BotInterface:
    def __init__(self, bot: MicroBot, location: list[float]) -> None:
        self.bot = bot
        self.location = location

    def set_location(self, location: list[float]):
        self.location[0] += location[0]
        self.location[1] += location[1]

    @property
    def x(self):
        return self.location[0]

    @property
    def y(self):
        return self.location[1]


"""Creates micro bots, receives their signals, and controls behavior"""


class Nest(TimeStepObserver):
    def __init__(self, arena: Arena, location: list[float]) -> None:
        super().__init__()
        self.arena = arena
        self.location = self.get_location(arena, location)
        self.bots: Dict[int, BotInterface] = {}
        self.instantiate_bot()

    """Gets location within the simulation arena. If location is known,
    return known location. Else, randomize location within arena bounds
    TODO: Currently, basic implementation requires the nest to know its
    location. However, it must eventually be refactored to only know its
    location relative to the targets in the arena"""

    def get_location(self, arena: Arena, location: list[float]) -> list[float]:
        if location is not None:
            return location
        else:
            x_pos = random.uniform(0, arena.x)
            y_pos = random.uniform(0, arena.y)
            return [x_pos, y_pos]

    def instantiate_bot(self):
        id = self.generate_bot_id()
        bot = MicroBot(id)
        bot_interface = BotInterface(bot, self.location.copy())
        self.bots[id] = bot_interface
        bot.set_interface(bot_interface)
        self.bot_move_command(id)

    def get_bot_interface(self, bot_id) -> BotInterface:
        return self.bots[bot_id]

    # TODO: look into better ways to generate unique id
    def generate_bot_id(self):
        return len(self.bots) - 1

    def bot_move_command(self, bot_id):
        bot: MicroBot = self.bots[bot_id].bot
        # TODO: refactor this to handle arenas with multiple targets. Works for now because there will always just be one
        bot_angle_to_target = self.get_new_bot_orientation(
            bot_id, self.arena.targets[0]
        )
        bot.rotate(
            bot_angle_to_target
        )  # calculate bot orientation and rotate relative to target
        bot.set_state(BotState.EXPLORING)

    def get_new_bot_orientation(self, bot_id, target: list[float]):
        bot: MicroBot = self.bots[bot_id].bot
        bot_location = self.bots[bot_id].location
        dx = target[0] - bot_location[0]
        dy = target[1] - bot_location[1]
        return math.atan2(dx, dy)

    def update(self, time_delta: float):
        print(f"Bot location: {self.bots[0].x}, {self.bots[0].y}")
