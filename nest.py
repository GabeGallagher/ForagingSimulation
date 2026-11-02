from arena import Arena
import random
from colliders.boundary_collider import BoundaryCollider
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
        self.arena: Arena = arena
        self.location: list[float] = self.get_location(arena, location)
        self.bots: Dict[int, BotInterface] = {}
        self.target_tracker: int = 0
        self.nav_type: NavType = nav_type
        self.nav: Navigation = self.get_navigator()
        self.next_bot_id: int = 0
        self.radius: float = 0.1
        self.spawn_margin: float = 0.01
        self.stuck_window: int = 40
        self.stuck_distance: float = 0.02
        self.instantiate_bot()
        self.collider: Collider = Collider(self.radius, self.location, self)
        self.inventory: list = []
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
        id: int = self.generate_bot_id()
        bot: MicroBot = MicroBot(id)
        from interfaces.bot_interface import BotInterface

        if id in self.bots:
            raise RuntimeError(f"Bot id {id} already in use; refusing to overwrite")

        spawn_location: list[float] = self.get_spawn_location(bot.length / 2)
        bot_interface: BotInterface = BotInterface(
            bot, self, spawn_location, self.arena
        )
        self.bots[id] = bot_interface
        bot.set_bot_interface(bot_interface)
        self.bot_move_command(id, bot_interface)

    """Scans outward from the nest's center in rings spaced one bot radius
    apart, out to the nest's radius, and returns the first point where the
    bot is clear of every obstacle and inside the arena. The first ring is
    just the center, so an unobstructed nest spawns bots at its center."""

    def get_spawn_location(self, bot_radius: float) -> list[float]:
        clearance: float = bot_radius + self.spawn_margin
        ring_count: int = int(self.radius / bot_radius)

        for ring in range(ring_count + 1):
            ring_radius: float = ring * bot_radius
            sample_count: int = max(1, math.ceil(2 * math.pi * ring_radius / bot_radius))

            for sample in range(sample_count):
                angle: float = 2 * math.pi * sample / sample_count
                point: list[float] = [
                    self.location[0] + ring_radius * math.sin(angle),
                    self.location[1] + ring_radius * math.cos(angle),
                ]
                if self.is_valid_spawn(point, clearance):
                    return point

        raise RuntimeError(
            f"No obstacle-free spawn point within {self.radius}m of nest at {self.location}"
        )

    def is_valid_spawn(self, point: list[float], clearance: float) -> bool:
        if not (clearance <= point[0] <= self.arena.x - clearance):
            return False
        if not (clearance <= point[1] <= self.arena.y - clearance):
            return False

        for obs in self.arena.obstacles:
            if math.dist(point, obs.position) < obs.radius + clearance:
                return False

        return True

    """Bot ids are drawn from a monotonic counter, never reused. Reusing ids
    (e.g. len(self.bots)) collides after destroy_bot pops from the dict, which
    silently overwrites a live bot in self.bots while leaving it subscribed to
    the SimulationManager and registered with the CollisionManager."""

    def generate_bot_id(self) -> int:
        bot_id: int = self.next_bot_id
        self.next_bot_id += 1
        return bot_id

    def get_navigator(self) -> Navigation:
        match self.nav_type:
            case NavType.POTENTIAL_FIELD:
                return PotentialField(self.arena)
            case NavType.BASIC:
                return BasicNavigation(self.arena)
            case _:
                print(f"{self.nav_type}")
                raise RuntimeError(f"Invalid or unimplemented navigation type")

    def get_target(self, bot_id: int) -> list[float]:
        bot: MicroBot = self.bots[bot_id].bot
        target_loc: list[float] = []

        if len(bot.inventory) > 0:
            bot.state = BotState.RETURNING

        match bot.state:
            case BotState.IDLE | BotState.EXPLORING:
                assigned_target = self.get_assigned_target(self.bots[bot_id])
                if assigned_target is None:
                    return bot.interface.location
                target_loc = assigned_target
            case BotState.RETURNING:
                target_loc = self.location
            case _:
                print(f"{bot.state}")
                raise RuntimeError(
                    "Invalid bot state. Cannot select navigation priority"
                )
            
        return target_loc

    """Each bot is assigned one target, round-robin across bots, the first time
    it needs one, and keeps it for the rest of its life. The tracker only
    advances on assignment, never on re-steering or collisions."""

    def get_assigned_target(self, bot_interface: "BotInterface") -> list[float] | None:
        if bot_interface.assigned_target is None and len(self.arena.target_locations) > 0:
            bot_interface.assigned_target = self.arena.target_locations[self.target_tracker]
            self.set_target_tracker()
        return bot_interface.assigned_target

    def bot_move_command(self, bot_id: int, bot_interface: "BotInterface") -> None:
        bot: MicroBot = self.bots[bot_id].bot

        match self.nav_type:
            case NavType.POTENTIAL_FIELD:
                target = self.get_target(bot_id)
                self.nav.set_target(target)
                rotation = self.nav.get_bot_direction(bot_interface, self.is_stuck(bot_interface))
                bot.rotate(rotation)
                if bot.state == BotState.IDLE:
                    bot.set_state(BotState.EXPLORING)
                bot_interface.debug_target = target
                # print(
                #     f"bot_{bot_id} moving at angle {bot_angle_to_target} radians and {math.degrees(bot_angle_to_target)} degrees thanks to potential field algo"
                # )
            case NavType.BASIC:
                self.basic_movement(bot_id)
            case _:
                raise RuntimeError(
                    f"Invalid or unimplemented navigation type: {self.nav_type}"
                )

    """A bot is stuck when its net movement over the last stuck_window
    updates is under stuck_distance"""

    def is_stuck(self, bot_interface: "BotInterface") -> bool:
        positions = bot_interface.recent_positions
        return (
            len(positions) == self.stuck_window
            and math.dist(positions[0], positions[-1]) < self.stuck_distance
        )

    def record_position(self, bot_interface: "BotInterface") -> None:
        positions = bot_interface.recent_positions
        positions.append(bot_interface.location.copy())
        if len(positions) > self.stuck_window:
            positions.popleft()

    def end_boundary_follow(self, bot_interface: "BotInterface") -> None:
        bot_interface.follow = None
        bot_interface.recent_positions.clear()

    def basic_movement(self, bot_id: int) -> None:
        bot: MicroBot = self.bots[bot_id].bot

        assigned_target = self.get_assigned_target(self.bots[bot_id])
        if assigned_target is None:
            return

        bot_angle_to_target = self.get_new_bot_orientation(bot_id, assigned_target)
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
        if isinstance(other, BoundaryCollider):
            # print(f"Bot {bot_id} collided with arena wall at {location}")
            self.bot_move_command(bot_id, bot.interface)
            return

        if isinstance(other, ObstacleCollider):
            # print(f"Bot {bot_id} collided with obstacle at {location}")
            self.bot_move_command(bot_id, bot.interface)
            return

        # Handle other collisions
        # print(f"Collided with {other.owner.__class__.__name__} at {other.position}")
        if isinstance(other.owner, Target):
            bot.collect_object(other.owner)

        elif isinstance(other.owner, Nest):
            self.transfer_bot_inventory(bot_id)
            self.destroy_bot(bot_id)

        elif isinstance(other.owner, MicroBot):
            # TODO: Implement better collision handling with other bots
            self.bot_move_command(bot_id, bot.interface)

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

    def destroy_bot(self, bot_id: int) -> None:
        if bot_id not in self.bots.keys():
            print(f"{bot_id} not in nest's bot dict")
        else:
            bot: MicroBot = self.bots[bot_id].bot
            self.bots.pop(bot_id)
            bot.destroy_self()

    def update(self, time_delta: float) -> None:
        for bot_id, bot_interface in self.bots.items():
            self.record_position(bot_interface)
            self.bot_move_command(bot_id, bot_interface)
