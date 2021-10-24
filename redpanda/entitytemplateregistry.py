from __future__ import annotations  # python 3.10
import yaml
import os
from redpanda.template.entitytemplate import EntityTemplate


class EntityTemplateRegistry():
    def __init__(self) -> None:
        self._db: dict[str, EntityTemplate] = {}

    def __str__(self) -> str:
        return f'{str(self._db)}'

    def __repr__(self) -> str:
        return f'{repr(self._db)}'

    def template(self, name: str) -> EntityTemplate:
        if name in self._db:
            data = self._db[name]
            if isinstance(data, EntityTemplate):
                return data
            raise Exception(f'{name} is not a npc tempalte')
        raise Exception(f'{name} is not a template')

    def add_template(self, name: str, template: EntityTemplate) -> None:
        # TODO consider handling adding twice
        self._db[name] = template


class EntityTemplateParser():
    def __init__(self) -> None:
        self._template: EntityTemplate = EntityTemplate()

    def parse(self, name: str, data) -> EntityTemplateParser:
        self._template.name = name
        for key, value in data.items():
            if key == 'spritesheet':
                self._template.spritesheet = value
            if key == 'width':
                self._template.width = value
            if key == 'height':
                self._template.height = value
        return self

    def template(self) -> EntityTemplate:
        return self._template


class EntityTemplateRegistryParser():
    def __init__(self, yaml_dir: str) -> None:
        self._registry: EntityTemplateRegistry = EntityTemplateRegistry()
        self._yaml_dir: str = yaml_dir

    def parse(self, filename: str) -> EntityTemplateRegistryParser:
        # load yaml file
        yaml_filename = os.path.join(self._yaml_dir, filename)
        try:
            with open(yaml_filename) as yaml_file:
                data = yaml.load(yaml_file, Loader=yaml.FullLoader)
                if data.get('type') != 'entity-template':
                    raise ValueError(f'{data.get("type")} is not of type npc-template')
                if 'entity-template' in data:
                    for name, yaml_npc_data in data['entity-template'].items():
                        template = EntityTemplateParser().parse(name, yaml_npc_data).template()
                        self._registry.add_template(template.name, template)
        except yaml.YAMLError:
            print('Unable to load npc templates')
            raise
        return self

    def build(self) -> EntityTemplateRegistry:
        registry = self._registry
        self._registry = EntityTemplateRegistry()
        return registry