from __future__ import annotations  # python 3.10
import os
import yaml
from redpanda.template.worldtemplate import WorldTemplate
from redpanda.parser.areaparser import AreaTemplateParser
import redpanda.logging


logger = redpanda.logging.get_logger('parser.WorldTemplate')


class WorldTemplateParser():
    def __init__(self, yaml_dir: str) -> None:
        self._yaml_dir: str = yaml_dir
        self._template = WorldTemplate()

    def parse(self, filename: str) -> WorldTemplateParser:
        yaml_filename = os.path.join(self._yaml_dir, filename)
        try:
            with open(yaml_filename) as yaml_file:
                data = yaml.load(yaml_file, Loader=yaml.FullLoader)
                if data.get('type') != 'world':
                    raise ValueError(f'{data.get("type")} is not of type world')
                if 'areas' in data['world']:
                    for name, yaml_area_data in data['world']['areas'].items():
                        template = AreaTemplateParser().parse(name, yaml_area_data).template()
                        self._template.add_area(template.name, template)
        except yaml.YAMLError:
            logger.error('Unable to load world template')
            raise

        return self
        
    def build(self) -> WorldTemplate:
        world = self._template
        self._template = WorldTemplate()
        return world
