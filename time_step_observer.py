


class TimeStepObserver:
    """Protocol for objects that need to update each time step"""

    def __init__(self) -> None:
        super().__init__()
        from simulation_manager import SimulationManager
        sim_manager = SimulationManager.get_instance()
        if sim_manager is not None:
            sim_manager.subscribe(self)

    def update(self, time_delta: float) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement update(time_delta) method"
        )
