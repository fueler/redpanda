
import pygame
import redpanda.logging


logger = redpanda.logging.get_logger('sounds')


class SoundData:
    def __init__(self, name: str, filename: str, load_now: bool = True) -> None:
        self._name: str = name
        self._filename: str = filename
        try:
            self._sound = pygame.mixer.Sound(self._filename)
        except FileNotFoundError as e:
            logger.error(f'Sound filename not found: {self._filename}')
            raise

    @property
    def name(self) -> str:
        return self._name

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def sound(self) -> pygame.mixer.Sound:
        return self._sound
