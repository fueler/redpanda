from typing import Dict
import uuid
from redpanda.ecs.types import Timer


class TimerRegistry:
    def __init__(self) -> None:
        self._timers: Dict[str, Timer] = {}

    @property
    def timers(self) -> Dict[str, Timer]:
        return self._timers

    def timer(self, id: str) -> Timer:
        return self._timers[id]

    def create(self,
               initial_value: float = 0,
               timeout: float = 0,
               timer_range_begin: float = 0,
               timer_range_end: float = 0) -> str:
        id = uuid.uuid4()
        self._timers[id] = Timer(initial_value,
                                 timeout,
                                 random_timeout=True if (timer_range_begin or timer_range_end) else False,
                                 timer_range_begin=timer_range_begin,
                                 timer_range_end=timer_range_end)
        return id
