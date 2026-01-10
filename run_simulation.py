from simulation_manager import SimulationManager
from arena import Arena
from nest import Nest
from enums.navigation_type import NavType

"""Initializes simulation and runs separately from simulated components"""

if __name__ == "__main__":
    time_delta = 0.05  # 50ms
    framerate = 20
    target_locations = [[0.8, 0.8], [0.7, 0.8], [0.8, 0.7]]
    obstacle_locations = [[0.5, 0.5]]
    arena = Arena([1, 1], target_locations, obstacle_locations)
    arena_size = [10, 10]
    headless = False
    nav_type = NavType.POTENTIAL_FIELD

    sim: SimulationManager = SimulationManager(
        time_delta, target_locations, obstacle_locations, arena, arena_size, headless
    )
    
    # Nest must init after sim manager
    nest: Nest = Nest(arena, [0.2, 0.2], nav_type)

    sim.run_realtime_loop()

    if headless:
        pass
    else:
        sim.set_visualization_manager(framerate, nest)
        sim.viz.animate_simulation()
        sim.stop()

