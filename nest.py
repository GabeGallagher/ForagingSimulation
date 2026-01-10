from arena import Arena
import random
from colliders.collider import Collider
from colliders.obstacle_collider import ObstacleCollider
from enums.navigation_type import NavType
from microbot import MicroBot
from enums.bot_state import BotState
from typing import Dict
import math
from collectables.target import Target
from navigation.basic import BasicNavigation
from navigation.navigation import Navigation
from navigation.potential_field import PotentialField
from time_step_observer import TimeStepObserver
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interfaces.bot_interface import BotInterface


"""Creates micro bots, receives their signals, and controls behavior"""


class Nest(TimeStepObserver):
    def __init__(self, arena: Arena, location: list[float], nav_type: NavType) -> None:
        super().__init__()
        self.arena = arena
        self.location = self.get_location(arena, location)
        self.bots: Dict[int, BotInterface] = {}
        self.target_tracker: int = 0
        self.nav_type = nav_type
        self.nav = self.get_navigator()
        self.instantiate_bot()
        self.collider: Collider = Collider(0.1, self.location, self)
        self.inventory = []
        self.time_since_last_spawn: float = 0.0

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

        bot_interface = BotInterface(bot, self, self.location.copy(), self.arena)
        self.bots[id] = bot_interface
        bot.set_bot_interface(bot_interface)
        self.bot_move_command(id)

    # TODO: look into better ways to generate unique id
    def generate_bot_id(self) -> int:
        return len(self.bots) - 1
    
    def get_navigator(self) -> Navigation:
        match self.nav_type:
            case NavType.POTENTIAL_FIELD:
                return PotentialField(self.arena)
            case NavType.BASIC:
                return BasicNavigation(self.arena)
            case _:
                raise RuntimeError(f"Invalid or unimplemented navigation type: {self.nav_type}")


    def bot_move_command(self, bot_id) -> None:
        match self.nav_type:
            case NavType.POTENTIAL_FIELD:
                self.nav.move()
            case NavType.BASIC:
                self.basic_movement(bot_id)
            case _:
                raise RuntimeError(f"Invalid or unimplemented navigation type: {self.nav_type}")

    def basic_movement(self, bot_id: int) -> None:
        bot: MicroBot = self.bots[bot_id].bot

        if len(self.arena.targets) == 0:
            return

        try:
            bot_angle_to_target = self.get_new_bot_orientation(
                bot_id, self.arena.targets[self.target_tracker].position
            )
        except:
            target_count: int = len(self.arena.targets)
            if target_count == 0:
                # TODO: implement destroy bot
                return
            else:
                bot_angle_to_target = self.get_new_bot_orientation(
                    bot_id, self.arena.targets[0].position
                )

        self.set_target_tracker()
        bot.rotate(
            bot_angle_to_target
        )  # calculate bot orientation and rotate relative to target
        bot.set_state(BotState.EXPLORING)


    def set_target_tracker(self) -> None:
        self.target_tracker += 1
        if self.target_tracker > len(self.arena.targets) - 1:
            self.target_tracker = 0

    def get_new_bot_orientation(self, bot_id, target_location: list[float]) -> float:
        bot: MicroBot = self.bots[bot_id].bot
        bot_location = self.bots[bot_id].location
        dx = target_location[0] - bot_location[0]
        dy = target_location[1] - bot_location[1]
        return math.atan2(dx, dy)

    def handle_collision(self, other, location: list[float], bot_id: int) -> None:
        bot: MicroBot = self.bots[bot_id].bot

        # Handle wall collision
        if isinstance(other, Arena):
            print(f"Bot {bot_id} collided with arena wall at {location}")
            self.bot_move_to_random(bot_id)
            return

        if isinstance(other, ObstacleCollider):
            print(f"Bot {bot_id} collided with obstacle at {location}")
            self.bot_move_to_random(bot_id)
            return

        # Handle other collisions
        print(f"Collided with {other.owner.__class__.__name__} at {other.position}")
        if isinstance(other.owner, Target):
            bot.collect_object(other.owner)

        elif isinstance(other.owner, Nest):
            self.transfer_bot_inventory(bot_id)

        elif isinstance(other.owner, MicroBot):
            # TODO: Implement better collision handling with other bots
            self.bot_move_to_random(bot_id)

    def transfer_bot_inventory(self, bot_id) -> None:
        bot: MicroBot = self.bots[bot_id].bot
        self.inventory.extend(bot.inventory)
        bot.inventory.clear()

    def handle_collection(self, bot_id: int, obj) -> None:
        if isinstance(obj, Target):
            self.bot_return_command(bot_id)

    def bot_return_command(self, bot_id: int) -> None:
        bot: MicroBot = self.bots[bot_id].bot
        bot_angle_to_nest: float = self.get_new_bot_orientation(bot_id, self.location)
        bot.rotate(bot_angle_to_nest)
        bot.set_state(BotState.RETURNING)

    def bot_move_to_random(self, bot_id: int) -> None:
        bot: MicroBot = self.bots[bot_id].bot
        ran_x: float = random.random()
        ran_y: float = random.random()
        bot_random_angle: float = self.get_new_bot_orientation(bot_id, [ran_x, ran_y])
        bot.rotate(bot_random_angle)
        bot.set_state(BotState.EXPLORING)

    def update(self, time_delta: float) -> None:
        pass
