"""Area or Arena in which the simulation takes place"""

from collectables.target import Target


class Arena:
    # dimensions: list[float] of arena x/y in meters
    def __init__(self, dimensions, target_locations: list[list[float]]) -> None:
        self._x: float = dimensions[0]
        self._y: float = dimensions[1]
        self.target_locations: list[list[float]] = target_locations
        self.targets: list[Target] = []

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
            target = Target(radius=0.1, position=target_location)
            self.targets.append(target)
    