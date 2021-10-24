from redpanda.ecs.types import Timer
from typing import Callable, Dict
from redpanda.ecs.core import Entity


# TODO Need to figure out what arguments to actually pass to all the triggers
#      OR revamp this to make more generic, BUT HOW!?


def movement_trigger(entity: Entity, timer: Timer) -> bool:
    # TODO handle timer, should only play if timer expires
    movement = entity.components['movement']
    # print(f'{velocity.value}, length={velocity.value.length()}')
    if movement.value.length() > 0:
        return True
    return False


def timer_trigger(entity: Entity, timer: Timer) -> bool:
    if timer.timer >= timer.timeout:
        timer.timer = 0
        return True
    return False


triggers: Dict[str, Callable[[Entity, Timer],bool]] = {
    'movement': movement_trigger,
    'timer': timer_trigger,
}
