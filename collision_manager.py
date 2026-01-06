from typing import Optional, TYPE_CHECKING
from time_step_observer import TimeStepObserver

if TYPE_CHECKING:
    from colliders.collider import Collider


class CollisionManager(TimeStepObserver):
    _instance = None

    def __new__(cls, *args, **kwargs) -> "CollisionManager":
        if cls._instance is None:
            cls._instance = super(CollisionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        if self._initialized:
            return

        self.colliders: list[Collider] = []

        self._initialized = True

    @classmethod
    def get_instance(cls) -> Optional["CollisionManager"]:
        return cls._instance

    def register_collider(self, collider) -> None:
        self.colliders.append(collider)

    def remove_collider(self, collider) -> None:
        self.colliders.remove(collider)

    def check_overlap(self, c1, c2) -> bool:
        dist_sq = (c1.position[0] - c2.position[0]) ** 2 + (
            c1.position[1] - c2.position[1]
        ) ** 2
        radius_sum = c1.radius + c2.radius
        return dist_sq <= radius_sum**2

    def update(self, time_delta: float) -> None:
        # Create snapshot to avoid issues if colliders are removed during collision handling
        colliders_snapshot = self.colliders[:]
        for i in range(len(colliders_snapshot)):
            for j in range(i + 1, len(colliders_snapshot)):
                if self.check_overlap(colliders_snapshot[i], colliders_snapshot[j]):
                    colliders_snapshot[i].on_collision(colliders_snapshot[j])
                    colliders_snapshot[j].on_collision(colliders_snapshot[i])
