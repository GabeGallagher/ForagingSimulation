

from colliders.collider import Collider


class ObstacleCollider(Collider):
    def __init__(self, radius:float, position: list[float], owner=None) -> None:
        super().__init__(radius, position, owner)