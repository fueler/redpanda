from __future__ import annotations
from redpanda.template.worldtemplate import WorldTemplate
from redpanda.parser.worldparser import WorldTemplateParser  # python 3.10
import yaml
import os
from redpanda.spritesheet import SpriteSheetMetaData, SpriteSheetParser
from redpanda.sounds import SoundData
from typing import Union
import pprint

class AssetRegistry():
    def __init__(self) -> None:
        self._db: dict[str, Union[SpriteSheetMetaData, SoundData, WorldTemplate]] = {}

    def __str__(self) -> str:
       return f'{str(self._db)}'

    def __repr__(self) -> str:
        return f'{repr(self._db)}'

    def spritesheet(self, name: str) -> SpriteSheetMetaData:
        if name in self._db:
            data = self._db[name]
            if isinstance(data, SpriteSheetMetaData):
                return data
            raise Exception(f'{name} is not a spritesheet asset')
        raise Exception(f'{name} is not an asset')

    def add_spritesheet(self, name: str, meta: SpriteSheetMetaData) -> None:
        # TODO consider handling adding twice
        self._db[name] = meta

    def sound(self, name: str) -> SoundData:
        if name in self._db:
            data = self._db[name]
            if isinstance(data, SoundData):
                return data
            raise Exception(f'{name} is not a sound asset')
        raise Exception(f'{name} is not an asset')

    def add_sound(self, name: str, sound_filename: str) -> None:
        # TODO consider handling adding twice
        # TODO consider converting this to just Metadata
        self._db[name] = SoundData(name, sound_filename)

    def world(self) -> WorldTemplate:
        name = 'world'
        if name in self._db:
            data = self._db[name]
            if isinstance(data, WorldTemplate):
                return data
            raise Exception(f'{name} is not a world template asset')
        raise Exception(f'{name} is not an asset')

    def add_world(self, template: WorldTemplate) -> None:
        # TODO consider handling adding twice
        self._db['world'] = template


class AssetRegistryParser():  # TODO Move this
    def __init__(self, yaml_dir: str) -> None:
        self._registry: AssetRegistry = AssetRegistry()
        self._yaml_dir: str = yaml_dir

    def parse(self, meta_filename: str) -> AssetRegistryParser:
        # load yaml meta file
        meta_filename = os.path.join(self._yaml_dir, meta_filename)
        try:
            with open(meta_filename) as meta_file:
                data = yaml.load(meta_file, Loader=yaml.FullLoader)
                if data.get('type') != 'asset-list':
                    raise ValueError(f'{data.get("type")} is not of type resource')
                if 'sprites' in data:
                    print('Assets: Parsing Sprites')
                    for name, yaml_filename in data['sprites'].items():
                        meta = SpriteSheetParser().parse(os.path.join(self._yaml_dir, 'sprites'), yaml_filename).meta()  # TODO fix this
                        self._registry.add_spritesheet(meta.name, meta)
                if 'sounds' in data:
                    print('Assets: Parsing Sounds')
                    for name, sound_filename in data['sounds'].items():
                        self._registry.add_sound(name, os.path.join(self._yaml_dir, 'sounds', sound_filename))  # TODO fix this
                if 'world' in data:
                    print('Assets: Parsing World')
                    world_filename = data['world']
                    world = WorldTemplateParser(self._yaml_dir).parse(world_filename).build()
                    self._registry.add_world(world)
        except yaml.YAMLError:
            print('Unable to load assets metadata')
            raise
        return self

    def build(self) -> AssetRegistry:
        registry = self._registry
        self._registry = AssetRegistry()
        return registry
