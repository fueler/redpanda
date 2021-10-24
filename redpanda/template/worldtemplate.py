from typing import Dict
from redpanda.template.areatemplate import AreaTemplate


class WorldTemplate:
    def __init__(self) -> None:
        self._areas: Dict[str, AreaTemplate] = {}

    def __repr__(self) -> str:
        return f'{repr(self._areas)}'

    @property
    def areas(self) -> Dict[str, AreaTemplate]:
        return self._areas

    def add_area(self, name: str, template: AreaTemplate) -> None:
        # TODO handle duplicates
        self._areas[name] = template
