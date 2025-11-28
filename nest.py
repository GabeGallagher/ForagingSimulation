from arena import Arena
import random

"""Creates micro bots, receives their signals, and controls behavior"""


class Nest:
    def __init__(self, arena: Arena, location: list[float]) -> None:
        self.arena = arena
        self.location = self.get_location(arena, location)

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
