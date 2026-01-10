from abc import ABC, abstractmethod

class Navigation(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def move(self) -> None:
        pass