from collectables.collectable import Collectable
from colliders.collider import Collider


class Target(Collectable):
    def __init__(self, radius, position) -> None:
        super().__init__()
        self.position: list[float] = position
        self.collider: Collider = Collider(radius, position, self)

    def collect(self) -> None:
        super().__init__()
        print(f"Target at position {self.position} collected.")
        
