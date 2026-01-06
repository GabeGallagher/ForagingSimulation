"""Area or Arena in which the simulation takes place"""

from collectables.target import Target
from colliders.obstacle_collider import ObstacleCollider


class Arena:
    # dimensions: list[float] of arena x/y in meters
    def __init__(
        self,
        dimensions,
        target_locations: list[list[float]],
        obstacle_locations: list[list[float]],
    ) -> None:
        self._x: float = dimensions[0]
        self._y: float = dimensions[1]
        self.target_locations: list[list[float]] = target_locations
        self.targets: list[Target] = []
        self.obstacle_locations: list[list[float]] = obstacle_locations
        self.obstacles: list[ObstacleCollider] = []

    @property
    def size(self) -> float:
        return self._x * self._y

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def instantiate_targets(self) -> None:
        for target_location in self.target_locations:
            # TODO: Refactor to get radius from run_simulation
            target = Target(radius=0.05, position=target_location)
            self.targets.append(target)

    def instantiate_obstacles(self) -> None:
        for obstacle_location in self.obstacle_locations:
            obstacle: ObstacleCollider = ObstacleCollider(
                radius=0.1, position=obstacle_location, owner=None
            )
            self.obstacles.append(obstacle)
