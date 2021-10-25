import random
import pygame
import pygame.time
from redpanda.ecs.core import System
from redpanda.ecs.core import Plugin
from redpanda.ecs.core import AppBuilder
from redpanda.ecs.core import World
from redpanda.ecs.core import Resources
from redpanda.ecs.core import ECS
from redpanda.ecs.core import register_atexit
from redpanda.ecs.types import Controller
from pygame_gui import UIManager
from redpanda.timerregistery import TimerRegistry
import redpanda.logging

logger = redpanda.logging.get_logger('pygame_plugin')

class ResourceTypes:
    SYS_QUIT = 'sys.quit'
    SYS_CLOCK = 'sys.clock'
    SYS_TIMERS = 'sys.timers'
    SYS_RESOLUTION = 'sys.resolution'
    SYS_KEYS_PRESSED = 'sys.keys_pressed'
    GAME_DIRECTORIES = 'sys.directories'
    GAME_TITLE = 'game.title'
    GAME_TIME_ELAPSED = 'game.time_elapsed'
    GAME_BACKGROUND_MUSIC = 'game.music.background'
    GAME_CAMERA_TRACKING_ENTITY = 'game.camera.tracking_entity'
    RENDERER_SURFACE = 'renderer.surface'
    CONTROLLER_PREFIX = 'sys.controller'


class PygamePlugin(Plugin):
    def __init__(self) -> None:
        super().__init__('PygamePlugin')

    def build(self, app: AppBuilder):
        class Config(System):
            def __init__(self) -> None:
                super().__init__('Config')

            def initialize(self, world: World, resources: Resources) -> None:
                resources[ResourceTypes.GAME_TITLE] = ''
                # TODO This needs to come from config
                resources[ResourceTypes.SYS_RESOLUTION] = dict({'width': 640,
                                                                'height': 480})

                resources[ResourceTypes.GAME_DIRECTORIES] = {}

        class PygameSetup(System):
            def __init__(self) -> None:
                super().__init__('PygameSetup')

            def initialize(self, world: World, resources: Resources) -> None:
                pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
                pygame.init()
                pygame.font.init()
                pygame.mouse.set_visible(False)

                # TODO figure out how to handle this better
                #      Currently doing this due to "pyscroll buffer redraw" spam
                #logger = logging.getLogger('orthographic')
                #logger.setLevel(logging.ERROR)

                resources[ResourceTypes.SYS_QUIT] = False  # TODO determine if correct place
                resources[ResourceTypes.SYS_CLOCK] = pygame.time.Clock()
                resources[ResourceTypes.SYS_TIMERS] = TimerRegistry()

                def pygame_atexit():
                    logger.info('Quiting pygame')
                    pygame.quit()

                register_atexit(pygame_atexit)


        class PygameRendererSetup(System):
            def __init__(self) -> None:
                super().__init__('PygameRendererSetup')
                self._width: int = 0
                self._height: int = 0
                self._resolution_changed: bool = False
                self._title: str = ''
                self._title_changed: bool = False

            def update(self, world: World, resources: Resources) -> None:
                width = resources[ResourceTypes.SYS_RESOLUTION]['width']
                height = resources[ResourceTypes.SYS_RESOLUTION]['height']

                if self._width != width or self._height != height:
                    self._resolution_changed = True
                    self._width = width
                    self._height = height

                if self._title != resources[ResourceTypes.GAME_TITLE]:
                    self._title = resources[ResourceTypes.GAME_TITLE]
                    self._title_changed = True

            def run_once(self, world: World, resources: Resources) -> None:
                if self._resolution_changed:
                    self._resolution_changed = False
                    surface = pygame.display.set_mode((self._width, self._height))
                    resources[ResourceTypes.RENDERER_SURFACE] = surface
                    logger.info(self.name(), f'- window created {self._width}x{self._height}')

                if self._title_changed:
                    self._title_changed = False
                    pygame.display.set_caption(set._title)

        class PygameRendererFlip(System):
            def __init__(self) -> None:
                super().__init__('PygameRendererFlip')

            def run_once(self, world: World, resources: Resources) -> None:
                pygame.display.update()


        class PygameRenderer(System):
            def __init__(self) -> None:
                super().__init__('PygameRenderer')

            def run_once(self, world: World, resources: Resources) -> None:
                # Render World and Entities
                surface = resources[ResourceTypes.RENDERER_SURFACE]
                tracking_entity = resources[ResourceTypes.GAME_CAMERA_TRACKING_ENTITY]  # TODO handle if no tracking entity
                world.current_area.render(surface, tracking_entity.rect.center)


        class PygameEvents(System):
            """Handles raw pygame events"""
            def __init__(self) -> None:
                super().__init__('PygameEvents')

            def run_once(self, world: World, resources: Resources) -> None:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        resources[ResourceTypes.SYS_QUIT] = True


        class PygameTimeElapsed(System):
            """Handles keeping time elapsed"""
            def __init__(self) -> None:
                super().__init__('PygameTimeElapsed')
            
            def run_once(self, world: World, resources: Resources) -> None:
                resources[ResourceTypes.GAME_TIME_ELAPSED] = resources[ResourceTypes.SYS_CLOCK].get_time()


        class PygameSleepToNextFrame(System):
            """Handles sleeping until next frame update"""
            def __init__(self) -> None:
                super().__init__('PygameSleepToNextFrame')
            
            def run_once(self, world: World, resources: Resources) -> None:
                resources[ResourceTypes.SYS_CLOCK].tick(60)  # TODO Fix this by using config


        class PygameInput(System):
            """Stores raw input from pygame"""
            def __init__(self) -> None:
                super().__init__('PygameInput')

            def run_once(self, world: World, resources: Resources) -> None:
                resources[ResourceTypes.SYS_KEYS_PRESSED] = pygame.key.get_pressed()


        class PygameControllersSetup(System):
            def __init__(self) -> None:
                super().__init__('PygameControllersSetup')

            def run_once(self, world: World, resources: Resources) -> None:
                for i in range(1, 5):
                    resource_name = ResourceTypes.CONTROLLER_PREFIX + str(i)
                    resources[resource_name] = Controller()


        class PygameController(System):
            """Maps raw input to controller input"""
            def __init__(self) -> None:
                super().__init__('PygameController')
                self._resource_name = ResourceTypes.CONTROLLER_PREFIX + '1'  # TODO Make this configurable

            def run_once(self, world: World, resources: Resources) -> None:
                """ TODO Need to handle key mapping"""
                resources[self._resource_name].up = True if resources[ResourceTypes.SYS_KEYS_PRESSED][pygame.K_UP] else False
                resources[self._resource_name].down = True if resources[ResourceTypes.SYS_KEYS_PRESSED][pygame.K_DOWN] else False
                resources[self._resource_name].left = True if resources[ResourceTypes.SYS_KEYS_PRESSED][pygame.K_LEFT] else False
                resources[self._resource_name].right = True if resources[ResourceTypes.SYS_KEYS_PRESSED][pygame.K_RIGHT] else False


        class PygameBackgroundMusic(System):
            """Plays background music"""
            def __init__(self) -> None:
                super().__init__('PygameBackgroundMusic')
    
            def run_once(self, world: World, resources: Resources) -> None:
                # TODO Make this better!!!
                if not pygame.mixer.music.get_busy():
                    if ResourceTypes.GAME_BACKGROUND_MUSIC in resources.keys():
                        filename = resources[ResourceTypes.GAME_BACKGROUND_MUSIC]
                        if filename:
                            pygame.mixer.music.load(filename)
                            pygame.mixer.music.set_volume(0.05)
                            pygame.mixer.music.play(-1)


        class Timers(System):
            """Manages Registered Timers"""
            def __init__(self) -> None:
                super().__init__('Timers')

            def run_once(self, world: World, resources: Resources) -> None:
                timers = resources[ResourceTypes.SYS_TIMERS].timers
                for id, timer in timers.items():
                    # Check for timer reset first
                    if timer.queue_reset:
                        timer.queue_reset = False
                        timer.expired = False
                        if not timer.random_timeout:
                            if timer.expired:
                                timer.timer -= timer.timeout
                            else:
                                timer.timer = 0
                        else:
                            timer.timer = 0
                            timer.timeout = random.uniform(timer.timer_range_begin, timer.timer_range_end)

                    # Update timer and check for expiry
                    timer.timer += resources[ResourceTypes.GAME_TIME_ELAPSED]
                    if timer.timer >= timer.timeout:
                        timer.expired = True



        (app.add_startup_system_to_stage(ECS.STARTUP_STAGE_PRE_STARTUP, Config())
            .add_startup_system(PygameRendererSetup())
            .add_startup_system(PygameSetup())
            .add_startup_system(PygameControllersSetup())
            .add_system_to_stage(ECS.STAGE_PRE_EVENT, PygameTimeElapsed())
            .add_system_to_stage(ECS.STAGE_PRE_EVENT, Timers())
            .add_system_to_stage(ECS.STAGE_PRE_EVENT, PygameInput())
            .add_system_to_stage(ECS.STAGE_PRE_EVENT, PygameEvents())
            .add_system_to_stage(ECS.STAGE_PRE_EVENT, PygameController())
            .add_system_to_stage(ECS.STAGE_UPDATE, PygameBackgroundMusic())
            .add_system_to_stage(ECS.STAGE_POST_UPDATE, PygameRenderer())
            .add_system_to_stage(ECS.STAGE_LAST, PygameRendererFlip())
            .add_system_to_stage(ECS.STAGE_LAST, PygameSleepToNextFrame())
        )


class UiManager(System):
    def __init__(self) -> None:
        super().__init__('UiManager')
        self._width = 640
        self._height = 480

    def initialize(self, world: World, resources: Resources):
        self._ui_manager = UIManager((self._width, self._height))

    def update(self, world: World, resources: Resources) -> None:
        pass

    def run_once(self, world: World, resources: Resources) -> None:
        pass
