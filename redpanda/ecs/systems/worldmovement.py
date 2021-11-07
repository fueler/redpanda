from redpanda.ecs.core import Resources, System, World
from redpanda.ecs.pygame_plugin import ResourceTypes
from redpanda.ecs.types import WorldMovementEvent
import redpanda.logging


logger = redpanda.logging.get_logger('ecs.system.WorldMovement')


# TODO should this belong in redpanda.ecs.systems or in a higher layer's system?

class WorldMovement(System):
    """Loads areas queued"""
    def __init__(self) -> None:
        super().__init__('WorldMovement')

    def initialize(self, world: World, resources: Resources) -> None:
        resources['world_movement_list'] = list()
        logger.info('Initialized')

    def run_once(self, world: World, resources: Resources) -> None:
        events = resources['world_movement_list']
        for event in events:
            resources['area_loader_list'].append(event.area)
            world.enter_area(event.area)
        resources['world_movement_list'].clear()
