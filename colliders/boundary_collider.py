from colliders.collider import Collider


"""The arena's outer walls as a single solid collider. Anything movable that
overlaps a wall is pushed back inside, so it can touch or slide along a wall
but never cross it. Nothing that moves needs to know where the walls are"""


class BoundaryCollider(Collider):
    def __init__(self, width: float, height: float, owner=None) -> None:
        super().__init__(0.0, [width / 2, height / 2], owner)
        self.width: float = width
        self.height: float = height

    def overlaps(self, other: Collider) -> bool:
        return (
            other.x - other.radius < 0
            or other.x + other.radius > self.width
            or other.y - other.radius < 0
            or other.y + other.radius > self.height
        )

    def on_collision(self, other: Collider) -> None:
        if not other.movable:
            return

        other.position[0] = min(max(other.x, other.radius), self.width - other.radius)
        other.position[1] = min(max(other.y, other.radius), self.height - other.radius)
