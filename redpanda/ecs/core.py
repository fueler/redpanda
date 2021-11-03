from __future__ import annotations
from abc import ABC, abstractmethod
import uuid
from collections import UserDict
from typing import List, Dict, Tuple
import pygame
from pygame.rect import Rect
from pygame.surface import Surface
import pytmx
import pyscroll
import pprint
import redpanda.logging

_atexit_fns = []

logger = redpanda.logging.get_logger('ecs')


def register_atexit(atexit_fn) -> None:
    """Register a function to be called at the end of
    the ECS game or when an exception is thrown"""
    logger.info(f'Registering atexit {atexit_fn.__name__} function')
    _atexit_fns.insert(0, atexit_fn)


def _run_atexit() -> None:
    """Iterates through all the atexit functions"""
    logger.info('Iterating atexit functions')
    for fn in _atexit_fns:
        logger.info(f'Calling {fn.__name__}')
        fn()


def start_game(game_fn) -> None:
    try:
        game_fn()
        _run_atexit()
    except:
        logger.critical('ERROR!! Exception thrown')
        _run_atexit()
        raise


class ECS:
    STARTUP_STAGE_PRE_STARTUP = 'startup_stage_pre_startup'
    STARTUP_STAGE_STARTUP = 'startup_stage_startup'
    STARTUP_STAGE_POST_STARTUP = 'startup_stage_post_startup'
    STAGE_FIRST = 'stage_first'
    STAGE_PRE_EVENT = 'stage_pre_event'
    STAGE_EVENT = 'stage_event'
    STAGE_PRE_UPDATE = 'stage_pre_update'
    STAGE_UPDATE = 'stage_update'
    STAGE_POST_UPDATE = 'stage_post_update'
    STAGE_LAST = 'stage_last'


class System(ABC):
    """An ECS system that can be added to a Schedule"""
    def __init__(self, name: str) -> None:
        self._name = name

    def __str__(self) -> str:
        return f'{self._name}'

    def name(self) -> str:
        """Returns name of system"""
        return self._name

    def initialize(self, world: World, resources: Resources) -> None:
        """Initializes the system"""
        pass

    def update(self, world: World, resources: Resources) -> None:
        pass

    def run_once(self, world: World, resources: Resources) -> None:
        pass


class Component(ABC):
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self):
        """Return component name"""
        return self._name


class Entity(pygame.sprite.Sprite):
    """Entity class that holds components. It is
    based on PyGame Sprite.

    https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite

    For Sprite Draw
    - image attribute holds what to draw
    - rect attribute - x, y == location, width, height == size

    For Sprite Collision
    - rect attribute
    """
    def __init__(self, component_list: List[Component]=[]) -> None:
        super().__init__()
        self._id = uuid.uuid4()
        self._components: Dict[str, Component] = {}
        for component in component_list:
            self._components[component.name] = component

    def __str__(self) -> str:
        return f'{self._id}: {" ".join(str(c) for c in self._components)}'

    def __repr__(self) -> str:
        # TODO make this easier to print and commonize with __str__
        # return super().__repr__()
        return f'{self._id}: {" ".join(str(c) for c in self._components)}'

    @staticmethod
    def default() -> Entity:
        return Entity()

    @property
    def id(self) -> int:
        """Returns id of entity"""
        return self._id

    @property
    def components(self) -> Dict[str, Component]:
        return self._components

    def clear(self) -> Entity:
        """Removes all components from entity"""
        self._components = {}
        return self

    def add_component(self, component: Component) -> Entity:
        """Add component to entity"""
        self._components[component.name] = component
        return self

    def add_components(self, component_list: List[Component]) -> Entity:
        for component in component_list:
            self._components[component.name] = component
        return self

    def remove(self, component: Component) -> Entity:
        """Remove component from entity"""
        del self._components[component.name]
        return self

    @property
    def image(self):
        """Used for Pygame sprite rendering"""
        sprite = self._components['sprite'].sprite
        action = self._components['animation'].action
        direction = self._components['direction'].value
        frame_index = self._components['animation'].counter
        return sprite.animation_set(action).direction(direction).frames[frame_index]

    @property
    def rect(self) -> Rect:
        """Used for Pygame sprite collision and for rendering
        x, y == location
        width, height == size
        """
        # TODO for now use size from sprite, figure out how to handle scaled image
        image = self.image
        return Rect((self._components['location'].position.x,
                     self._components['location'].position.y),
                     (image.get_width(), image.get_height()))

    @property
    def feet(self) -> Rect:
        """Used for Pygame sprite collision"""
        rect = self.rect
        feet_rect = Rect(0, 0, rect.width * 0.7, rect.height * 0.3)  # TODO verify this
        feet_rect.midbottom = rect.midbottom
        return feet_rect


class Entities():
    def __init__(self) -> None:
        self._entities: Dict[int, Entity] = {}

    def __str__(self) -> None:
        value = ''
        for _, entity in self._entities.items():
            value += '\t'
            value += '\n\t'.join(str(entity).splitlines())
            value += '\n'
        return value if value else '<EMPTY>'

    @staticmethod
    def default() -> Entities:
        return Entities()

    @property
    def entities(self) -> Dict[int, Entity]:
        return self._entities

    def contains(self, entity: Entity) -> bool:
        """Test if entity still exists"""
        return entity.id() in self._entities

    def clear(self) -> None:
        """Destroy all entities"""
        for entity in self._entities:
            entity.clear()
        self._entities = {}

    def alloc(self, component_list: List[Component] = []) -> Entity:
        """Return new Entity"""
        entity = Entity.default()
        self._entities[entity.id] = entity
        if component_list:
            entity.add_components(component_list)
        return entity

    def release(self, entity: Entity) -> None:
        """Remove Entity from container"""
        del self._entities[entity.id()]


class Resources(UserDict):
    """For now Resources will be a simple key/value store"""
    def __str__(self) -> str:
        return pprint.pformat(self.data)


class Query(ABC):
    def __init__(self) -> None:
        pass

    def execute(self, entities: Entities) -> List[Entity]:
        return []

    __call__ = execute

class ContainsComponentsQuery(Query):
    def __init__(self, *components: str) -> None:
        self._components: Tuple[str] = components

    def execute(self, entities: Entities) -> List[Entity]:
        matching_entities: List[Entity] = []
        for entity in entities.entities.values():
            if all(component in entity.components.keys() for component in self._components):
                matching_entities.append(entity)
        return matching_entities

    __call__ = execute


class Event(ABC):
    def __init__(self) -> None:
        pass


class AppExit(Event):
    def __init__(self) -> None:
        pass


class EntityBuilder():
    """TODO figure out if I need this"""
    def __init__(self) -> None:
        pass

    def add(self, component: Component) -> EntityBuilder:
        """Add component to Entity"""
        return self

    def build(self):
        """Construct a Bunble suitable for spawning"""
        pass

    def clear(self) -> EntityBuilder:
        """Drop previously added components"""
        return self


class Area():
    """Container for subsection of the World"""
    def __init__(self, name: str, map_filename: str) -> None:
        self._name = name
        self._map_file = map_filename

    def name(self) -> str:
        return self._name

    def enter(self) -> None:
        """Enter an area"""
        # TODO Move this to a system so that it can access resources
        # viewport = (resources[ResourceTypes.SYS_RESOLUTION]['width'],
        #             resources[ResourceTypes.SYS_RESOLUTION]['height'])
        viewport = (640, 480)  # TODO read from resources

        self._tmx_data = pytmx.util_pygame.load_pygame(self._map_file)
        self._map_data = pyscroll.data.TiledMapData(self._tmx_data)
        self._map_layer = pyscroll.BufferedRenderer(self._map_data,
                                                    viewport,
                                                    clamp_camera=True)
        self._map_layer.zoom = 3  # TODO read from config
        self._main_group = pyscroll.PyscrollGroup(map_layer=self._map_layer, default_layer=4)

        self._walls = list()
        self._doors = list()
        self._stationary_objects = list()
        for object in self._tmx_data.objects:
            if object.type == 'SolidCollision':
                self._walls.append(pygame.Rect(
                    object.x, object.y,
                    object.width, object.height
                ))
            elif object.type == 'Door':
                self._doors.append(pygame.Rect(
                    object.x, object.y,
                    object.width, object.height
                ))

        self._stationary_objects.extend(self._walls)
        self._stationary_objects.extend(self._doors)

    def leave(self) -> None:
        """Leave an area"""
        pass

    def add(self, entity: Entity) -> None:
        """Add an entity to area"""
        self._main_group.add(entity)

    def remove(self, entity: Entity) -> None:
        """Remove an entity from area"""
        self._main_group.add(entity)

    def render(self, surface: Surface, camera_center: Tuple[int, int]) -> None:
        self._main_group.center(camera_center)
        self._main_group.draw(surface)

    def collide_check(self, entity_rect: Rect) -> bool:
        #return entity_rect.collidelist(self._walls + self._doors) > -1
        return entity_rect.collidelist(self._stationary_objects) > -1


class World():
    """Container for entities"""
    def __init__(self) -> None:
        self._entities: Entities = Entities.default()
        self._areas: Dict[str, Area] = {}
        self._current_area: str = ''

    @staticmethod
    def default() -> World:
        return World()

    def __str__(self) -> str:
        value = 'World\n'

        value += '\tEntities\n'
        value += '\t\t'
        value += '\n\t\t'.join(str(self._entities).splitlines())
        value += '\n'

        value += '\tAreas\n'
        for system in self._areas:
            value += '\t\t'
            value += '\n\t\t'.join(str(system).splitlines())
            value += '\n'
        
        return value

    def add_area(self, area: Area) -> None:
        """Add Area to world"""
        self._areas[area.name()] = area

    def enter_area(self, area_name: str) -> None:
        """Enter an area, setting it the focus

        TODO Need to handle this better
        TODO Move current area to resource?
        TODO Move this to a system
        """
        if self._current_area:
            self._areas[self._current_area].leave()
        if area_name in self._areas:
            self._areas[area_name].enter()
            self._current_area = area_name
        else:
            logger.error(f'Invalid area: {area_name}, valid ones {self._areas.keys()}')

    @property
    def current_area(self) -> Area:
        return self._areas[self._current_area]

    def spawn(self, component_list: List[Component]) -> Entity:
        """Create an entity with certain components"""
        entity = self._entities.alloc(component_list)
        # TODO Add entity to area
        return entity

    def despawn(self, entity: Entity) -> None:
        """Destroy an entity and all its components"""
        # TODO remove entity from area
        del self._entities[entity.id()]
        entity.clear()

    def clear(self) -> None:
        """Destroy all entities"""
        for entity in self._entities:
            # TODO remove entity from area
            entity.clear()
        self._entities = {}

    def contains(self, entity: Entity) -> bool:
        """Test if entity still exists"""
        return entity.id() in self._entities

    def has_component_type(self, entity: Entity, component_type) -> bool:
        """Returns true if the given entity has a component with the given type"""
        for component in entity.components():
            if isinstance(component, component_type):
                return True
        return False

    def query(self, query_fn) -> List[Entity]:
        """Iterates over all entities that have certain components and returns a generator"""
        return query_fn(self._entities)

    def insert(self, entity: Entity, components: List[Component]) -> None:
        """Add components to entity"""
        for component in components:
            entity.add(component)

    def remove(self, entity: Entity) -> None:
        """Remove all components from entity"""
        entity.clear()

    def remove_one(self, entity: Entity, component: Component) -> None:
        """Remove one component from entity"""
        entity.remove(component)

    def collide_check(self, entity_rect: Rect) -> bool:
        """Checks if entity collides with world"""
        return self._areas[self._current_area].collide_check(entity_rect)

class WorldBuilder():
    """Modifies the world using a builder pattern

    TODO determine if I want to use this"""
    def __init__(self) -> None:
        pass


class Stage():
    """Stage holder"""
    def __init__(self, name: str) -> None:
        self._name = name
        self._systems : List[System] = []
        self._executor : Executor = Executor.default()

    def __str__(self) -> str:
        value = f'{self._name}\n'
        for system in self._systems:
            value += '\t'
            value += '\n\t'.join(str(system).splitlines())
            value += '\n'
        return value

    def name(self) -> str:
        return self._name

    def add_system(self, system: System) -> None:
        self._systems.append(system)
        # TODO add to uninitialized list

    def add_system_to_front(self, system: System) -> None:
        self._systems.insert(0, system)
        # TODO add to uninitialized list

    def initialize(self, world: World, resources: Resources) -> None:
        for system in self._systems:
            system.initialize(world, resources)

    def run(self, world: World, resources: Resources) -> None:
        # TODO pass in list of stages to execute on, for now use all
        self._executor.execute_stage(self._systems, world, resources)


class Schedule():
    """An ordered collection of stages, which each contain
    an ordered list of Systems. It is an execution plan for
    an application. The are run on a given World and Resources
    """
    def __init__(self) -> None:
        self._stages: Dict[str, Stage] = {}
        self._stage_order: List[str] = []
        self._name: str = 'Schedule'

    def __str__(self):
        value = f'{self._name}:\n'
        for _, stage in self._stages.items():
            value += '\t'
            value += '\n\t'.join(str(stage).splitlines())
            value += '\n'
        return value

    @staticmethod
    def default() -> Schedule:
        return Schedule()

    def name(self) -> str:
        return self._name

    def set_name(self, name: str) -> Schedule:
        self._name = name + '_Schedule'
        return self

    def add_stage(self, stage_name: str) -> Schedule:
        """Add new stage to end of the list of stages"""
        if stage_name in self._stage_order:
            raise Exception(f'Stage already exists {stage_name}')
        else:
            self._stages[stage_name] = Stage(stage_name)
            self._stage_order.append(stage_name)
        return self

    def add_stage_before(self, stage_name: str, target_name: str) -> Schedule:
        """Add new stage in the list of the stages before target stage"""
        if stage_name in self._stage_order:
            raise Exception(f'Stage already exists {stage_name}')
        else:
            target_index = self._stage_order.index(target_name)
            self._stages[stage_name] = Stage(stage_name)
            self._stage_order.insert(target_index, stage_name)
        return self

    def add_stage_after(self, stage_name: str, target_name: str) -> Schedule:
        """Add new stage in the list of the stages after target stage"""
        if stage_name not in self._stage_order:
            raise Exception(f'Stage already exists {stage_name}')
        else:
            target_index = self._stage_order.index(target_name)
            self._stages[stage_name] = Stage(stage_name)
            self._stage_order.insert(target_index + 1, stage_name)
        return self

    def add_system_to_stage(self, stage_name: str, system: System) -> Schedule:
        """Add system to specified stage's list of systems"""
        if stage_name not in self._stage_order:
            raise Exception(f'Stage does not exists {stage_name}')
        else:
            self._stages[stage_name].add_system(system)
        return self

    def add_system_to_stage_front(self, stage_name: str, system: System) -> Schedule:
        """Add system to front of specified stage's list of systems"""
        if stage_name not in self._stage_order:
            raise Exception(f'Stage does not exists {stage_name}')
        else:
            self._stages[stage_name].add_system_to_front(system)
        return self

    def initialize(self, world: World, resources: Resources) -> Schedule:
        """Initialize all systems in stage order, called once per update"""
        for stage_name in self._stage_order:
            self._stages[stage_name].initialize(world, resources)
        return self

    def run_once(self, world: World, resources: Resources) -> None:
        """Iterate over the stages in order and run systems contained within"""
        for stage_name in self._stage_order:
            self._stages[stage_name].run(world, resources)

    def initialize_and_run(self, world: World, resources: Resources) -> None:
        self.initialize(world, resources)
        self.run_once(world, resources)


class Executor():
    """Executes each schedule stage."""
    def __init__(self) -> None:
        pass

    @staticmethod
    def default() -> Executor:
        return Executor()

    def initialize(self, resources: Resources) -> None:
        pass

    def execute_stage(self, systems: List[System], world: World, resources: Resources) -> None:
        for system in systems:
            system.update(world, resources)
            system.run_once(world, resources)


class Plugin(ABC):
    """Plugins use AppBuilder to configure an App. When an App
    registers a plugin, the plugin's build function is run."""
    def __init__(self, name: str) -> None:
        self._name = name

    def __str__(self) -> str:
        return f'{self._name}'

    def name(self) -> str:
        """Returns name of plugin"""
        return self._name

    @abstractmethod
    def build(self, app: AppBuilder):
        pass


def _run_once(app: App) -> None:
    app.update()


class App():
    def __init__(self,
                 world: World,
                 resources: Resources,
                 runner,
                 schedule: Schedule,
                 startup_schedule: Schedule) -> None:
        self._world = world
        self._resources = resources
        self._runner = runner
        self._schedule = schedule
        self._startup_schedule = startup_schedule

    def __str__(self) -> str:
        return '\n'.join([str(self._world),
                          str(self._startup_schedule),
                          str(self._schedule),
                          str(self._resources)])

    @staticmethod
    def default() -> App:
        """Returns a default App"""
        return App(
            world=World.default(),
            resources=Resources(),  # .default(),
            schedule=Schedule.default(),
            startup_schedule=Schedule.default().set_name('Startup'),
            runner=_run_once
        )

    @staticmethod
    def build() -> AppBuilder:
        """Returns an AppBuilder"""
        return AppBuilder.default()

    @property
    def resources(self) -> Resources:
        return self._resources

    def update(self) -> None:
        self._schedule.initialize_and_run(self._world, self._resources)

    def initialize(self) -> None:
        logger.info('Initialize Application')
        self._startup_schedule.initialize_and_run(self._world, self._resources)

    def run(self) -> None:
        self._runner(self)


class AppBuilder():
    """Configure application using builder pattern"""
    def __init__(self, app: App) -> None:
        self._app = app

    def __str__(self) -> str:
        return str(self._app)

    @staticmethod
    def default() -> AppBuilder:
        app_builder = AppBuilder(App.default())
        app_builder.add_default_stages()
        # app_builder.add_event(AppExit)  # TODO Figure this out
        return app_builder

    def run(self) -> AppBuilder:
        """Start running the application"""
        self._app.initialize()
        self._app.run()
        return self

    def set_world(self, world: World) -> AppBuilder:
        """Set the world"""
        self._app._world = world
        return self

    def add_area(self, area: Area) -> AppBuilder:
        """Add an area to the world"""
        self._app._world.add_area(area)
        return self

    def clear(self) -> AppBuilder:
        """Reset builder TODO (empty) returns default version of the app"""
        self._app.clear()
        return AppBuilder(App.default())

    def resources(self) -> Resources:
        """Return resources in builder"""
        return self._app._resources

    def add_stage(self, stage_name: str) -> AppBuilder:
        """Add stage"""
        self._app._schedule.add_stage(stage_name)
        return self

    def add_stage_after(self, target: str, stage_name: str) -> AppBuilder:
        """Add stage after target stage"""
        self._app._schedule.add_stage_after(target, stage_name)
        return self

    def add_stage_before(self, target: str, stage_name: str) -> AppBuilder:
        """Add stage before target stage"""
        self._app._schedule.add_stage_before(target, stage_name)
        return self

    def add_startup_stage(self, stage_name: str) -> AppBuilder:
        """Add startup stage"""
        self._app._startup_schedule.add_stage(stage_name)
        return self

    def add_startup_stage_before(self, target: str, stage_name: str) -> AppBuilder:
        """Add startup stage before target stage"""
        self._app._startup_schedule.add_stage_before(target, stage_name)
        return self

    def add_startup_stage_after(self, target: str, stage_name: str) -> AppBuilder:
        """Add startup stage after target stage"""
        self._app._startup_schedule.add_stage_after(target, stage_name)
        return self

    def add_system(self, system: System) -> AppBuilder:
        """Add system to default stage"""
        self.add_system_to_stage(ECS.STAGE_UPDATE, system)
        return self

    def init_system(self, system_builder_fn) -> AppBuilder:
        """Add init system and TODO what then?"""
        self.init_system_to_stage(ECS.STAGE_UPDATE, system_builder_fn)
        return self

    def init_system_to_stage(self, stage_name: str, system_builder_fn) -> AppBuilder:
        """Init system and add to stage"""
        system = system_builder_fn(self._app._resources)
        self.add_system_to_stage(stage_name, system)
        return self

    def add_startup_system_to_stage(self, stage_name: str, system: System) -> AppBuilder:
        """Add system to stage"""
        self._app._startup_schedule.add_system_to_stage(stage_name, system)
        return self

    def add_startup_system(self, system: System) -> AppBuilder:
        """Add system to default stage"""
        self.add_startup_system_to_stage(
            ECS.STARTUP_STAGE_STARTUP, system)
        return self

    def init_startup_system(self, system_builder_fn) -> AppBuilder:
        """Add startup system and TODO what then?"""
        self.init_startup_system_to_stage(
            ECS.STARTUP_STAGE_STARTUP, system_builder_fn)
        return self

    def init_startup_system_to_stage(self, stage_name: str, system_builder_fn) -> AppBuilder:
        """Init startup system and add to stage"""
        system = system_builder_fn(self._app._resources)
        self.add_startup_system_to_stage(stage_name, system)
        return self

    def add_default_stages(self) -> AppBuilder:
        """Add default stages"""
        (self.add_startup_stage(ECS.STARTUP_STAGE_PRE_STARTUP)  # TODO figure out how to run once only
             .add_startup_stage(ECS.STARTUP_STAGE_STARTUP)  # TODO figure out how to run once only
             .add_startup_stage(ECS.STARTUP_STAGE_POST_STARTUP)  # TODO figure out how to run once only
             .add_stage(ECS.STAGE_FIRST)
             .add_stage(ECS.STAGE_PRE_EVENT)
             .add_stage(ECS.STAGE_EVENT)
             .add_stage(ECS.STAGE_PRE_UPDATE)
             .add_stage(ECS.STAGE_UPDATE)
             .add_stage(ECS.STAGE_POST_UPDATE)
             .add_stage(ECS.STAGE_LAST))
        return self

    def add_system_to_stage(self, stage_name: str, system: System) -> AppBuilder:
        """Add system to stage"""
        self._app._schedule.add_system_to_stage(stage_name, system)
        return self

    def add_system_to_stage_front(self, stage_name: str, system: System) -> AppBuilder:
        """Add system to front of stage"""
        self._app._schedule.add_system_to_stage_front(stage_name, system)
        return self

    """TODO
    def add_event(self, ????) -> AppBuilder:
        return self
    """

    def add_resource(self, key: str, value) -> AppBuilder:
        """Add resource"""
        # self._app._resources.insert(key, value)
        self._app._resources[key] = value
        return self

    def init_resource(self) -> AppBuilder:
        """TODO figure this out"""
        return self

    def set_runner(self, runner) -> AppBuilder:
        """Set the application runner"""
        self._app._runner = runner
        return self

    def add_plugin(self, plugin: Plugin) -> AppBuilder:
        """Add plugin"""
        plugin.build(self)
        return self
