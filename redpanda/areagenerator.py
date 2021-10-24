import os
from redpanda.ecs.core import Resources
from redpanda.ecs.core import Area
from redpanda.ecs.pygame_plugin import ResourceTypes


def generate_areas_from_world_template(resources: Resources):
    template = resources['asset_registry'].world()
    for _, area_template in template.areas.items():
        yield Area(area_template.name, 
                   os.path.join(resources[ResourceTypes.GAME_DIRECTORIES]['assets.maps'],
                                area_template.filename))
