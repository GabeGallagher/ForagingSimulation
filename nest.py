from arena import Arena
import random
from microbot import MicroBot


"""Contains information about the bots that the bots themselves
should not be privy to."""
class BotInterface:
    def __init__(self, bot: MicroBot, position: list[float]) -> None:
        self.bot = bot
        self.position = position

    @property
    def x(self):
        return self.position[0]
    
    @property
    def y(self):
        return self.position[1]

"""Creates micro bots, receives their signals, and controls behavior"""


class Nest:
    def __init__(self, arena: Arena, location: list[float]) -> None:
        self.arena = arena
        self.location = self.get_location(arena, location)
        self.bots = {}
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
        # bot_interface = BotInterface(bot, self.location)
        bot_interface = BotInterface(bot, [0.4, 0.4]) # debug
        self.bots[id] = bot_interface

    def generate_bot_id(self):
        return len(self.bots) - 1