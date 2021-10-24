from __future__ import annotations  # python 3.10
from string import Template
import pygame
import yaml
import os
from typing import List, Dict, Optional
from redpanda.ecs.types import Direction


# TODO list
#  determine how to handle frames shown for varying times

def to_direction(direction: str) -> Direction:
    conversion: Dict[str, Direction] = {
        'up': Direction.up,
        'down': Direction.down,
        'left': Direction.left,
        'right': Direction.right
    }
    return conversion[direction]


class SpriteSheetFrame():
    __slots__ = ['_filename', '_rect', '_flip_x', '_flip_y']

    def __init__(self,
                 filename: str,
                 rect: Optional[pygame.Rect],
                 flip_x: bool,
                 flip_y: bool) -> None:
        self._filename = filename
        self._rect = rect
        self._flip_x = flip_x
        self._flip_y = flip_y

    def __str__(self) -> str:
        return f'Filename: {self._filename} Rect: {self._rect} Flip_X: {self._flip_x} Flip_Y: {self._flip_y}'

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def rect(self) -> Optional[pygame.Rect]:
        return self._rect

    @property
    def flip_x(self) -> bool:
        return self._flip_x

    @property
    def flip_y(self) -> bool:
        return self._flip_y


class SpriteSheetAnimation():
    __slots__ = ['_frames']

    def __init__(self) -> None:
        self._frames: List[SpriteSheetFrame] = []

    def __str__(self) -> str:
        return ' '.join([str(frame) for frame in self._frames])

    @property
    def frames(self) -> List[SpriteSheetFrame]:
        return self._frames

    def add_frame(self, frame: SpriteSheetFrame) -> None:
        self._frames.append(frame)


class SpriteSheetAnimationSet():
    __slots__ = ['_name', '_direction']

    def __init__(self, name: str) -> None:
        self._name: str = name
        self._direction: List[SpriteSheetAnimation] = [SpriteSheetAnimation() for i in range(0, len(Direction))]

    def __str__(self) -> str:
        #print(f'DEBUG: {" ".join([str(direction) for direction in self._direction])}')
        return f'{self._name}: {" ".join([str(direction) for direction in self._direction])}'

    @property
    def name(self) -> str:
        return self._name

    def direction(self, direction: Direction) -> SpriteSheetAnimation:
        return self._direction[direction]

    def set_direction_animation(self,
                                direction: Direction,
                                animation: SpriteSheetAnimation) -> None:
        self._direction[direction] = animation


class SpriteSheetMetaData():
    def __init__(self, name: str) -> None:
        self._name: str = name
        self._sets: Dict[str, SpriteSheetAnimationSet] = {}

    def __str__(self) -> str:
        return f'SpriteSheet:{self._name}: {" ".join([f"{name}: {str(animation_set)}" for name, animation_set in self._sets.items()])}'

    def __repr__(self) -> str:
        return f'SpriteSheet:{self._name}: sets:[{", ".join(self._sets.keys())}]'

    @property
    def name(self) -> str:
        return self._name

    def animation_set(self, name: str) -> Optional[SpriteSheetAnimationSet]:
        return self._sets.get(name)

    def add_animation_set(self, name: str, animation_set: SpriteSheetAnimationSet) -> None:
        self._sets[name] = animation_set

"""
class PygameImage():
    def __init__(self, filename: str) -> None:
        self._filename: str = filename
        self._image: Optional[pygame.Surface] = None

    def load(self) -> PygameImage:
        try:
            self._image = pygame.image.load(self._filename).convert_alpha()
        except pygame.error as e:
            # TODO do this better
            raise SystemExit from e
        return self

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def image(self) -> Optional[pygame.Surface]:
        return self._image

    def pixel_color_at(self, x: int, y: int) -> pygame.Color:
        # use the very first pixel color as colorkey
        return self._image.get_at((0,0))
"""

class SpriteSheetParser():
    """Builds a sprite sheet"""
    def __init__(self) -> None:
        self._meta = None

    def parse(self, sprites_dir: str, meta_filename: str) -> SpriteSheetParser:
        # load yaml meta file
        prefix = sprites_dir
        try:
            with open(os.path.join(prefix, meta_filename)) as meta_file:
                data = yaml.load(meta_file, Loader=yaml.FullLoader)
                if data.get('type') != 'resource':
                    raise ValueError(f'{data.get("type")} is not of type resource')
                resource_data = data['resource']
                name = resource_data['name']
                if resource_data['type'] == 'spritesheet-simple':
                    self._meta = SpriteSheetMetaData(name)

                    ss_filename = os.path.join(prefix, resource_data['filename'])

                    width = resource_data['size']['width']
                    height = resource_data['size']['height']
                    alpha_type = resource_data['alpha']['type']

                    # Iterate through each animation set, idle, walking, etc
                    for name, animation_set_data in resource_data['animations'].items():
                        animation_set = SpriteSheetAnimationSet(name)
                        if animation_set_data:
                            # Iterate through up, down, left, right
                            for direction_name, animation_data in animation_set_data.items():
                                if not animation_data:  # TODO figure out a better way to handle this
                                    continue
                                animation = SpriteSheetAnimation()
                                direction = to_direction(direction_name)
                                if animation_data['type'] == 'horizontal':
                                    flip_x = False
                                    flip_y = False
                                    if 'flip' in animation_data:
                                        if 'x' in animation_data['flip']:
                                            flip_x = animation_data['flip']['x']
                                        if 'y' in animation_data['flip']:
                                            flip_y = animation_data['flip']['y']
                                    frame_count = animation_data['frame_count']
                                    left = animation_data['first_frame']['x']
                                    top = animation_data['first_frame']['y']
                                    for frame_index in range(0, frame_count):
                                        frame_top = top
                                        frame_left = left + width * frame_index
                                        frame = SpriteSheetFrame(ss_filename,
                                                                 pygame.Rect(frame_left,
                                                                             frame_top,
                                                                             width,
                                                                             height),
                                                                 flip_x,
                                                                 flip_y)
                                        animation.add_frame(frame)
                                animation_set.set_direction_animation(direction, animation)
                        self._meta.add_animation_set(name, animation_set)
                elif resource_data['type'] == 'spritesheet-collection':
                    self._meta = SpriteSheetMetaData(name)

                    alpha_type = resource_data['alpha']['type']
                    # Iterate through each animation set, idle, walking, etc
                    for name, animation_set_data in resource_data['animations'].items():
                        animation_set = SpriteSheetAnimationSet(name)
                        if animation_set_data:
                            # Iterate through up, down, left, right
                            for direction_name, animation_data in animation_set_data.items():
                                animation = SpriteSheetAnimation()
                                direction = to_direction(direction_name)

                                if animation_data['type'] == 'single':
                                    frame_count = animation_data['frame_count']
                                    filename_template = animation_data['frames']['filename_template']
                                    flip_x = False
                                    flip_y = False
                                    if 'flip' in animation_data:
                                        if 'x' in animation_data['flip']:
                                            flip_x = animation_data['flip']['x']
                                        if 'y' in animation_data['flip']:
                                            flip_y = animation_data['flip']['y']
                                    for frame_index in range(0, frame_count):
                                        ss_filename = os.path.join(prefix, Template(filename_template).substitute(index=frame_index))
                                        frame = SpriteSheetFrame(ss_filename,
                                                                 None,
                                                                 flip_x,
                                                                 flip_y)
                                        animation.add_frame(frame)
                                animation_set.set_direction_animation(direction, animation)
                        self._meta.add_animation_set(name, animation_set)
                else:
                    # TODO find better exception
                    raise Exception('Unknown sprite type')
        except yaml.YAMLError:
            print('Unable to load spritesheet metadata')
            raise
        #print(self._meta)
        return self

    def meta(self) -> SpriteSheetMetaData:
        return self._meta

    def convert(self, width: int, height: int) -> SpriteSheetParser:
        pass

    # TODO should this class adapt (scaling) the sprites
    #      to requested size?