from enum import IntEnum
from dataclasses import dataclass
from typing import List


class Animation(IntEnum):
    idle = 0
    walking = 1
    running = 2
    sitting = 3


class Direction(IntEnum):
    up = 0
    down = 1
    left = 2
    right = 3


@dataclass
class Controller():
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False


@dataclass
class Timer():
    timer: float = 0
    timeout: float = 0
    expired: bool = False
    random_timeout: bool = False
    timer_range_begin: float = 0
    timer_range_end: float = 0
    queue_reset: bool = False


@dataclass
class SoundEffect():
    name: str
    sound: str
    triggers: List[str]
    timer: Timer = Timer()  # TODO consider placing this in global timers
    volume: float = 0
    enabled: bool = False
    triggered: bool = False
