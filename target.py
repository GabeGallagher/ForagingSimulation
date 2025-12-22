from collider import Collider


class Target():
    def __init__(self, radius, position):
        self.position: list[float] = position
        self.collider: Collider = Collider(radius, position)
        
