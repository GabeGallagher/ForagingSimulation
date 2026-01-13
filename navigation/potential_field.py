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
        self.k_rep = 5.0
        self.influence_dist = 2.0

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
        repulsive = np.zeros(2)

        for obs in self.arena.obstacles:
            to_robot = np.array(obs.position) - pos
            dist = np.linalg.norm(to_robot) - obs.radius

            if dist < self.influence_dist and dist > 0.0:
                print(f"influenced by obstacle at: {obs.position}")
                repulsion_magnitude = (
                    self.k_rep * (1 / dist - 1 / self.influence_dist) * (1 / dist**2)
                )
                repulsion_direction = to_robot / np.linalg.norm(to_robot)
                repulsive += repulsion_magnitude * repulsion_direction

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

        for wall, dist in distances.items():
            if dist < self.influence_dist and dist > 0.001:
                magnitude = (
                    self.k_rep * (1 / dist - 1 / self.influence_dist) * (1 / dist**2)
                )
                repulsive += magnitude * directions[wall]

        total_force = attractive_force + repulsive

        if np.linalg.norm(total_force) > 0.001:
            return total_force / np.linalg.norm(total_force)
        else:
            return np.zeros(2)
