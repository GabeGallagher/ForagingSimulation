

from typing import Optional
from time_step_observer import TimeStepObserver


class CollisionManager(TimeStepObserver):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CollisionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.colliders = []

        self._initialized = True

    @classmethod
    def get_instance(cls) -> Optional["CollisionManager"]:
        return cls._instance

    def register_collider(self, collider) -> None:
        self.colliders.append(collider)

    def check_overlap(self, c1, c2) -> bool:
        dist_sq = (c1.position[0] - c2.position[0]) ** 2 + (c1.position[1] - c2.position[1]) ** 2
        radius_sum = c1.radius + c2.radius
        return dist_sq <= radius_sum ** 2

    def update(self, time_delta: float) -> None:
        for i in range(len(self.colliders)):
            for j in range(i + 1, len(self.colliders)):
                if self.check_overlap(self.colliders[i], self.colliders[j]):
                    self.colliders[i].on_collision(self.colliders[j])
                    self.colliders[j].on_collision(self.colliders[i])
