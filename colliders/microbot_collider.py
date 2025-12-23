from __future__ import annotations
from typing import TYPE_CHECKING
from colliders.collider import Collider
from target import Target

if TYPE_CHECKING:
    from microbot import MicroBot

class MicroBotCollider(Collider):
    def __init__(self, radius: float, position: list[float], owner: MicroBot) -> None:
        super().__init__(radius, position, owner)
        self.microbot: MicroBot = owner

    def on_collision(self, other) -> None:
        if isinstance(other.owner, Target) and self.owner is not None:
            print(f"Collider owned by {self.microbot.id} collided with Target at {other.position}")
            # Handle collision with target (e.g., microbot collects the target)
            # if hasattr(self.owner, 'collect_target'):
            #     self.owner.collect_target(other.owner)