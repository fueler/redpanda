import random
from pygame.math import Vector3
from redpanda.ecs.core import Resources, System, World
from redpanda.ecs.core import ContainsComponentsQuery
from redpanda.ecs.pygame_plugin import ResourceTypes
from redpanda.ecs.types import Direction


class PlayerInput(System):
    """2D player input, could be extended to 3D
    TODO: Figure how to handle 2D versus 3D
    TODO: Have config for type of movement, one direction at a time or multiple
    """
    def __init__(self) -> None:
        super().__init__('PlayerInput')
        self._type = 'fluid'  # vs 'priority # TODO make this configurable

    def run_once(self, world: World, resources: Resources) -> None:
        # Find all entities with controller, direction, and movement
        entities = world.query(ContainsComponentsQuery('controller',
                                                       'direction',
                                                       'movement'))
        for entity in entities:
            controller_index = entity.components['controller'].index
            controller_name = ResourceTypes.CONTROLLER_PREFIX + str(controller_index)
            controller = resources[controller_name]
            if self._type == 'priority':
                # NOTE: Current priority up > down > left > right
                if controller.up:
                    entity.components['direction'].value = Direction.up
                    entity.components['movement'].value = Vector3(0, -1, 0)
                elif controller.down:
                    entity.components['direction'].value = Direction.down
                    entity.components['movement'].value = Vector3(0, 1, 0)
                elif controller.left:
                    entity.components['direction'].value = Direction.left
                    entity.components['movement'].value = Vector3(-1, 0, 0)
                elif controller.right:
                    entity.components['direction'].value = Direction.right
                    entity.components['movement'].value = Vector3(1, 0, 0)
                else:
                    entity.components['movement'].value = Vector3(0, 0, 0)
            elif self._type == 'fluid':
                # Determine movement first
                movement = Vector3(0, 0, 0)
                if controller.up:
                    movement += Vector3(0, -1, 0)
                if controller.down:
                    movement += Vector3(0, 1, 0)
                if controller.left:
                    movement += Vector3(-1, 0, 0)
                if controller.right:
                    movement += Vector3(1, 0, 0)

                entity.components['movement'].value = movement

                # Determine direction second
                movement = movement.normalize() if movement.length() != 0 else movement
                if movement.x > movement.y:
                    entity.components['direction'].value = Direction.up
                elif movement.x < movement.y:
                    entity.components['direction'].value = Direction.down
                elif movement.y < 0:
                    entity.components['direction'].value = Direction.left
                else:
                    entity.components['direction'].value = Direction.right


class RandomInput(System):
    def __init__(self) -> None:
        super().__init__('RandomInput')
        self._timer: float = 0
        self._timeout: float 

    def run_once(self, world: World, resources: Resources) -> None:
        entities = world.query(ContainsComponentsQuery('random_direction_timer',
                                                       'direction',
                                                       'movement'))
        for entity in entities:
            # TODO read the type of random input????
            direction_timer = resources[ResourceTypes.SYS_TIMERS].timer(entity.components['random_direction_timer'].id)
            if direction_timer.expired:
                direction_timer.queue_reset = True
                new_direction = random.choice(list(Direction))
                entity.components['direction'].value = new_direction
                if new_direction == Direction.up:
                    entity.components['movement'].value = Vector3(0, -1, 0)
                elif new_direction == Direction.down:
                    entity.components['movement'].value = Vector3(0, 1, 0)
                elif new_direction == Direction.left:
                    entity.components['movement'].value = Vector3(-1, 0, 0)
                elif new_direction == Direction.right:
                    entity.components['movement'].value = Vector3(1, 0, 0)
