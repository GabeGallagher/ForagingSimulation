from arena import Arena
from matplotlib.axes import Axes

"""Visualize simulation"""
class VisualizationManager:
    def __init__(self, fig, ax:Axes, arena: Arena) -> None:
        self.ax = ax
        self.arena = arena

    def draw_arena(self):
        self.ax.set_xlim(0, self.arena.x)
        self.ax.set_ylim(0, self.arena.y)
        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.set_aspect("equal")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)