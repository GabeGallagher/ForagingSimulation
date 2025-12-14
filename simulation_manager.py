from arena import Arena
from nest import Nest
import matplotlib.pyplot as plt
from visualization_manager import VisualizationManager
from matplotlib.animation import FuncAnimation


def animate_simulation(arena: Arena, nest: Nest, fig, ax, viz: VisualizationManager):
    anim = FuncAnimation(fig, viz.update_frame, fargs=(fig, ax, arena, nest))
    plt.show()
    return anim


"""Initializes simulation and runs separately from simulated components"""

if __name__ == "__main__":
    target_locations = [[0.8, 0.8]]
    arena = Arena([1, 1], target_locations)
    nest = Nest(arena, [0.2, 0.2])
    fig, ax = plt.subplots(figsize=(10, 10))
    viz = VisualizationManager(fig, ax)
    animate_simulation(arena, nest, fig, ax, viz)
