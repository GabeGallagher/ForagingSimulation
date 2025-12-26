from colliders.microbot_collider import MicroBotCollider
from enums.bot_state import BotState
import math
from time_step_observer import TimeStepObserver
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nest import BotInterface

"""Microbot behavior. Current parameters; microbots know ONLY their state
and orientation. They also will also eventually know when they hit something
and be able to relay simple information about what they've collided with to 
the brain"""


class MicroBot(TimeStepObserver):
    def __init__(self, id, length=1e-2) -> None:
        super().__init__()
        self.id = id
        self.length = length
        self.width = length / 3
        self.orientation = 0.0
        self.state = BotState.IDLE
        self.speed = 2e-1  # 20 cm/s - very fast microbot speed
        self.interface: BotInterface = None # Set by nest after instantiation

    def rotate(self, angle_radians):
        self.orientation = angle_radians

    def set_interface(self, interface) -> None:
        self.interface = interface
        self.collider: MicroBotCollider = self.set_collider()

    def set_state(self, state):
        self.state = state
        print(f"Bot: {self.id} changing to {self.state}")

    def move(self, time_delta: float) -> None:
        dx = self.speed * time_delta * math.sin(self.orientation)
        dy = self.speed * time_delta * math.cos(self.orientation)
        
        if self.interface != None:
            self.interface.set_location([dx, dy])

    def set_collider(self) -> MicroBotCollider:
        return MicroBotCollider(self.length / 2, self.interface.location, self)

    def handle_collision(self, other) -> None:
        self.interface.report_collision(other)
    
    def update(self, time_delta: float) -> None:
        match self.state:
            case BotState.EXPLORING:
                self.move(time_delta)
