from arena import Arena
from navigation.navigation import Navigation
import numpy as np
from numpy.typing import NDArray
from microbot import MicroBot
from typing import TYPE_CHECKING


class PotentialField(Navigation):
    def __init__(self, arena: Arena) -> None:
        super().__init__()
        self.arena = arena
        self.attractive_strength = 0.2
        self.influence_dist = 0.2
        self.beta = 1
        self.eta = 1e-4
        self.calc_walls = True # Test code, delete on release

    def set_target(self, target_loc: list[float]) -> None:
        self.target: list[float] = target_loc

    def get_direction(self, bot_position: list[float], bot_rotation: float) -> float:
        theta_target = np.arctan2(self.target[0] - bot_position[0], self.target[1] - bot_position[1])

        dx = self.attractive_strength * np.sin(theta_target)
        dy = self.attractive_strength * np.cos(theta_target)

        escape_x = 0.0
        escape_y = 0.0
        inside_obstacle = False

        for obs in self.arena.obstacles:
            d_obs = np.linalg.norm(np.array(obs.position) - np.array(bot_position))
            theta_obs = np.arctan2(obs.x - bot_position[0], obs.y - bot_position[1])
            d_surface = d_obs - obs.radius

            if d_surface <= 0:
                inside_obstacle = True
                escape_x -= np.sin(theta_obs)
                escape_y -= np.cos(theta_obs)
            elif d_surface < self.influence_dist:
                repulsion = self.eta * (1 / d_surface - 1 / self.influence_dist) / d_surface**2
                dx -= repulsion * np.sin(theta_obs)
                dy -= repulsion * np.cos(theta_obs)

        if inside_obstacle:
            return np.arctan2(escape_x, escape_y)

        if self.calc_walls: # Calc walls is test code. Remove once thoroughly tested
            d_left = bot_position[0]
            d_right = self.arena.x - bot_position[0]
            d_bottom = bot_position[1]
            d_top = self.arena.y - bot_position[1]

            if d_left < self.influence_dist:
                dx += self.beta * (self.influence_dist - d_left)
            if d_right < self.influence_dist:
                dx -= self.beta * (self.influence_dist - d_right)
            if d_bottom < self.influence_dist:
                dy += self.beta * (self.influence_dist - d_bottom)
            if d_top < self.influence_dist:
                dy -= self.beta * (self.influence_dist - d_top)


        rotation: float = np.arctan2(dx, dy)
        
        return rotation
