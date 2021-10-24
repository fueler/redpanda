from pygame.math import Vector3
from redpanda.ecs.core import Resources, System, World
from redpanda.ecs.core import ContainsComponentsQuery
from redpanda.ecs.pygame_plugin import ResourceTypes


class EntityMovement(System):
    def __init__(self) -> None:
        super().__init__('PlayerMovement')

    def run_once(self, world: World, resources: Resources) -> None:
        # Use resources for controller to apply to velocity
        # Update position with current velocity
        # Consider acceleration
        entities = world.query(ContainsComponentsQuery('velocity',
                                                       'speed',
                                                       'location',
                                                       'movement'))
        for entity in entities:
            # old_velocity = entity.components['velocity']
            entity.components['velocity'] = entity.components['speed']
            time_elapsed_seconds = resources[ResourceTypes.GAME_TIME_ELAPSED] / 1000
            location = entity.components['location']
            velocity = entity.components['velocity']
            movement = entity.components['movement']

            delta = movement.value * (velocity.value * Vector3(time_elapsed_seconds))
            location.position += delta
            if world.collide_check(entity.feet):
                location.position -= delta
