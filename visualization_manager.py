import numpy as np
from typing import Optional
from arena import Arena
from nest import Nest
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle, Circle
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import CheckButtons
import matplotlib.pyplot as plt
from enums.bot_state import BotState

"""Visualize simulation"""

STATE_COLORS = {
    BotState.IDLE: "lightgray",
    BotState.EXPLORING: "lightblue",
    BotState.RETURNING: "gold",
    BotState.BLOCKED: "salmon",
}


class VisualizationManager:
    def __init__(self, framerate: int, fig: Figure, ax: Axes, arena: Arena, nest: Nest, pause_callback) -> None:
        super().__init__()
        self.frametime = self.get_frametime_miliseconds(framerate)
        self.fig = fig
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.ax = ax
        self.elapsed: float = 0.0
        self.last_draw: float = 0.0
        self.arena = arena
        self.nest = nest
        self.pause_callback = pause_callback
        self.overlay_keys = ["force", "heading", "state", "target", "influence", "bot_locations"]
        self.overlay_labels = [
            "Force vectors",
            "Headings",
            "State colors",
            "Target lines",
            "Influence zones",
            "Show Bot Locations",
        ]
        self.overlays = {key: False for key in self.overlay_keys}
        self._build_overlay_controls()

    def _build_overlay_controls(self) -> None:
        check_ax = self.fig.add_axes((0.005, 0.7, 0.17, 0.26))
        check_ax.set_facecolor("whitesmoke")
        self.overlay_check = CheckButtons(
            check_ax, self.overlay_labels, list(self.overlays.values())
        )
        self.overlay_check.on_clicked(self._on_overlay_toggle)

    def _on_overlay_toggle(self, label: Optional[str]) -> None:
        if label is None:
            return
        key = self.overlay_keys[self.overlay_labels.index(label)]
        self.overlays[key] = not self.overlays[key]

    def get_frametime_miliseconds(self, framerate: int) -> int:
        return int(1000 / framerate)

    def draw_arena(self, arena: Arena) -> None:
        self.ax.set_xlim(0, arena.x)
        self.ax.set_ylim(0, arena.y)
        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.set_aspect("equal")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)

    def draw_nest(self, nest_loc: list[float]) -> None:
        if nest_loc is not None:
            self.ax.plot(
                nest_loc[0],
                nest_loc[1],
                "g*",
                markersize=20,
                label="Nest",
            )

    def draw_bots(self, nest: Nest) -> None:
        if len(nest.bots) > 0:
            for bot_id, ibot in nest.bots.items():
                length = ibot.bot.length
                width = ibot.bot.width
                orientation = ibot.bot.orientation

                # State-color overlay: tint the body by BotState, else default.
                if self.overlays["state"]:
                    facecolor = STATE_COLORS.get(ibot.bot.state, "lightblue")
                else:
                    facecolor = "lightblue"

                # Convert orientation to degrees for matplotlib
                angle_deg = 90 - (orientation * 180 / np.pi)

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
                    facecolor=facecolor,
                    alpha=0.7,
                    angle=angle_deg,  # Use the orientation directly in degrees
                )
                self.ax.add_patch(rect)

    def draw_targets(self, arena: Arena) -> None:
        self.ax.plot([], [], "r*", markersize=10, label="Target")
        if len(arena.targets) > 0:
            for target in arena.targets:
                if not target.iscollected:
                    self.ax.plot(
                        target.position[0],
                        target.position[1],
                        "r*",
                        markersize=10,
                    )

    def draw_obstacles(self, arena: Arena) -> None:
        self.ax.plot([], [], "o", color="gray", markersize=10, label="Obstacle")
        if len(arena.obstacles) > 0:
            for obstacle in arena.obstacles:
                circle = Circle(
                    (obstacle.position[0], obstacle.position[1]),
                    obstacle.radius,
                    facecolor="gray",
                    edgecolor="darkgray",
                    alpha=0.7,
                )
                self.ax.add_patch(circle)

    def draw_force_vectors(self, nest: Nest) -> None:
        for ibot in nest.bots.values():
            force = ibot.debug_force
            if force is None:
                continue
            magnitude = float(np.linalg.norm(force))
            if magnitude < 1e-9:
                continue
            length = 0.12
            ux, uy = force[0] / magnitude, force[1] / magnitude
            self.ax.arrow(
                ibot.x, ibot.y, ux * length, uy * length,
                head_width=0.02, head_length=0.02,
                fc="red", ec="red", length_includes_head=True, zorder=5,
            )

    def draw_headings(self, nest: Nest) -> None:
        for ibot in nest.bots.values():
            orientation = ibot.bot.orientation
            length = 0.1
            ux, uy = np.sin(orientation), np.cos(orientation)
            self.ax.arrow(
                ibot.x, ibot.y, ux * length, uy * length,
                head_width=0.02, head_length=0.02,
                fc="green", ec="green", length_includes_head=True, zorder=5,
            )

    def draw_target_lines(self, nest: Nest) -> None:
        for ibot in nest.bots.values():
            target = ibot.debug_target
            if target is None:
                continue
            self.ax.plot(
                [ibot.x, target[0]], [ibot.y, target[1]],
                linestyle="--", color="purple", alpha=0.5, linewidth=1, zorder=3,
            )

    def draw_influence_zones(self, arena: Arena, nest: Nest) -> None:
        influence_dist = getattr(nest.nav, "influence_dist", None)
        if influence_dist is None:
            return
        for obstacle in arena.obstacles:
            ring = Circle(
                (obstacle.position[0], obstacle.position[1]),
                obstacle.radius + influence_dist,
                fill=False, linestyle=":", edgecolor="orange", alpha=0.6, zorder=2,
            )
            self.ax.add_patch(ring)

    def draw_bot_locations(self, nest: Nest) -> None:
        label_offset = 0.01
        for ibot in nest.bots.values():
            self.ax.text(
                ibot.x,
                ibot.y + label_offset,
                f"({ibot.x:.3f}, {ibot.y:.3f})",
                ha="center",
                va="bottom",
                fontsize=8,
                color="black",
                zorder=6,
            )

    def draw_overlays(self, arena: Arena, nest: Nest) -> None:
        if self.overlays["influence"]:
            self.draw_influence_zones(arena, nest)
        if self.overlays["target"]:
            self.draw_target_lines(nest)
        if self.overlays["force"]:
            self.draw_force_vectors(nest)
        if self.overlays["heading"]:
            self.draw_headings(nest)
        if self.overlays["bot_locations"]:
            self.draw_bot_locations(nest)

    def visualize_simulation(self, arena: Arena, nest: Nest) -> None:
        self.draw_nest(nest.location)
        self.draw_bots(nest)
        self.draw_targets(arena)
        self.draw_obstacles(arena)
        self.draw_arena(arena)

    def update_frame(self, frame) -> list:
        self.ax.clear()
        self.visualize_simulation(self.arena, self.nest)
        self.draw_overlays(self.arena, self.nest)
        return []

    def animate_simulation(self) -> FuncAnimation:
        anim = FuncAnimation(
            self.fig,
            self.update_frame,
            interval=self.frametime,
            blit=False,
            cache_frame_data=False,
        )
        plt.show()
        return anim
    
    def on_key_press(self, event):
        if event.key == ' ':
            self.pause_callback()
