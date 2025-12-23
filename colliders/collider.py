from collision_manager import CollisionManager

class Collider:
    def __init__(self, radius, position, owner=None):
        self.radius = radius
        self.position = position
        self.owner = owner

        manager = CollisionManager.get_instance()
        if manager is not None:
            manager.register_collider(self)
        else:
            raise RuntimeError("CollisionManager instance not found.")

    def on_collision(self, other):
        from target import Target
        if isinstance(other.owner, Target) and self.owner is not None:
            print(f"Collider owned by {self.owner} collided with Target at {other.position}")
            # Handle collision with target (e.g., microbot collects the target)
            # if hasattr(self.owner, 'collect_target'):
            #     self.owner.collect_target(other.owner)
