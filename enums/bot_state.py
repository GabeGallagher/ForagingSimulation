from enum import Enum


class BotState(Enum):
    IDLE = "idle"
    BLOCKED = "blocked"
    EXPLORING = "exploring"
    RETURNING = "returning"
