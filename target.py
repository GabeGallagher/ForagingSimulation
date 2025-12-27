from colliders.collider import Collider


class Target():
    def __init__(self, radius, position):
        self.position: list[float] = position
        self.collider: Collider = Collider(radius, position, self)

    def collect(self) -> None:
        print(f"Target at position {self.position} collected.")
        
