from redpanda.ecs.core import Resources, System, World
from redpanda.ecs.core import ContainsComponentsQuery
from redpanda.ecs.pygame_plugin import ResourceTypes


class SpriteAnimation(System):
    def __init__(self) -> None:
        super().__init__('Animation')

    def run_once(self, world: World, resources: Resources) -> None:
        entities = world.query(ContainsComponentsQuery('animation',
                                                       'sprite',
                                                       'direction',
                                                       'movement'))  # TODO Should I really require movement component to animate?
        time_elapsed = resources[ResourceTypes.GAME_TIME_ELAPSED]
        for entity in entities:
            animation = entity.components['animation']
            sprite = entity.components['sprite'].sprite
            direction = entity.components['direction'].value
            movement = entity.components['movement'].value
            # TODO determine state based on other components, for now leave it as idle
            frames = sprite.animation_set(animation.action).direction(direction).frames
            if movement.length() > 0:
                animation.timer += time_elapsed
                timeout = 200  # TODO get timeout from animation
                if animation.timer > timeout:
                    animation.timer -= timeout
                    animation.counter = (animation.counter + 1) % len(frames)
                animation.counter = animation.counter % len(frames)  # TODO instead when direction changes counter should reset
            else:
                animation.counter = 0  # Reset back to standing ASSUMPTION
