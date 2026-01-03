from __future__ import annotations
from typing import TYPE_CHECKING
from colliders.collider import Collider
from collectables.target import Target
from enums.bot_state import BotState

if TYPE_CHECKING:
    from microbot import MicroBot


class MicroBotCollider(Collider):
    def __init__(self, radius: float, position: list[float], owner: MicroBot) -> None:
        super().__init__(radius, position, owner)
        self.microbot: MicroBot = owner

    def on_collision(self, other: Collider) -> None:
        from nest import Nest
        if isinstance(other.owner, Nest):
            if self.microbot.state == BotState.RETURNING:
                self.microbot.handle_collision(other)
        else:
            self.microbot.handle_collision(other)
