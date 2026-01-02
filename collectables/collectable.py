class Collectable:
    def __init__(self):
        self.iscollected = False

    def collect(self) -> None:
        self.iscollected = True