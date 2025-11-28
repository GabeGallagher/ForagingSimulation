from arena import Arena
from nest import Nest
import matplotlib.pyplot as plt
from visualization_manager import VisualizationManager

"""Initializes simulation and runs separately from simulated components"""

if __name__ == "__main__":
    arena = Arena([1, 1], 1)
    nest = Nest(arena, [0.8, 0.8])
    fig, ax = plt.subplots(figsize=(10, 10))
    viz = VisualizationManager(fig, ax, arena)
    viz.draw_arena()
    plt.show()
