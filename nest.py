from arena import Arena
import random
from microbot import MicroBot
from enums.bot_state import BotState
from typing import Dict
import math
from collectables.target import Target
from time_step_observer import TimeStepObserver
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interfaces.bot_interface import BotInterface


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

    def instantiate_bot(self) -> None:
        id = self.generate_bot_id()
        bot = MicroBot(id)
        from interfaces.bot_interface import BotInterface

        bot_interface = BotInterface(bot, self, self.location.copy())
        self.bots[id] = bot_interface
        bot.set_bot_interface(bot_interface)
        self.bot_move_command(id)

    # TODO: look into better ways to generate unique id
    def generate_bot_id(self) -> int:
        return len(self.bots) - 1

    def bot_move_command(self, bot_id) -> None:
        bot: MicroBot = self.bots[bot_id].bot
        # TODO: refactor this to handle arenas with multiple targets. Works for now because there will always just be one
        bot_angle_to_target = self.get_new_bot_orientation(
            bot_id, self.arena.targets[0].position
        )
        bot.rotate(
            bot_angle_to_target
        )  # calculate bot orientation and rotate relative to target
        bot.set_state(BotState.EXPLORING)

    def get_new_bot_orientation(self, bot_id, target_location: list[float]) -> float:
        bot: MicroBot = self.bots[bot_id].bot
        bot_location = self.bots[bot_id].location
        dx = target_location[0] - bot_location[0]
        dy = target_location[1] - bot_location[1]
        return math.atan2(dx, dy)

    def handle_collision(self, other, location: list[float], bot_id: int) -> None:
        if isinstance(other.owner, Target):
            print(f"Collided with {other.owner.__class__.__name__} at {other.position}")
            bot: MicroBot = self.bots[bot_id].bot
            bot.collect_object(other.owner)

    def handle_collection(self, bot_id: int, obj) -> None:
        if isinstance(obj, Target):
            self.bot_return_command(bot_id)

    def bot_return_command(self, bot_id: int) -> None:
        bot: MicroBot = self.bots[bot_id].bot
        bot_angle_to_nest: float = self.get_new_bot_orientation(bot_id, self.location)
        bot.rotate(bot_angle_to_nest)
        bot.set_state(BotState.RETURNING)

    def update(self, time_delta: float) -> None:
        print(f"Bot location: {self.bots[0].x}, {self.bots[0].y}")
