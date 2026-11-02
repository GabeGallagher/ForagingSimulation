from dataclasses import dataclass


"""Per-bot state for one boundary-following episode. side is the direction of
travel around obstacles (same convention as the potential field's circulation),
target is what the bot was heading for when it got stuck, and hit_dist is how
far it was from that target at the time"""


@dataclass
class BoundaryFollow:
    side: float
    target: list[float]
    hit_dist: float
    reversed: bool = False
