from redpanda.spriteloader import load_sprite
from redpanda.ecs.core import Component, Resources
import redpanda.ecs.components as Components
from typing import List
from pygame import Vector3


def create_components_from_entity_template(name: str, resources: Resources) -> List[Component]:
    template = resources['entity_templates'].template(name)
    spritesheet = resources['asset_registry'].spritesheet(template.spritesheet)
    sprite = load_sprite(spritesheet, template.width, template.height)
    return [
        Components.DirectionComponent(),
        Components.LocationComponent('area1',
                                     Vector3(24, 24, 0)), # TODO Fix me
                                     #Vector3(1024.0, 1024.0, 0.0)),  # TODO fix me
        Components.SpriteComponent(sprite),
    ]
