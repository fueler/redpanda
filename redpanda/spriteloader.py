from redpanda.ecs.types import Animation, Direction
from typing import List, Optional
from redpanda.sprite import Sprite, SpriteAnimation, SpriteAnimationSet
from redpanda.spritesheet import SpriteSheetAnimation, SpriteSheetAnimationSet, SpriteSheetMetaData
import pygame


class SimpleSpriteSheetConverter():
    """Simple sprite sheet"""
    def __init__(self, filename: str, width: int, height: int) -> None:
        try:
            self._sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as message:
            # TODO do better error handling
            print('Unable to load spritesheet image: {}'.format(filename))
            raise SystemExit from message

        self._width = width
        self._height = height

    def image_at(self,
                 rectangle: Optional[pygame.Rect],
                 flip_x: bool = False,
                 flip_y: bool = False,
                 colorkey = None):  # TODO fix type hint
        """Loads image from specific rectangle"""
        if not rectangle:
            # Use full image
            rectangle = self._sheet.get_rect()
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
        image.blit(self._sheet, (0, 0), rect)
        if colorkey is not None:
            # use specified colorkey
            if colorkey == -1:
                # use the very first pixel color as colorkey
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        image = pygame.transform.scale(image, (self._width, self._height))
        image = pygame.transform.flip(image, flip_x, flip_y)
        return image

    def images_at(self, rects, flip_x = False, flip_y = False, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, flip_x, flip_y, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


def load_sprite(meta: SpriteSheetMetaData, width: int, height: int) -> Sprite:
    def load_sprite_animation(meta: SpriteSheetAnimation) -> SpriteAnimation:
        list_of_frames: List[pygame.Surface] = []

        for frame in meta.frames:
            # TODO need to cache the converter for same filename or make
            #      converter cache it
            converter = SimpleSpriteSheetConverter(frame.filename, width, height)
            list_of_frames.append(converter.image_at(frame.rect,
                                                     frame.flip_x,
                                                     frame.flip_y))

        return SpriteAnimation(list_of_frames)

    def load_sprite_animation_set(meta: SpriteSheetAnimationSet) -> SpriteAnimationSet:
        list_of_animations: List[SpriteAnimation] = []

        for entry in Direction:
            list_of_animations.append(load_sprite_animation(meta.direction(entry.value)))

        return SpriteAnimationSet(meta.name, list_of_animations)

    list_of_animation_sets: List[SpriteAnimationSet] = []
    for entry in Animation:
        if meta.animation_set(entry.name):
            list_of_animation_sets.append(load_sprite_animation_set(meta.animation_set(entry.name)))

    return Sprite(meta.name, list_of_animation_sets)
