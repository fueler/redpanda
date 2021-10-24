from typing import List
import pygame
from redpanda.ecs.types import Animation, Direction


class SpriteAnimation():
    def __init__(self, frames: List[pygame.Surface]) -> None:
        self._frames: List[pygame.Surface] = frames

    @property
    def frames(self) -> List[pygame.Surface]:
        return self._frames


class SpriteAnimationSet():
    """Contains a single animation and different variations; eg up, down, left, right"""
    def __init__(self, name: str, animations: List[SpriteAnimation]) -> None:
        self._name: str = name
        self._direction: List[SpriteAnimation] = animations

    def direction(self, direction: Direction) -> SpriteAnimation:
        return self._direction[direction]


class Sprite():
    """Contains animations for all types, eg walking"""
    def __init__(self, name: str, sets: List[SpriteAnimationSet]) -> None:
        self._name: str = name
        self._sets: List[SpriteAnimationSet] = sets

    @property
    def name(self) -> str:
        return self._name

    # TODO convert to getitem
    def animation_set(self, animation: Animation) -> SpriteAnimationSet:
        return self._sets[animation]
