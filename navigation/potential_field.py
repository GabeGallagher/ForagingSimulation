from arena import Arena
from colliders.obstacle_collider import ObstacleCollider
from navigation.boundary_follow import BoundaryFollow
from navigation.navigation import Navigation
import math
import numpy as np
from numpy.typing import NDArray
from microbot import MicroBot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interfaces.bot_interface import BotInterface


class PotentialField(Navigation):
    def __init__(self, arena: Arena) -> None:
        super().__init__()
        self.arena = arena
        self.attractive_strength = 0.2
        self.influence_dist = 0.2
        self.beta = 1
        self.eta = 1e-4
        self.circulation = 1.0
        self.follow_standoff = 0.025
        self.follow_leave_margin = 0.05
        self.calc_walls = True # Test code, delete on release

    def set_target(self, target_loc: list[float]) -> None:
        self.target: list[float] = target_loc

    def get_direction(self, bot_position: list[float], bot_rotation: float) -> float:
        theta_target = np.arctan2(self.target[0] - bot_position[0], self.target[1] - bot_position[1])

        attraction = self.attractive_strength * np.array([np.sin(theta_target), np.cos(theta_target)])
        repulsion = np.zeros(2)
        circulation = np.zeros(2)
        walls = np.zeros(2)

        escape = np.zeros(2)
        inside_obstacle = False

        for obs in self.arena.obstacles:
            d_obs = np.linalg.norm(np.array(obs.position) - np.array(bot_position))
            theta_obs = np.arctan2(obs.x - bot_position[0], obs.y - bot_position[1])
            d_surface = d_obs - obs.radius

            if d_surface <= 0:
                inside_obstacle = True
                escape -= np.array([np.sin(theta_obs), np.cos(theta_obs)])
            elif d_surface < self.influence_dist:
                strength = self.eta * (1 / d_surface - 1 / self.influence_dist) / d_surface**2
                repulsion -= strength * np.array([np.sin(theta_obs), np.cos(theta_obs)])

                side = self.get_circulation_side(theta_target, theta_obs)
                circulation += self.circulation * strength * side * np.array([np.cos(theta_obs), -np.sin(theta_obs)])

        if inside_obstacle:
            self.last_forces = {"escape": escape}
            return np.arctan2(escape[0], escape[1])

        if self.calc_walls: # Calc walls is test code. Remove once thoroughly tested
            d_left = bot_position[0]
            d_right = self.arena.x - bot_position[0]
            d_bottom = bot_position[1]
            d_top = self.arena.y - bot_position[1]

            if d_left < self.influence_dist:
                walls[0] += self.beta * (self.influence_dist - d_left)
            if d_right < self.influence_dist:
                walls[0] -= self.beta * (self.influence_dist - d_right)
            if d_bottom < self.influence_dist:
                walls[1] += self.beta * (self.influence_dist - d_bottom)
            if d_top < self.influence_dist:
                walls[1] -= self.beta * (self.influence_dist - d_top)

        self.last_forces = {
            "attraction": attraction,
            "repulsion": repulsion,
            "circulation": circulation,
            "walls": walls,
        }
        total = attraction + repulsion + circulation + walls
        rotation: float = np.arctan2(total[0], total[1])

        return rotation

    """Steers with the potential field until the nest reports the bot as stuck,
    then follows the nearest obstacle's boundary (Bug-style) until the bot is
    follow_leave_margin closer to its target than where it got stuck. If
    following runs into an arena wall the bot reverses once; a second wall
    ends the follow and hands the bot back to the field."""

    def get_bot_direction(self, bot_interface: "BotInterface", stuck: bool) -> float:
        location: list[float] = bot_interface.location
        orientation: float = bot_interface.bot.orientation

        if bot_interface.follow is None and stuck:
            side = self.get_follow_side(location)
            if side is not None:
                bot_interface.follow = BoundaryFollow(
                    side, self.target, math.dist(location, self.target)
                )

        follow = bot_interface.follow
        if follow is not None:
            progressed: bool = (
                math.dist(location, self.target) < follow.hit_dist - self.follow_leave_margin
            )
            if follow.target != self.target or progressed:
                bot_interface.nest.end_boundary_follow(bot_interface)
            else:
                rotation = self.get_follow_direction(location, orientation, follow.side)
                if (
                    rotation is not None
                    and self.heads_into_wall(location, rotation)
                    and not follow.reversed
                ):
                    follow.side = -follow.side
                    follow.reversed = True
                    rotation = self.get_follow_direction(location, orientation, follow.side)

                if rotation is None or self.heads_into_wall(location, rotation):
                    bot_interface.nest.end_boundary_follow(bot_interface)
                else:
                    return rotation

        return self.get_direction(location, orientation)

    """Which way to circle an obstacle: around the side facing the target.
    Exactly collinear bot, obstacle, and target ties to 1.0"""

    def get_circulation_side(self, theta_target: float, theta_obs: float) -> float:
        return 1.0 if np.sin(theta_target - theta_obs) >= 0 else -1.0

    def get_nearest_obstacle(self, bot_position: list[float]) -> tuple[ObstacleCollider | None, float]:
        nearest: ObstacleCollider | None = None
        nearest_surface: float = np.inf

        for obs in self.arena.obstacles:
            d_surface = np.linalg.norm(np.array(obs.position) - np.array(bot_position)) - obs.radius
            if d_surface < nearest_surface:
                nearest = obs
                nearest_surface = d_surface

        return nearest, nearest_surface

    def get_follow_side(self, bot_position: list[float]) -> float | None:
        nearest, d_surface = self.get_nearest_obstacle(bot_position)
        if nearest is None or d_surface > self.influence_dist:
            return None

        theta_target = np.arctan2(self.target[0] - bot_position[0], self.target[1] - bot_position[1])
        theta_obs = np.arctan2(nearest.x - bot_position[0], nearest.y - bot_position[1])
        return self.get_circulation_side(theta_target, theta_obs)

    """Heading that tracks the nearest obstacle's boundary at follow_standoff,
    moving around it in the direction of side. Returns None when no obstacle is
    within influence_dist to follow"""

    def get_follow_direction(self, bot_position: list[float], bot_rotation: float, side: float) -> float | None:
        nearest, d_surface = self.get_nearest_obstacle(bot_position)
        if nearest is None or d_surface > self.influence_dist:
            return None
        if d_surface <= 0:
            return self.get_direction(bot_position, bot_rotation)

        theta_obs = np.arctan2(nearest.x - bot_position[0], nearest.y - bot_position[1])
        correction = np.clip((self.follow_standoff - d_surface) / self.follow_standoff, -1.0, 1.0)

        dx = side * np.cos(theta_obs) - correction * np.sin(theta_obs)
        dy = -side * np.sin(theta_obs) - correction * np.cos(theta_obs)
        self.last_forces = {"follow": np.array([dx, dy])}
        return np.arctan2(dx, dy)

    def heads_into_wall(self, bot_position: list[float], rotation: float) -> bool:
        dx = np.sin(rotation)
        dy = np.cos(rotation)

        return (
            (bot_position[0] < self.follow_standoff and dx < 0)
            or (bot_position[0] > self.arena.x - self.follow_standoff and dx > 0)
            or (bot_position[1] < self.follow_standoff and dy < 0)
            or (bot_position[1] > self.arena.y - self.follow_standoff and dy > 0)
        )
