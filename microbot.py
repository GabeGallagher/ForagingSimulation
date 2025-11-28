from enums.bot_state import BotState

class MicroBot:
    def __init__(self, id, length=1e-2) -> None:
        self.id = id
        self.length = length
        self.width = length / 3
        self.orientation = 0.0
        self.state = BotState.IDLE
        self.speed = 2e-1  # 20 cm/s - very fast microbot speed

    def rotate(self, angle_radians):
        self.orientation = angle_radians