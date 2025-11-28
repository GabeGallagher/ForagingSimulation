"""Area or Arena in which the simulation takes place"""

class Arena:
    # dimensions: list[float] of arena x/y in meters
    def __init__(self, dimensions, targets: list[list[float]]) -> None:
        self._x = dimensions[0]
        self._y = dimensions[1]
        self.targets = targets

    @property
    def size(self):
        return self._x * self._y
    
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    