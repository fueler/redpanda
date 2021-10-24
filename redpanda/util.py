import pygame
import sys


def quit_game():
    pygame.quit()
    sys.exit()

def set_window_icon(icon_filename: str) -> None:
    #title_bar_icon = pygame.image.load(icon_filename)
    #pygame.display.set_icon(title_bar_icon)
    pass

def set_window_caption(caption: str) -> None:
    pygame.display.set_caption(caption)

def set_window_size(width: int, height: int) -> pygame.Surface:
    """Returns surface with width and height requested"""
    return pygame.display.set_mode((width, height))
