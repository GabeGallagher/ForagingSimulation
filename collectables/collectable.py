class Collectable:
    def __init__(self):
        self.iscollected: bool = False

    def collect(self) -> None:
        self.iscollected = True