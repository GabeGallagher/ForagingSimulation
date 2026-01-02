from typing import Protocol, runtime_checkable

@runtime_checkable
class Collectable(Protocol):
    def collect(self) -> None: ...