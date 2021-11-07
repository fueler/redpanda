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


class PyScrollMap():
    # TODO add slots

    def __init__(self,
                 tmx_data,
                 map_data,
                 map_layer,
                 main_group,
                 stationary_collision_list) -> None:
        self._tmx_data = tmx_data
        self._map_data = map_data
        self._map_layer = map_layer
        self._stationary_collision_list = stationary_collision_list
        self._main_group = main_group  # TODO should this be here or in the area?

    @property
    def tmx_data(self):
        return self._tmx_data

    @property
    def map_data(self):
        return self._map_data

    @property
    def map_layer(self):
        return self._map_layer

    @property
    def stationary_collision_list(self):
        return self._stationary_collision_list

    @property
    def main_group(self):
        return self._main_group


@dataclass
class WorldMovementEvent():
    area: str
