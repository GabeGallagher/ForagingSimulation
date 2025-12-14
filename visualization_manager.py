import numpy as np
from arena import Arena
from nest import Nest
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
from matplotlib.transforms import Affine2D

"""Visualize simulation"""


class VisualizationManager:
    def __init__(self, fig, ax: Axes) -> None:
        self.ax = ax

    def draw_arena(self, arena: Arena):
        self.ax.set_xlim(0, arena.x)
        self.ax.set_ylim(0, arena.y)
        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.set_aspect("equal")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)

    def draw_nest(self, nest_loc: list[float]):
        if nest_loc is not None:
            self.ax.plot(
                nest_loc[0],
                nest_loc[1],
                "g*",
                markersize=20,
                label="Nest",
            )

    def draw_bots(self, nest: Nest):
        if len(nest.bots) > 0:
            for bot_id, ibot in nest.bots.items():
                length = ibot.bot.length
                width = ibot.bot.width
                orientation = ibot.bot.orientation
                print(
                    f"Expected bot orientation: {orientation} rad = {orientation * 180/np.pi:.1f}°"
                )
                print(f"Expected bot Location: {ibot.position}")

                # Convert orientation to degrees for matplotlib
                angle_deg = 90 - (orientation * 180 / np.pi)
                print(f"Matplotlib angle: {angle_deg:.1f}°")

                # Half dimensions
                half_length = length / 2
                half_width = width / 2

                # The center offset from bottom-left corner (before rotation)
                center_offset_x = half_length
                center_offset_y = half_width

                # After rotation, this offset becomes:
                angle_rad = np.radians(angle_deg)
                rotated_offset_x = center_offset_x * np.cos(
                    angle_rad
                ) - center_offset_y * np.sin(angle_rad)
                rotated_offset_y = center_offset_x * np.sin(
                    angle_rad
                ) + center_offset_y * np.cos(angle_rad)

                # So the bottom-left corner should be at:
                corner_x = ibot.x - rotated_offset_x
                corner_y = ibot.y - rotated_offset_y

                rect = Rectangle(
                    (corner_x, corner_y),
                    length,
                    width,
                    linewidth=1,
                    edgecolor="blue",
                    facecolor="lightblue",
                    alpha=0.7,
                    angle=angle_deg,  # Use the orientation directly in degrees
                )
                self.ax.add_patch(rect)

    def draw_targets(self, arena: Arena):
        if len(arena.targets) > 0:
            target_count = 1
            for target in arena.targets:
                self.ax.plot(
                    target[0],
                    target[1],
                    "r*",
                    markersize=10,
                    label="Target_" + str(target_count),
                )
                target_count += 1

    def visualize_simulation(self, arena: Arena, nest: Nest):
        self.draw_nest(nest.location)
        self.draw_bots(nest)
        self.draw_targets(arena)
        self.draw_arena(arena)

    def update_frame(self, frame, fig, ax: Axes, arena: Arena, nest: Nest):
        ax.clear()
        self.visualize_simulation(arena, nest)
        return []
