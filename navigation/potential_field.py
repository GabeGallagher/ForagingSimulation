from arena import Arena
from navigation.navigation import Navigation


class PotentialField(Navigation):
    def __init__(self, arena: Arena) -> None:
        super().__init__()

    def move(self) -> None:
        print("Potential field Nav active")
