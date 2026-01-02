from collision_manager import CollisionManager

class Collider:
    def __init__(self, radius, position, owner=None) -> None:
        self.radius = radius
        self.position = position
        self.owner = owner

        self.manager: CollisionManager | None = CollisionManager.get_instance()
        if self.manager is not None:
            self.manager.register_collider(self)
        else:
            raise RuntimeError("CollisionManager instance not found.")

    def on_collision(self, other) -> None:
        from collectables.target import Target
        if isinstance(other.owner, Target) and self.owner is not None:
            print(f"Collider owned by {self.owner} collided with Target at {other.position}")

    def destroy(self) -> None:
        if self.manager is not None:
            self.manager.remove_collider(self)
            self = None
        else:
            raise RuntimeError("CollisionManager instance not found in destroy function")
