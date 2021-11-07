from redpanda.ecs.core import Resources, System, World
from redpanda.ecs.pygame_plugin import ResourceTypes
import pygame
import pytmx
import pyscroll
import redpanda.logging
from redpanda.ecs.types import PyScrollMap


logger = redpanda.logging.get_logger('ecs.system.AreaLoader')


# TODO should this belong in redpanda.ecs.systems or in a higher layer's system?

class AreaLoader(System):
    """Loads areas queued"""
    def __init__(self) -> None:
        super().__init__('AreaLoader')

    def initialize(self, world: World, resources: Resources) -> None:
        resources['area_loader_list'] = list()
        logger.info('Initialized')

    def run_once(self, world: World, resources: Resources) -> None:
        # I need the area
        # I need the resource for area loading queue
        # Add to area walls
        # Add to world entities
        # Add to area entities
        for area_name in resources['area_loader_list']:
            # something to do
            area = world.find_area(area_name)
            # TODO Move this to a system so that it can access resources
            # viewport = (resources[ResourceTypes.SYS_RESOLUTION]['width'],
            #             resources[ResourceTypes.SYS_RESOLUTION]['height'])
            viewport = (640, 480)  # TODO read from resources

            tmx_data = pytmx.util_pygame.load_pygame(area.map_filename)
            map_data = pyscroll.data.TiledMapData(tmx_data)
            map_layer = pyscroll.BufferedRenderer(map_data,
                                                  viewport,
                                                  clamp_camera=True)
            map_layer.zoom = 3  # TODO read from config
            main_group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=4)

            walls = list()
            doors = list()
            stationary_collision_list = list()
            #area_entities = list()
            for object in tmx_data.objects:
                if object.type == 'SolidCollision':
                    walls.append(
                        pygame.Rect(
                            object.x, object.y,
                            object.width, object.height
                        )
                    )
                elif object.type == 'Door':
                    logger.info(f'door: {str(object)}')
                    doors.append(
                        pygame.Rect(
                            object.x, object.y,
                            object.width, object.height
                        )
                    )
                    #entity = Entity()
                    #self._area_entities.append(
                        
                    #)

            stationary_collision_list.extend(walls)
            stationary_collision_list.extend(doors)
            
            map = PyScrollMap(tmx_data, map_data, map_layer, main_group, stationary_collision_list)

            area.map = map

        resources['area_loader_list'].clear()
