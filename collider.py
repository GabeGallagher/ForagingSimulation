from collision_manager import CollisionManager

class Collider:
    def __init__(self, radius, position):
        self.radius = radius
        self.position = position

        manager = CollisionManager.get_instance()
        if manager is not None:
            manager.register_collider(self)
        else:
            raise RuntimeError("CollisionManager instance not found.")

    def on_collision(self, other):
        print(f"Target at {self.position} colliding with {other}")
