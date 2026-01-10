from arena import Arena
from navigation.navigation import Navigation


class BasicNavigation(Navigation):
    def __init__(self, arena: Arena) -> None:
        super().__init__()

    def move(self) -> None:
        pass
