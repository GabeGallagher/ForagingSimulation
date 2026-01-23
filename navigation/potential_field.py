from arena import Arena
from navigation.navigation import Navigation
import numpy as np
from numpy.typing import NDArray
from typing import TYPE_CHECKING


class PotentialField(Navigation):
    def __init__(self, arena: Arena) -> None:
        super().__init__()
        self.arena = arena
        self.k_att = 1.0
        self.k_rep = 2.0
        self.influence_dist = 0.2

    def set_target(self, target_loc: list[float]) -> None:
        self.target: list[float] = target_loc

    def get_direction(self, bot_position: list[float]) -> NDArray:
        print("Potential field Nav active")
        # Calculate attractive force to target
        pos = np.array(bot_position)
        goal = np.array(self.target)
        to_goal = goal - pos
        attractive_force = self.k_att * to_goal

        # Calculate repulsive force from obstacles
        repulsive_force = np.zeros(2)

        for obs in self.arena.obstacles:
            to_robot = pos - np.array(obs.position)
            dist_to_obs_surface = np.linalg.norm(to_robot) - obs.radius

            if dist_to_obs_surface <= self.influence_dist:
                print(f"influenced by obstacle at: {obs.position}")
                repulsive_direction = to_robot / np.linalg.norm(to_robot)
                magnitude = (
                    self.k_rep
                    * (1 / self.influence_dist - 1 / dist_to_obs_surface)
                    * (1 / dist_to_obs_surface**2)
                )
                repulsive_force += magnitude * repulsive_direction

        # Calculate repulsive force from walls
        distances = {
            "top": self.arena.y - pos[1],
            "right": self.arena.x - pos[0],
            "bot": pos[1],
            "left": pos[0],
        }

        directions = {
            "top": np.array([0, -1]),
            "right": np.array([-1, 0]),
            "bot": np.array([0, 1]),
            "left": np.array([1, 0]),
        }

        # for wall, dist_to_obs_surface in distances.items():
        #     if (
        #         dist_to_obs_surface < self.influence_dist
        #         and dist_to_obs_surface > 0.001
        #     ):
        #         magnitude = (
        #             self.k_rep
        #             * (1 / dist_to_obs_surface - 1 / self.influence_dist)
        #             * (1 / dist_to_obs_surface**2)
        #         )
        #         repulsive_force += magnitude * directions[wall]

        total_force = attractive_force + repulsive_force

        if np.linalg.norm(total_force) > 0.001:
            return total_force
        else:
            return np.zeros(2)
