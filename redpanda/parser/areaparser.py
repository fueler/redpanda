from __future__ import annotations  # python 3.10
from redpanda.template.areatemplate import AreaTemplate


class AreaTemplateParser():
    def __init__(self) -> None:
        self._template: AreaTemplate = AreaTemplate()

    def parse(self, name: str, data) -> AreaTemplateParser:
        self._template.name = name
        for key, value in data.items():
            if key == 'filename':
                self._template.filename = value
        return self

    def template(self) -> AreaTemplate:
        return self._template
