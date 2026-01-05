from arena import Arena
from nest import Nest
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from visualization_manager import VisualizationManager
from typing import List, Optional
import time
from time_step_observer import TimeStepObserver
import threading
from threading import Thread
from collision_manager import CollisionManager


class SimulationManager:
    _instance: Optional["SimulationManager"] = None

    def __new__(cls, *args, **kwargs) -> "SimulationManager":
        if cls._instance is None:
            cls._instance = super(SimulationManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        td: float,
        target_locations: list[list[float]],
        obstacle_locations: list[list[float]],
        arena: Arena,
        arena_size: list[int],
        headless=True,
    ) -> None:
        if self._initialized:
            return

        # Initialize observers list FIRST, before anything else
        self.observers: List[TimeStepObserver] = []
        # Collision manager must be initialized before any possible colliders
        self.collision_manager: CollisionManager = CollisionManager()

        self.time_delta: float = td
        self.target_locations: list[list[float]] = target_locations
        self.obstacle_locations: list[list[float]] = obstacle_locations
        self.arena: Arena = arena
        self.arena.instantiate_targets()
        self.arena.instantiate_obstacles()
        self.headless = headless
        self.fig, self.ax = plt.subplots(figsize=(arena_size[0], arena_size[1]))
        self.current_time: float = 0.0

        self._initialized = True

    @classmethod
    def get_instance(cls) -> Optional["SimulationManager"]:
        return cls._instance

    def subscribe(self, observer: TimeStepObserver):
        if observer not in self.observers:
            self.observers.append(observer)

    def unsubscribe(self, observer: TimeStepObserver) -> None:
        if observer in self.observers:
            self.observers.remove(observer)

    def set_visualization_manager(self, framerate: int, nest: Nest) -> None:
        self.viz = VisualizationManager(framerate, self.fig, self.ax, self.arena, nest)


    def get_interval_miliseconds(self, time_delta) -> int:
        return int(1000 * time_delta)

    def run_realtime_loop(self) -> None:
        self.running = True

        def loop():
            last_time = time.time()

            while self.running:
                current_time = time.time()
                elapsed = current_time - last_time

                while elapsed >= self.time_delta:
                    self.step()
                    elapsed -= self.time_delta
                    last_time += self.time_delta

                # Sleep to prevent busy waiting
                time.sleep(0.001)  # 1ms sleep
        
        self.sim_thread: Thread = threading.Thread(target=loop, daemon=True)
        self.sim_thread.start()

    def stop(self) -> None:
        self.running = False

    def step(self) -> None:
        self.current_time += self.time_delta

        for observer in self.observers:
            try:
                observer.update(self.time_delta)
            except Exception as e:
                pass
                # TODO: figure out why this is called every frame and fix
                # UPDATE: I believe this is happening because there are errors that are failing silently
                # print(f"Error updating observer {observer}: {e}")
