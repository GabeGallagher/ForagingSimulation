from simulation_manager import SimulationManager
from arena import Arena
from nest import Nest
from enums.navigation_type import NavType
import random

"""Initializes simulation and runs separately from simulated components"""

if __name__ == "__main__":
    time_delta = 0.05  # 50ms
    framerate = 20
    target_locations = [[0.8, 0.8]]
    obstacle_count = 5
    obstacle_specs = []

    # randomly gens obstacles. Doesn't account for overlap
    for i in range(obstacle_count):
        obs_x = random.uniform(0.2, 0.7)
        obs_y = random.uniform(0.2, 0.7)
        obs_r = random.uniform(0.025, 0.2)
        spec = [obs_x, obs_y, obs_r]
        obstacle_specs.append(spec)
    
    arena = Arena([1, 1], target_locations, obstacle_specs)
    arena_size = [10, 10]
    headless = False
    nav_type = NavType.POTENTIAL_FIELD

    sim: SimulationManager = SimulationManager(
        time_delta, target_locations, arena, arena_size, headless
    )
    
    # Nest must init after sim manager
    nest: Nest = Nest(arena, [0.1, 0.1], nav_type)

    sim.run_realtime_loop()

    if headless:
        for _ in range(400):
            sim.step()
    else:
        sim.set_visualization_manager(framerate, nest)
        sim.viz.animate_simulation()
        sim.stop()

