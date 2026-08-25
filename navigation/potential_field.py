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
        self.beta = .75

    def set_target(self, target_loc: list[float]) -> None:
        self.target: list[float] = target_loc

    def get_direction(self, bot_position: list[float], bot_rotation: float) -> float:
        theta_target = np.arctan2(self.target[0] - bot_position[0], self.target[1] - bot_position[1])

        dx = self.attractive_strength * np.sin(theta_target)
        dy = self.attractive_strength * np.cos(theta_target)

        obs = self.arena.obstacles[0]
        d_obs = np.linalg.norm(np.array(obs.position) - np.array(bot_position))
        theta_obs = np.arctan2(obs.position[0] - bot_position[0], obs.position[1] - bot_position[1])

        if d_obs <= obs.radius:
            dx = np.sign(np.sin(theta_obs))
            dy = np.sign(np.cos(theta_obs))
        elif d_obs < obs.radius + self.influence_dist:
            dx += -self.beta * (self.influence_dist + obs.radius - d_obs) * np.sin(theta_obs)
            dy += -self.beta * (self.influence_dist + obs.radius - d_obs) * np.cos(theta_obs)

        rotation: float = np.arctan2(dx, dy)
        
        return rotation
