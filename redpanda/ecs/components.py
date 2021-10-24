from typing import Dict, Optional
from pygame import Rect
from pygame.math import Vector3
from redpanda.ecs.core import Component
from redpanda.sprite import Sprite
from redpanda.ecs.types import Animation, Direction, SoundEffect


class DirectionComponent(Component):
    def __init__(self, initial_direction: Direction = Direction.down) -> None:
        super().__init__('direction')
        self._value: Direction = initial_direction

    @property
    def value(self) -> Direction:
        return self._value

    @value.setter
    def value(self, direction: Direction) -> None:
        self._value = direction


class LocationComponent(Component):
    def __init__(self, area: str, position: Vector3) -> None:
        super().__init__('location')
        self._area: str = area
        self._position: Vector3 = position
        self._last_position: Vector3 = position

    @property
    def area(self) -> str:
        return self._area

    @area.setter
    def area(self, new_area: str) -> None:
        # TODO enforce position change here as well?
        self._area = new_area

    @property
    def position(self) -> Vector3:
        return self._position

    @position.setter
    def position(self, vector: Vector3) -> None:
        self._last_position = self._position
        self._position = vector


class VectorBasedComponent(Component):
    def __init__(self, name: str, vector: Vector3) -> None:
        super().__init__(name)
        self._vector: Vector3 = vector

    @property
    def value(self) -> Vector3:
        return self._vector

    @value.setter
    def value(self, vector: Vector3) -> None:
        self._vector = vector

    @property
    def x(self) -> float:
        return self._vector.x

    @property
    def y(self) -> float:
        return self._vector.y

    @property
    def z(self) -> float:
        return self._vector.z


class MovementComponent(VectorBasedComponent):
    def __init__(self) -> None:
        super().__init__('movement', Vector3(0, 0, 0))


class VelocityComponent(VectorBasedComponent):
    def __init__(self, vector: Optional[Vector3] = None) -> None:
        super().__init__('velocity', vector or Vector3(0, 0, 0))


class SpeedComponent(VectorBasedComponent):
    def __init__(self, vector: Vector3) -> None:
        super().__init__('speed', vector)


class SpriteComponent(Component):
    def __init__(self, sprite: Sprite) -> None:
        super().__init__('sprite')
        self._sprite: Sprite = sprite

    @property
    def sprite(self) -> Sprite:
        return self._sprite


class AnimationComponent(Component):
    def __init__(self) -> None:
        super().__init__('animation')
        self._timer: float = 0
        self._counter: int = 0
        self._action: Animation = Animation.walking  # TODO should be idle

    @property
    def timer(self) -> float:
        return self._timer

    @timer.setter
    def timer(self, value: float) -> None:
        self._timer = value

    @property
    def counter(self) -> int:
        return self._counter

    @counter.setter
    def counter(self, value: int) -> None:
        self._counter = value

    @property
    def action(self) -> Animation:
        return self._action


class RectComponent(Component):  # TODO this isn't used so far
    def __init__(self, rect: Rect) -> None:
        super().__init__('rect')
        self._rect: Rect = rect

    @property
    def rect(self) -> Rect:
        return self._rect


class ControllerComponent(Component):
    def __init__(self) -> None:
        super().__init__('controller')

    @property
    def index(self) -> int:
        return 1  # TODO Fix this


class TimerComponent(Component):
    def __init__(self, name: str, id: str) -> None:
        super().__init__(name)
        self._id: str = id

    @property
    def id(self) -> str:
        return self._id

class RandomDirectionTimerComponent(TimerComponent):
    def __init__(self, id: str) -> None:
        super().__init__('random_direction_timer', id)


class SoundEffectsComponent(Component):
    def __init__(self) -> None:
        super().__init__('sound_effects')
        self._sound_effects: Dict[str, SoundEffect] = {}

    @property
    def sound_effects(self) -> Dict[str, SoundEffect]:
        return self._sound_effects

    def add(self, name: str, effect: SoundEffect) -> None:
        self._sound_effects[name] = effect
