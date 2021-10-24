from redpanda.ecs.core import Resources, System, World
from redpanda.ecs.core import ContainsComponentsQuery
from redpanda.ecs.pygame_plugin import ResourceTypes


class SoundEffects(System):
    """For now combine determining if playing a sound and actually playing a sound"""
    def __init__(self) -> None:
        super().__init__('SoundEffects')

    def run_once(self, world: World, resources: Resources) -> None:
        time_elapsed = resources[ResourceTypes.GAME_TIME_ELAPSED]
        entities = world.query(ContainsComponentsQuery('sound_effects'))
        for entity in entities:
            sound_effects = entity.components['sound_effects'].sound_effects
            for _, sound_effect in sound_effects.items():
                sound_effect.timer.timer += time_elapsed
                from redpanda.ecs.triggers import triggers as Triggers
                # TODO make more pythonic
                triggered = True
                for trigger in sound_effect.triggers:
                    triggered = triggered and Triggers[trigger](entity, sound_effect.timer)
                if triggered:
                    # play sound
                    # TODO just queue it here and have this handled by Sound system so
                    #      priority of sounds can be used in case there are too many
                    # TODO I shouldn't have to set sound volume every time???
                    resources['asset_registry'].sound(sound_effect.sound).sound.set_volume(sound_effect.volume)
                    resources['asset_registry'].sound(sound_effect.sound).sound.play()

